from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, current_user
from dotenv import dotenv_values
from peewee import DoesNotExist

from flaskr import db
from flaskr.auth import check_password, LoginCredential, SignupCredential, hash_password, create_user, require_admin
from flaskr.db import db_handle, User, Role, Material
from flaskr.forms import SignupForm
from flaskr.util import _ensure_default_materials, _normalize_material_id

# .env File
config = dotenv_values(".env")

# Flask App Configuration
app = Flask(__name__)
app.secret_key = config["SECRET_KEY"]

# File Upload Handling
ALLOWED_UPLOAD_EXTENSIONS = {'.nc', '.gcode', '.txt'}

def allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_UPLOAD_EXTENSIONS

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)

# Database
db_handle.init(config["DATABASE_PATH"])
db_handle.connect()
db_handle.create_tables([db.Role, db.User, Material])
db_handle.close()


## Database Connection Handlers

@app.before_request
def _db_connect():
    db_handle.connect()


@app.teardown_request
def _db_close(exc):
    if not db_handle.is_closed():
        db_handle.close()


# User Loader

@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    try:
        return User.get(User.username == user_id)
    except DoesNotExist:
        return None


# Routes

@app.route('/')
def root():
    return redirect(url_for('machine_state'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('machine_state'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        json: dict = request.get_json()
        credential = LoginCredential(json["username"], json["password"])
        status, user = check_password(credential)

        if status:
            if login_user(user):
                return {
                    "info": "test-info",
                    "success": True,
                    "redirect": "/setup",
                    "message": "Login successful"
                }
            else:
                return {
                    "info": "test-info",
                    "success": False,
                    "redirect": "/login",
                    "message": "Error logging in"
                }
        else:
            return {
                "info": "test-info",
                "success": False,
                "redirect": "/setup",
                "message": "Could not log in user"
            }
    else:
        return {
            "info": "test-info",
            "success": False,
            "redirect": "/login",
            "message": "Invalid HTTP method"
        }


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm()

    if request.method == "GET":
        return render_template("signup.html", form=signup_form)
    elif request.method == "POST" and signup_form.validate_on_submit():
        if create_user(SignupCredential(
                name=signup_form.name.data,
                username=signup_form.username.data,
                hashed_password=hash_password(signup_form.password.data)
        )):
            return redirect(url_for("login"))
        else:
            return f'<h1>Did not create user!</h1>'
    else:
        return f'<h1>Unknown method</h1>'


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    _ensure_default_materials()
    materials = list(Material.select().dicts())
    is_admin = False
    if current_user.is_authenticated:
        is_admin = getattr(current_user, 'role_id', None) == 1
    return render_template("setup.html", materials=materials, is_admin=is_admin)


@app.route('/machine_state', methods=['GET', 'POST'])
def machine_state():
    if request.method == 'GET':
        return render_template("machine_state.html")
    else:
        return '<h1>Method POST not available for route "machine_state".', 405


@app.route('/manage_users')
def manage_users():
    if not require_admin(current_user):
        return redirect(url_for('login'))
    return render_template('manage_users.html')


# API Routes

@app.route('/api/materials', methods=['GET'])
def api_get_materials():
    materials = list(Material.select().dicts())
    return jsonify(success=True, materials=materials)

@app.route('/api/materials', methods=['POST'])
def api_add_material():
    if not require_admin(current_user):
        return jsonify(success=False, message='Forbidden'), 403

    data = request.get_json(silent=True) or {}
    name = str(data.get('name', '')).strip()
    desc = str(data.get('desc', '')).strip()
    thickness = str(data.get('thickness', '')).strip()
    z_offset = str(data.get('z_offset', '')).strip()

    if not name or not desc or not thickness or not z_offset:
        return jsonify(success=False, message='Missing required fields'), 400

    material_id = _normalize_material_id(name)
    material = Material.create(
        id=material_id,
        name=name,
        desc=desc,
        thickness=thickness,
        z_offset=z_offset
    )

    return jsonify(success=True, material={
        'id': material.id,
        'name': material.name,
        'desc': material.desc,
        'thickness': material.thickness,
        'z_offset': material.z_offset
    })


@app.route('/api/materials/<material_id>', methods=['DELETE'])
def api_delete_material(material_id):
    if not require_admin(current_user):
        return jsonify(success=False, message='Forbidden'), 403

    try:
        material = Material.get(Material.id == material_id)
        material.delete_instance()
        return jsonify(success=True)
    except Material.DoesNotExist:
        return jsonify(success=False, message='Material not found'), 404


@app.route('/api/upload_file', methods=['POST'])
def api_upload_file():
    if 'file' not in request.files:
        return jsonify(success=False, message='No file part'), 400
    file = request.files['file']
    if file.filename is not None:
        if file.filename == '':
            return jsonify(success=False, message='No selected file'), 400
        elif not allowed_file(file.filename):
            return jsonify(success=False, message='File type not allowed'), 400

    upload_dir = os.path.join(app.instance_path, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(file.filename)
    save_path = os.path.join(upload_dir, filename)
    try:
        file.save(save_path)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    return jsonify(success=True, message='Uploaded', path=save_path)


@app.route('/api/estop', methods=['POST'])
def api_estop():
    payload = request.get_json(silent=True) or {}
    source = payload.get('source', 'unknown')
    app.logger.info('E-stop request received from %s', source)
    # TODO: wire this into the machine control hardware or API.
    return jsonify(success=True, message='E-stop request received', source=source)


@app.route('/api/users', methods=['GET'])
def api_get_users():
    if not require_admin(current_user):
        return jsonify(success=False, message='Forbidden'), 403
    users = []
    for u in User.select():
        users.append({
            'username': u.username,
            'name': u.name,
            'role_id': getattr(u, 'role_id', None)
        })
    return jsonify(success=True, users=users)


@app.route('/api/users/<username>/role', methods=['POST'])
def api_change_role(username):
    if not require_admin(current_user):
        return jsonify(success=False, message='Forbidden'), 403
    data = request.get_json() or {}
    role_id = int(data.get('role_id', 0))
    try:
        role_obj = Role.get(Role.id == role_id)
    except Role.DoesNotExist:
        return jsonify(success=False, message='Role not found'), 400
    try:
        u = User.get(User.username == username)
        u.role = role_obj
        u.save()
        return jsonify(success=True)
    except User.DoesNotExist:
        return jsonify(success=False, message='User not found'), 404


@app.route('/api/users/<username>', methods=['DELETE'])
def api_delete_user(username):
    if not require_admin(current_user):
        return jsonify(success=False, message='Forbidden'), 403
    if current_user.is_authenticated and current_user.username == username:
        return jsonify(success=False, message='Cannot delete yourself'), 400
    try:
        u = User.get(User.username == username)
        u.delete_instance()
        return jsonify(success=True)
    except User.DoesNotExist:
        return jsonify(success=False, message='User not found'), 404

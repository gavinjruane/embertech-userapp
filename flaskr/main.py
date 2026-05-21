from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from dotenv import dotenv_values
from peewee import DoesNotExist

from flaskr import db
from flaskr.auth import check_password, LoginCredential, SignupCredential, hash_password, create_user
from flaskr.db import db_handle, User, Role
from flaskr.forms import LoginForm, SignupForm

# .env File
config = dotenv_values(".env")

# Flask App Configuration
app = Flask(__name__)
app.secret_key = config["SECRET_KEY"]

# Upload config
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
db_handle.create_tables([db.Role, db.User])
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
def hello_world():
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
        print(json)
        credential = LoginCredential(json["username"], json["password"])
        status, user = check_password(credential)
        print("user is:", user, type(user))
        if status:
            if login_user(user):
                print("Success!")
                return {
                    "info": "test-info",
                    "success": True,
                    "redirect": "/setup",
                    "message": "Login successful"
                }
            else:
                print("Failed to login!")
                return {
                    "info": "test-info",
                    "success": False,
                    "redirect": "/login",
                    "message": "Error logging in"
                }
        else:
            print("Fail!")
            return { "info": "test-info" , 
                         "success": False,
                         "redirect": "/setup",
                         "message": "Error Logging In!"
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
    materials = [
        {
            'id': 'fabric-a',
            'name': 'Fabric A',
            'desc': 'Standard woven polyester blend. Mid-weight, low stretch. Suitable for general cutting operations.',
            'thickness': '1.2',
            'z_offset': '-0.50'
        },
        {
            'id': 'fabric-b',
            'name': 'Fabric B',
            'desc': 'Heavy-duty canvas. Dense weave, rigid structure. Requires slower feed rate and higher Z clearance.',
            'thickness': '2.8',
            'z_offset': '-1.20'
        },
        {
            'id': 'fabric-c',
            'name': 'Fabric C',
            'desc': 'Lightweight chiffon / silk blend. Delicate; use vacuum hold-down. Minimal Z pressure recommended.',
            'thickness': '0.4',
            'z_offset': '-0.15'
        }
    ]
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
    

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify(success=False, message='No file part'), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(success=False, message='No selected file'), 400
    if not allowed_file(file.filename):
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


def _require_admin():
    if not current_user.is_authenticated or getattr(current_user, 'role_id', None) != 1:
        return False
    return True


@app.route('/manage_users')
def manage_users():
    if not _require_admin():
        return redirect(url_for('login'))
    return render_template('manage_users.html')


@app.route('/api/users', methods=['GET'])
def api_get_users():
    if not _require_admin():
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
    if not _require_admin():
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
    if not _require_admin():
        return jsonify(success=False, message='Forbidden'), 403
    if current_user.is_authenticated and current_user.username == username:
        return jsonify(success=False, message='Cannot delete yourself'), 400
    try:
        u = User.get(User.username == username)
        u.delete_instance()
        return jsonify(success=True)
    except User.DoesNotExist:
        return jsonify(success=False, message='User not found'), 404


    




from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user
from dotenv import dotenv_values
from peewee import DoesNotExist

from flaskr import db
from flaskr.auth import check_password, Credential
from flaskr.db import db_handle, User
from flaskr.forms import LoginForm

# .env File
config = dotenv_values("./flaskr/.env")

# Flask App Configuration
app = Flask(__name__)
app.secret_key = config["SECRET_KEY"]

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
    preston = db.User.get(db.User.name == "Preston Kearnan")

    return f'<h1>Hello World! Embertech Automation with {preston.name}</h1>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    credential = Credential("", "")

    if request.method == "GET":
        return render_template("login.html", form=login_form)
    elif request.method == "POST" and login_form.validate_on_submit():
        login_form.populate_obj(credential)
        if check_password(credential):
            return f'<h1>Success!</h1>'
        else:
            return f'<h1>NOT a success!</h1>'
    else:
        return f'<h1>Unknown method</h1>'
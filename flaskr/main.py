from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required
from dotenv import dotenv_values
from peewee import DoesNotExist

from flaskr import db
from flaskr.auth import check_password, LoginCredential, SignupCredential, hash_password, create_user
from flaskr.db import db_handle, User
from flaskr.forms import LoginForm, SignupForm

# .env File
config = dotenv_values(".env")

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
    return f'<h1>Hello World! Embertech Automation</h1>'


@app.route('/login', methods=['GET', 'POST'])
def login():
    # login_form = LoginForm()
    # credential = LoginCredential("", "")

    # if request.method == "GET":
    #     return render_template("login.html", form=login_form)
    # elif request.method == "POST" and login_form.validate_on_submit():
    #     login_form.populate_obj(credential)
    #     status, user = check_password(credential)
    #     if status:
    #         login_user(user)
    #         return f'<h1>Success!</h1>'
    #     else:
    #         return f'<h1>NOT a success!</h1>'
    # else:
    #     return f'<h1>Unknown method</h1>'
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
                return { "info": "test-info" , 
                         "success": True,
                         "redirect": "/setup",
                         "message": "Error Logging In!"
                         }
            else:
                print("Failed to login!")
                return { "info": "test-info" , 
                         "success": False,
                         "redirect": "/setup",
                         "message": "Error Logging In!"
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
@login_required
def setup():
    if request.method == 'GET':
        return render_template("setup.html")

        
@app.route('/machine_state', methods=['GET', 'POST'])
def machine_state():
    if request.method == 'GET':
        return render_template("machine_state.html")
        


    

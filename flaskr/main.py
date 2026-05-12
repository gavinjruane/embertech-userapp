from flask import Flask
from flask_login import LoginManager
from dotenv import dotenv_values

from flaskr import db
from flaskr.db import db_handle

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

# Routes

@app.route('/')
def hello_world():
    preston = db.User.get(db.User.name == "Preston Kearnan")

    return f'<h1>Hello World! Embertech Automation with {preston.name}</h1>'
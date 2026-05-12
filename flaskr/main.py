from flask import Flask
from flask_login import LoginManager
from dotenv import dotenv_values

# .env File
config = dotenv_values("./flaskr/.env")

# Flask App Configuration
app = Flask(__name__)
app.secret_key = config["SECRET_KEY"]

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def hello_world():
    return '<h1>Hello World! Embertech Automation</h1>'
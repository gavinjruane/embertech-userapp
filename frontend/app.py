from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def machine_state():
    return render_template("machine_state.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/setup")
def setup():
    return render_template("setup.html")


if __name__ == "__main__":
    app.run(debug=True)
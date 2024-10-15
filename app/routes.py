from flask import render_template
from app import app

user = {"username": "Andrew"}

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", user=user)

@app.route("/about")
def about():
    return render_template("about.html", user=user)

@app.route("/contact")
def contact():
    return render_template("contact.html", user=user)
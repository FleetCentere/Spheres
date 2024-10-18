from flask import render_template
from app import app

user = {"username": "Andrew"}
posts = [
    {
        "author": {"username": "Steve"},
        "body": "This is a post from Steve"
    },
    {
        "author": {"username": "Hampus"},
        "body": "I am a defenseman!"
    }
]

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", user=user, posts=posts)

@app.route("/about")
def about():
    return render_template("about.html", user=user)

@app.route("/contact")
def contact():
    return render_template("contact.html", user=user)
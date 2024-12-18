from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, TaskForm, WorkoutForm, PersonForm, ContentForm, EventForm, TagForm
from app.models import User, Post, Task, WorkoutActivity, Person, Event, Content
import sqlalchemy as sa
from datetime import datetime, timezone

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()
    posts = db.session.scalars(current_user.following_posts()).all()
    if form.validate_on_submit():
        post = Post(body=form.body.data, title=form.title.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been submitted")
        return redirect(url_for("index"))
    return render_template("index.html", form=form, posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(url_for("index"))
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user")
        return redirect(url_for("index"))
    return render_template("register.html", form=form)

@app.route("/user/<username>")
@login_required
def user(username):
    form = EmptyForm()
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {"author": user, "body": "Test post #1"},
        {"author": user, "body": "This is yet another test post"}
    ]
    return render_template("user.html", user=user, posts=posts, form=form)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)

def get_user_or_flash(username):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user is None:
        flash(f"User {username} not found")
        return None
    if user == current_user:
        flash("You cannot perform this action on yourself!")
        return None
    return user

@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = get_user_or_flash(username)
        if user:
            current_user.follow(user)
            db.session.commit()
            flash(f"You are now following {username}")
        return redirect(url_for("user", username=username))
    return redirect(url_for("index"))

@app.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = get_user_or_flash(username)
        if user:
            current_user.unfollow(user)
            db.session.commit()
            flash(f"You are no longer following {username}")
        return redirect(url_for("user", username=username))
    return redirect(url_for("index"))

@app.route("/explore")
@login_required
def explore():
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.session.scalars(query).all()
    query = sa.select(User)
    people = db.session.scalars(query).all()
    return render_template("index.html", title="Explore", posts=posts, people=people)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/homepage")
@login_required
def homepage():
    taskform = TaskForm()
    postform = PostForm()
    workoutform = WorkoutForm()
    personform = PersonForm()
    contentform = ContentForm()
    eventform = EventForm()
    # getting tasks
    query = db.session.query(Task).filter(Task.user_id == current_user.id, Task.deleted == False).order_by(sa.desc(Task.timestamp)) 
    tasks = query.all()
    # getting posts
    query = db.session.query(Post).filter(Post.user_id == current_user.id).order_by(sa.desc(Post.timestamp))
    posts = query.all()
    # getting people
    query = db.session.query(Person).filter(Person.user_id == current_user.id)
    people = query.all()
    # getting events
    query = db.session.query(Event).filter(Event.user_id == current_user.id).order_by(sa.desc(Event.day))
    events = query.all()
    # getting content
    query = db.session.query(Content).filter(Content.user_id == current_user.id).order_by(sa.desc(Content.timestamp))
    contents = query.all()

    return render_template("homepage.html", 
                            tasks=tasks, 
                            posts=posts,
                            people=people,
                            contents=contents,
                            events=events,
                            taskform=taskform, 
                            postform=postform, 
                            personform=personform,
                            workoutform=workoutform, 
                            eventform=eventform,
                            contentform=contentform)

@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    taskform = TaskForm()
    if taskform.validate_on_submit():
        title = taskform.title.data
        description = taskform.description.data
        owner = current_user
        task = Task(title=title, description=description, owner=owner)
        db.session.add(task)
        db.session.commit()
        flash("Task added successfuly")
        return redirect(url_for("homepage"))

@app.route("/update_task/<int:task_id>", methods=["POST"])
@login_required
def update_task(task_id):
    task = db.first_or_404(sa.select(Task).where(Task.id == task_id))
    task.mark_complete()
    db.session.commit()
    flash("Task updated successfully")
    return redirect(url_for("homepage"))

@app.route("/delete_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def delete_task(task_id):
    task = db.first_or_404(sa.select(Task).where(Task.id == task_id))
    task.mark_delete()
    db.session.commit()
    flash("Task deleted successfully")
    return redirect(url_for("homepage"))

@app.route("/add_tag", methods=["POST"])
@login_required
def add_tag():
    tagform = TagForm()
    if tagform.validate_on_submit():
        name = tagform.name.data
        owner = current_user
        tag = Tag(name=name, owner=owner)
        db.session.add(tag)
        db.session.commit()
        flash("Tag added successfully")
        return redirect(url_for("homepage"))

@app.route("/add_post", methods=["POST"])
@login_required
def add_post():
    postform = PostForm()
    if postform.validate_on_submit():
        title = postform.title.data
        body = postform.body.data
        author = current_user
        post = Post(title=title, body=body, author=author)
        db.session.add(post)
        db.session.commit()
        flash("Post added successfuly")
        return redirect(url_for("homepage"))

@app.route("/add_person", methods=["POST"])
@login_required
def add_person():
    personform = PersonForm()
    if personform.validate_on_submit():
        name = personform.name.data
        birthday = personform.birthday.data
        entity = personform.entity.data
        bio = personform.bio.data
        friend = current_user
        person = Person(name=name, birthday=birthday, entity=entity, bio=bio, friend=friend)
        db.session.add(person)
        db.session.commit()
        flash("Person has been added")
        return redirect(url_for("homepage"))
    else:
        flash("Not validated upon submit")
        return redirect(url_for("homepage"))

@app.route("/add_workout", methods=["POST"])
@login_required
def add_workout():
    workoutform = WorkoutForm()
    if workoutform.validate_on_submit():
        activity_name = workoutform.activity_name.data
        activity_location = workoutform.activity_location.data
        duration_minutes = workoutform.duration_minutes.data
        distance_number = workoutform.distance_number.data
        distance_units = workoutform.distance_units.data
        athlete = current_user
        workout = WorkoutActivity(activity_name=activity_name, 
                                  activity_location=activity_location, 
                                  duration_minutes=duration_minutes,
                                  distance_number=distance_number,
                                  distance_units=distance_units,
                                  athlete=athlete)
        db.session.add(workout)
        db.session.commit()
        flash("Workout has been submitted")
        return redirect(url_for("homepage"))


@app.route("/add_event", methods=["POST"])
@login_required
def add_event():
    eventform = EventForm()
    if eventform.validate_on_submit():
        title = eventform.title.data
        description = eventform.description.data
        day = eventform.day.data
        start_time = eventform.start_time.data
        end_time = eventform.end_time.data
        location = eventform.location.data
        event = Event(title=title,
                      description=description,
                      day=day,
                      start_time=start_time,
                      end_time=end_time,
                      location=location,
                      event_owner=current_user)
        db.session.add(event)
        db.session.commit()
        flash("Your event has been added")
        return redirect(url_for("homepage"))


@app.route("/add_content", methods=["POST"])
@login_required
def add_content():
    contentform = ContentForm()
    if contentform.validate_on_submit():
        title = contentform.title.data
        description = contentform.description.data
        content_type = contentform.content_type.data
        url = contentform.url.data
        consumer = current_user
        content = Content(title=title,
                          description=description,
                          content_type=content_type,
                          url=url,
                          consumer=consumer)
        db.session.add(content)
        db.session.commit()
        flash("Your content has been added")
        return redirect(url_for("homepage"))
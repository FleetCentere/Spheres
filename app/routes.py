from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, TaskForm, WorkoutForm, PersonForm, ContentForm, EventForm, TagForm, WeightForm, PredictionForm
from app.models import User, Post, Task, WorkoutActivity, Person, Event, Content, Tag, WeightEntry, Prediction
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone, timedelta, date

bullets = ["Why not try to be excellent; it is fun to see how high you can score",
            "There are no epiphanies, just keep doing one step at a time",
            "Speak less and listen more",
            "Manage the field as best you can"]

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
    posts = user.posts
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

@app.route("/projects")
@login_required
def projects():
    return render_template("projects.html")

@app.route("/homepage")
@login_required
def homepage():
    predictionform = PredictionForm()
    taskform = TaskForm()
    postform = PostForm()
    workoutform = WorkoutForm()
    personform = PersonForm()
    contentform = ContentForm()
    eventform = EventForm()
    tagform = TagForm()
    weightform = WeightForm()
    # getting tasks, posts, people, events, content, tags
    tasks = db.session.query(Task).filter(Task.user_id == current_user.id, Task.deleted == False).order_by(sa.desc(Task.timestamp)).all()
    posts = db.session.query(Post).filter(Post.user_id == current_user.id).order_by(sa.desc(Post.timestamp)).all()
    people = db.session.query(Person).filter(Person.user_id == current_user.id).all()
    events = db.session.query(Event).filter(Event.user_id == current_user.id).order_by(sa.desc(Event.day)).all()
    contents = db.session.query(Content).filter(Content.user_id == current_user.id).order_by(sa.desc(Content.timestamp)).all()
    tags = db.session.query(Tag).filter(Tag.user_id == current_user.id).order_by(sa.desc(Tag.timestamp)).all()
    return render_template("homepage.html", 
                            tasks=tasks, 
                            posts=posts,
                            people=people,
                            contents=contents,
                            events=events,
                            tags=tags,
                            taskform=taskform, 
                            postform=postform, 
                            personform=personform,
                            workoutform=workoutform, 
                            eventform=eventform,
                            contentform=contentform,
                            tagform=tagform,
                            weightform=weightform,
                            predictionform=predictionform,
                            bullets=bullets)

@app.route("/posts")
@login_required
def posts():
    posts = db.session.query(Post).filter(Post.user_id == current_user.id).order_by(sa.desc(Post.timestamp)).all()
    return render_template("posts.html", posts=posts)

@app.route("/people")
@login_required
def people():
    return redirect("homepage")

@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    postform = PostForm()
    post = db.first_or_404(sa.select(Post).where(Post.id == post_id))
    tags = db.session.query(Tag).filter(Tag.user_id == current_user.id).order_by(sa.desc(Tag.timestamp)).all()
    if postform.validate_on_submit():
        post.body = postform.body.data
        post.title = postform.title.data
        db.session.commit()
        flash("Your post has been successfully edited")
        return redirect(url_for("edit_post", post_id=post_id))
    return render_template("edit_post.html", post=post, tags=tags, postform=postform)

@app.route("/remove_post/<int:post_id>")
@login_required
def remove_post(post_id):
    return redirect(url_for("posts"))

@app.route("/tag_post/<int:post_id>/<int:tag_id>")
@login_required
def tag_post(post_id, tag_id):
    post = db.first_or_404(sa.select(Post).where(Post.id == post_id))
    tag = db.first_or_404(sa.select(Tag).where(Tag.id == tag_id))
    if tag in post.tags:
        flash("This tag has already been added")
        return redirect(url_for("edit_post", post_id=post_id))
    else:
        post.tags.append(tag)
        db.session.commit()
        flash("Your tag has been added to your post")
        return redirect(url_for("edit_post", post_id=post_id))

@app.route("/remove_tag/<int:post_id>/<int:tag_id>")
@login_required
def remove_tag(post_id, tag_id):
    post = db.first_or_404(sa.select(Post).where(Post.id == post_id))
    tag = db.first_or_404(sa.select(Tag).where(Tag.id == tag_id))
    if tag in post.tags:
        post.tags.remove(tag)
        db.session.commit()
        flash("Your tag has been removed from this post")
        return redirect(url_for("edit_post", post_id=post_id))
    else:
        flash("This tag is not currently applied to this post")
        return redirect(url_for("edit_post", post_id=post_id))

@app.route("/content", methods=["GET", "POST"])
@app.route("/content/<int:content_id>", methods=["GET", "POST"])
@login_required
def content(content_id=None):
    form = ContentForm()
    if content_id:
        content = db.first_or_404(sa.select(Content).where(Content.id == content_id))
    if form.validate_on_submit():
        if content_id:
            if content.consumer == current_user:
                content.title = form.title.data
                content.description = form.description.data
                content.content_type = form.content_type.data
                content.content_creator = form.content_creator.data
                content.url = form.url.data
                # If a workout_id was provided, link it to the workout
                workout_id = request.form.get('workout_id')
                if workout_id:
                    workout = WorkoutActivity.query.get(workout_id)
                    if workout and workout.athlete == current_user:
                        content.workout = workout
                db.session.commit()
                flash('Your content has been updated!')
                return redirect(url_for("content", content_id=content.id))
        else:
            content = Content(
            title=form.title.data,
            description=form.description.data,
            content_type=form.content_type.data,
            url=form.url.data,
            content_creator=form.content_creator.data,
            consumer=current_user)

            # If a workout_id was provided, link it to the workout
            workout_id = request.form.get('workout_id')
            if workout_id:
                workout = db.get_or_404(WorkoutActivity, workout_id)
                if workout and workout.athlete == current_user:
                    content.workout = workout

            db.session.add(content)
            db.session.commit()
            flash('Your content has been added!')
            return redirect(url_for("content"))
    else:
        print("Form not valid")

    # Get creator statistics
    creator_stats = db.session.query(
        Content.content_creator,
        sa.func.count(Content.id).label('count')
    ).group_by(Content.content_creator).all()

    # Get recent workouts for the dropdown
    recent_workouts = WorkoutActivity.query.filter_by(
        user_id=current_user.id
    ).order_by(WorkoutActivity.timestamp_entry.desc()).limit(10).all()

    # Get last 20 content items
    recent_contents = Content.query.filter_by(
        user_id=current_user.id
    ).order_by(Content.timestamp.desc()).limit(20).all()

    if content_id:
        content = db.first_or_404(sa.select(Content).where(Content.id == content_id))
        if content.consumer == current_user:
            form.title.data = content.title
            form.description.data = content.description
            form.content_type.data = content.content_type
            form.content_creator.data = content.content_creator
            form.url.data = content.url
        else:
            flash("This is not your content to edit")
            return redirect(url_for("content"))

    return render_template('content2.html',
                            form=form,
                            creator_stats=creator_stats,
                            recent_contents=recent_contents,
                            recent_workouts=recent_workouts)

@app.route("/content_creator/<string:creator>")
@login_required
def content_creator(creator):
    return render_template("content_creator.html", 
                            creator=creator)

@app.route("/edit_content/<int:content_id>")
@login_required
def edit_content(content_id):
    content = db.first_or_404(sa.select(Content).where(Content.id == content_id))
    tags = db.session.query(Tag).filter(Tag.user_id == current_user.id).order_by(sa.desc(Tag.timestamp)).all()
    return render_template("edit_content.html", content=content, tags=tags)

@app.route("/tag_content/<int:content_id>/<int:tag_id>")
@login_required
def tag_content(content_id, tag_id):
    content = db.first_or_404(sa.select(Content).where(Content.id == content_id))
    tag = db.first_or_404(sa.select(Tag).where(Tag.id == tag_id))
    if tag in content.tags:
        flash("This tag has already been added")
        return redirect(url_for("edit_content", content_id=content_id))
    else:
        content.tags.append(tag)
        db.session.commit()
        flash("Your tag has been added to your content")
        return redirect(url_for("edit_content", content_id=content_id))

@app.route("/remove_tag_content/<int:content_id>/<int:tag_id>")
@login_required
def remove_tag_content(content_id, tag_id):
    content = db.first_or_404(sa.select(Content).where(Content.id == content_id))
    tag = db.first_or_404(sa.select(Tag).where(Tag.id == tag_id))
    if tag in content.tags:
        content.tags.remove(tag)
        db.session.commit()
        flash("Your tag has been removed from this piece of content")
        return redirect(url_for("edit_content", content_id=content_id))
    else:
        flash("This tag is not currently applied to this piece of content")
        return redirect(url_for("edit_content", content_id=content_id))

@app.route("/tags")
@login_required
def tags():
    tags = db.session.query(Tag).filter(Tag.user_id == current_user.id).options(
        joinedload(Tag.posts),
        joinedload(Tag.events),
        joinedload(Tag.tasks),
        joinedload(Tag.contents)
    ).order_by(sa.desc(Tag.timestamp)).all()
    return render_template("tags.html", tags=tags)

@app.route("/tag/<tag_id>")
@login_required
def tag(tag_id):
    tag = db.first_or_404(sa.select(Tag).where(Tag.id == tag_id))
    return render_template("tag.html", tag=tag)

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
        date = workoutform.day.data
        athlete = current_user
        workout = WorkoutActivity(activity_name=activity_name, 
                                  activity_location=activity_location, 
                                  duration_minutes=duration_minutes,
                                  distance_number=distance_number,
                                  distance_units=distance_units,
                                  date=date,
                                  athlete=athlete)
        db.session.add(workout)
        db.session.commit()
        flash("Workout has been submitted")
        return redirect(url_for("homepage"))
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
        content_creator = contentform.content_creator.data
        url = contentform.url.data
        consumer = current_user
        content = Content(title=title,
                          description=description,
                          content_type=content_type,
                          url=url,
                          content_creator=content_creator,
                          consumer=consumer)
        db.session.add(content)
        db.session.commit()
        flash("Your content has been added")
        return redirect(url_for("content"))
    if request.method == "POST":
        for field, errors in contentform.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "danger")
        return redirect(url_for("homepage"))

@app.route("/add_weight", methods=["GET", "POST"])
@login_required
def add_weight():
    weightform = WeightForm()
    if weightform.validate_on_submit():
        weight = weightform.weight.data
        weightentry = WeightEntry(weight=weight, user=current_user)
        db.session.add(weightentry)
        db.session.commit()
        flash("Your weight has been added")
        return redirect(url_for("homepage"))
    if request.method == "POST":
        for field, errors in weightform.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "danger")
        return redirect(url_for("homepage"))

@app.route("/weights", methods=["GET", "POST"])
@login_required
def weights():
    all_weights = WeightEntry.query.filter_by(user_id=current_user.id).order_by(WeightEntry.timestamp.desc()).all()
    return render_template("weights.html", weights=all_weights)

def get_entries_by_user_and_date(model, user_id, target_date):
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())

    # workouts as "date" is used instead of "timestamp"
    if model == WorkoutActivity:
        entries = (
            model.query.
            filter(model.user_id == current_user.id).
            filter(model.date >= start_of_day, model.date <= end_of_day).
            all()
        )
    # events as "day" is used instead of "timestamp"
    elif model == Event:
        entries = (
            model.query.
            filter(model.user_id == current_user.id).
            filter(model.day == target_date).
            all()
        )
    # generic works for contents, weights, posts, tasks
    else:
        entries = (
            model.query.
            filter(model.user_id == current_user.id).
            filter(model.timestamp >= start_of_day, model.timestamp <= end_of_day).
            all()
        )
    return entries

@app.route("/days")
@login_required
def days():
    n = 10
    actions = { }
    current_day = datetime.now(timezone.utc).date()
    # fill up {actions} with keys of days and values of dictionaries, contents=[], tasks=[], etc for given date
    list_of_days = [current_day]
    for i in range(1,n):
        list_of_days.append(current_day - timedelta(days=i))
    for day in list_of_days:
        actions[day] = {"contents": get_entries_by_user_and_date(Content, current_user.id, day), 
                        "workouts": get_entries_by_user_and_date(WorkoutActivity, current_user.id, day),
                        "weights": get_entries_by_user_and_date(WeightEntry, current_user.id, day),
                        "posts": get_entries_by_user_and_date(Post, current_user.id, day),
                        "tasks": get_entries_by_user_and_date(Task, current_user.id, day),
                        "events": get_entries_by_user_and_date(Event, current_user.id, day)}
    return render_template("days.html", actions=actions, list_of_days=list_of_days)

@app.route("/predictions", methods=["GET", "POST"])
@app.route("/predictions/<int:prediction_id>", methods=["GET", "POST"])
@login_required
def predictions(prediction_id=None):
    predictionform = PredictionForm()
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.timestamp.desc()).all()
    if predictionform.validate_on_submit():
        if prediction_id == None:
            prediction = Prediction(statement=predictionform.statement.data,
                                    check_date=predictionform.check_date.data,
                                    associated_content=predictionform.associated_content.data,
                                    predictor=current_user)
            db.session.add(prediction)
            db.session.commit()
            flash("Your prediction has been added")
        else:
            prediction = db.first_or_404(sa.select(Prediction).where(Prediction.id == prediction_id))
            if prediction.predictor == current_user:
                prediction.statement = predictionform.statement.data
                prediction.check_date = predictionform.check_date.data
                prediction.associated_content = predictionform.associated_content.data
                db.session.commit()
                flash("Your prediction has been updated")
        return redirect(url_for("predictions"))
    if prediction_id is not None:
        prediction = db.first_or_404(sa.select(Prediction).where(Prediction.id == prediction_id))
        if prediction.predictor == current_user:
            predictionform.statement.data = prediction.statement
            predictionform.check_date.data = prediction.check_date
            predictionform.associated_content.data = prediction.associated_content
        else:
            flash("You are unable to edit this prediction")
            return(redirect(url_for("predictions")))
    return render_template("predictions.html", predictions=predictions, predictionform=predictionform)

@app.route("/events", methods=["GET", "POST"])
@app.route("/events/<int:event_id>", methods=["GET", "POST"])
@login_required
def events(event_id=None):
    events = Event.query.filter_by(user_id=current_user.id).order_by(Event.day.desc()).all()
    event = db.first_or_404(sa.select(Event).where(Event.id == event_id)) if event_id is not None else None
    return render_template("events.html", 
                            events=events, 
                            event=event)

@app.route("/add_prediction", methods=["GET", "POST"])
@login_required
def add_prediction():
    return redirect(url_for("predictions"))

@app.route("/homepage_2025", methods=["GET", "POST"])
@login_required
def homepage_2025():
    return render_template("homepage_2025.html")
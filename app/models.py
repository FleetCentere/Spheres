from datetime import datetime, timezone, time
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

followers = sa.Table(
    "followers",
    db.metadata,
    sa.Column("follower_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("followed_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True)
)

event_attendees = sa.Table(
    "event_attendees",
    db.metadata,
    sa.Column("event_id", sa.Integer, sa.ForeignKey("events.id"), primary_key=True),
    sa.Column("person_id", sa.Integer, sa.ForeignKey("people.id"), primary_key=True)
)

# association tables for tags

task_tags = sa.Table(
    "task_tags",
    db.metadata,
    sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id"), primary_key=True),
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True),
)

post_tags = sa.Table(
    "post_tags",
    db.metadata,
    sa.Column("post_id", sa.Integer, sa.ForeignKey("posts.id"), primary_key=True),
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True),
)

event_tags = sa.Table(
    "event_tags",
    db.metadata,
    sa.Column("event_id", sa.Integer, sa.ForeignKey("events.id"), primary_key=True),
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True),
)

content_tags = sa.Table(
    "content_tags",
    db.metadata,
    sa.Column("content_id", sa.Integer, sa.ForeignKey("contents.id"), primary_key=True),
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True),
)

prediction_tags = sa.Table(
    "prediction_tags",
    db.metadata,
    sa.Column("prediction_id", sa.Integer, sa.ForeignKey("predictions.id"), primary_key=True),
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True),
)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    posts: so.Mapped[list["Post"]] = so.relationship(back_populates="author", uselist=True)
    tasks: so.Mapped[list["Task"]] = so.relationship(back_populates="owner", uselist=True)
    workout_activities: so.Mapped[list["WorkoutActivity"]] = so.relationship(back_populates="athlete", uselist=True)
    people: so.Mapped[list["Person"]] = so.relationship(back_populates="friend", uselist=True)
    events: so.Mapped[list["Event"]] = so.relationship(back_populates="event_owner", uselist=True)
    contents: so.Mapped[list["Content"]] = so.relationship(back_populates="consumer", uselist=True)
    tags: so.Mapped[list["Tag"]] = so.relationship(back_populates="owner", uselist=True)
    weight_entries: so.Mapped[list["WeightEntry"]] = so.relationship(back_populates="user", uselist=True)
    predictions: so.Mapped[list["Prediction"]] = so.relationship(back_populates="predictor", uselist=True)

    following: so.Mapped[list["User"]] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        back_populates="followers"
    )

    followers: so.Mapped[list["User"]] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates="following"
    )

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = (
            sa.select(followers)
            .where(
                followers.c.follower_id == self.id,
                followers.c.followed_id == user.id,
            )
        )
        return db.session.scalar(query) is not None
    
    def followers_count(self):
        query = (
            sa.select(sa.func.count())
            .select_from(followers)
            .where(followers.c.followed_id == self.id)
            )
        return db.session.scalar(query)

    def following_count(self):
        query = (
            sa.select(sa.func.count())
            .select_from(followers)
            .where(followers.c.follower_id == self.id)
        )
        return db.session.scalar(query)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )

    def __repr__(self):
        return "<User {}>".format(self.username)

class WeightEntry(db.Model):
    __tablename__ = "weight_entries"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    weight: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    user: so.Mapped[User] = so.relationship(back_populates="weight_entries")

    def __repr__(self):
        return f"<WeightEntry {self.weight} lbs on {self.timestamp}>"

class Tag(db.Model):
    __tablename__ = "tags"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True, nullable=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    owner: so.Mapped[User] = so.relationship(back_populates="tags")

    posts: so.Mapped[list["Post"]] = so.relationship("Post", secondary=post_tags, back_populates="tags", uselist=True)
    tasks: so.Mapped[list["Task"]] = so.relationship("Task", secondary=task_tags, back_populates="tags", uselist=True)
    events: so.Mapped[list["Event"]] = so.relationship("Event", secondary=event_tags, back_populates="tags", uselist=True)
    contents: so.Mapped[list["Content"]] = so.relationship("Content", secondary=content_tags, back_populates="tags", uselist=True)
    predictions: so.Mapped[list["Prediction"]] = so.relationship("Prediction", secondary=prediction_tags, back_populates="tags", uselist=True)

    def __repr__(self):
        return f"<Tag {self.name}>"

class Post(db.Model):
    __tablename__ = "posts"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140), default="", nullable=True)
    body: so.Mapped[str] = so.mapped_column(sa.Text)
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates="posts")
    tags: so.Mapped[list["Tag"]] = so.relationship("Tag", secondary=post_tags, back_populates="posts", uselist=True)
    
    def __repr__(self):
        return "<Post {}>".format(self.body)

class Task(db.Model):
    __tablename__ = "tasks"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(100))
    description: so.Mapped[str] = so.mapped_column(sa.Text)
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    completed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    deleted: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    owner: so.Mapped[User] = so.relationship(back_populates="tasks")
    tags: so.Mapped[list["Tag"]] = so.relationship("Tag", secondary=task_tags, back_populates="tasks", uselist=True)

    def mark_complete(self):
        self.completed = not self.completed

    def mark_delete(self):
        self.deleted = not self.deleted

    def __repr__(self):
        return "<Task {}>".format(self.title)

class WorkoutActivity(db.Model):
    __tablename__ = "workout_activities"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    activity_name: so.Mapped[str] = so.mapped_column(sa.String(100))
    activity_location: so.Mapped[str] = so.mapped_column(sa.String(100))
    duration_minutes: so.Mapped[int] = so.mapped_column(sa.Integer)
    distance_number: so.Mapped[float] = so.mapped_column(sa.Float)
    distance_units: so.Mapped[str] = so.mapped_column(sa.String(100))
    date: so.Mapped[Optional[datetime]] = so.mapped_column(nullable=True)
    timestamp_entry: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    athlete: so.Mapped[User] = so.relationship(back_populates="workout_activities")
    
    contents: so.Mapped[list["Content"]] = so.relationship(back_populates="workout", uselist=True)
    
    def __repr__(self):
        return f"<WorkoutActivity {self.activity_name} - {self.duration_minutes} min by {self.athlete.username}>"
    
class Person(db.Model):
    __tablename__ = "people"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(120), nullable=False)
    birthday: so.Mapped[Optional[datetime]] = so.mapped_column(nullable=True)
    entity: so.Mapped[str] = so.mapped_column(sa.String(120))
    bio: so.Mapped[str] = so.mapped_column(sa.Text, default="")
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    friend: so.Mapped[User] = so.relationship(back_populates="people")

    events: so.Mapped[list["Event"]] = so.relationship(
        "Event",
        secondary=event_attendees,
        back_populates="attendees",
        uselist=True)

    def __repr__(self):
        return f"<Person {self.name}>"

class Event(db.Model):
    __tablename__ = "events"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    day: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    start_time: so.Mapped[time] = so.mapped_column()
    end_time: so.Mapped[time] = so.mapped_column()
    location: so.Mapped[str] = so.mapped_column(sa.String(120))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    event_owner: so.Mapped[User] = so.relationship(back_populates="events")
    tags: so.Mapped[list["Tag"]] = so.relationship("Tag", secondary=event_tags, back_populates="events", uselist=True)

    attendees: so.Mapped[list["Person"]] = so.relationship(
        "Person",
        secondary=event_attendees,
        back_populates="events", 
        uselist=True)

    def __repr__(self):
        return f"<Event {self.title}>"

class Content(db.Model):
    __tablename__ = "contents"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140), nullable=False)
    description: so.Mapped[str] = so.mapped_column(sa.Text)
    content_type: so.Mapped[str] = so.mapped_column(sa.String(50))
    content_creator: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=True)
    url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    timestamp: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    consumer: so.Mapped[User] = so.relationship(back_populates="contents")
    
    workout_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(WorkoutActivity.id), index=True, nullable=True)
    workout: so.Mapped[WorkoutActivity] = so.relationship(back_populates="contents")
    
    tags: so.Mapped[list["Tag"]] = so.relationship("Tag", secondary=content_tags, back_populates="contents", uselist=True)

    def __repr__(self):
        return f"<Content {self.title} ({self.content_type})>"

class Prediction(db.Model):
    __tablename__ = "predictions"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    statement: so.Mapped[str] = so.mapped_column(sa.String(140), nullable=False)
    check_date: so.Mapped[datetime] = so.mapped_column()
    associated_content: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    
    tags: so.Mapped[list["Tag"]] = so.relationship("Tag", secondary=prediction_tags, back_populates="predictions", uselist=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    predictor: so.Mapped[User] = so.relationship(back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction {self.statement} ({self.check_date})>"

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, DateField, DateTimeField, TimeField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError("Please use a different username")

    def validate_email(self, email):
        email = db.session.scalar(sa.select(User).where(User.email == email.data))
        if email is not None:
            raise ValidationError("Please use a different email address")

class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError("Please use a different username")

class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")

class PostForm(FlaskForm):
    title = StringField("Title")
    body = TextAreaField("Submit your post", validators=[DataRequired(), Length(min=1, max=240)])
    tags = StringField("Tags", validators=[Optional()])
    submit = SubmitField("Submit")

class TagForm(FlaskForm):
    name = StringField("Name")
    submit = SubmitField("Submit")

class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField("Submit")

class WorkoutForm(FlaskForm):
    activity_name = StringField("Activity Name")
    activity_location = StringField("Location")
    day = DateField("Date")
    duration_minutes = IntegerField("Time (minutes)")
    distance_number = FloatField("Distance")
    distance_units = StringField("Distance units")
    submit = SubmitField("Submit")

class PersonForm(FlaskForm):
    name = StringField("Name")
    birthday = DateField("Birthday", validators=[Optional()])
    entity = StringField("Entity")
    bio = TextAreaField("Bio")
    submit = SubmitField("Submit")

class ContentForm(FlaskForm):
    title = StringField("Title")
    description = StringField("Description")
    content_type = StringField("Type")
    content_creator = StringField("Creator")
    url = StringField("url", validators=[Optional()])
    date_time = DateTimeField("Date and time", validators=[Optional()])
    submit = SubmitField("Submit")

class EventForm(FlaskForm):
    title = StringField("Title")
    description = StringField("Description")
    day = DateField("Day")
    start_time = TimeField("Start Time")
    end_time = TimeField("End Time")
    location = StringField("Location")
    submit = SubmitField("Submit")

class WeightForm(FlaskForm):
    weight = FloatField("Weight")
    submit = SubmitField("Submit")

class PredictionForm(FlaskForm):
    statement = StringField("Statement")
    check_date = DateField("Deadline")
    associated_content = TextAreaField("Additional Comments", validators=[Optional()])
    submit = SubmitField("Submit")
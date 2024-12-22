from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,FileField,SubmitField
from wtforms.validators import DataRequired,Email,EqualTo,Length
from flask_wtf.file import FileAllowed

class RegistrationForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(),Email(),Length(max=120)])
    username = StringField("User name ",validators=[DataRequired(),Length(min=3,max=80)])
    password = PasswordField("Password",validators=[DataRequired(),Length(min=8)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    profile_image = FileField("profile Image",
                              validators=[FileAllowed(["jpg","png","jpeg"],"Images Only!")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email",validators=[Email(),DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Login")


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=3,max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_image = FileField("profile Image",
                              validators=[FileAllowed(["jpg","png","jpeg"],"Images Only!")])
    password = PasswordField('Your Password',validators=[DataRequired()])
    new_password = PasswordField('New Password')
    submit = SubmitField('Update Profile')


class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    new_password =  PasswordField('Your Password',validators=[DataRequired()])
    submit = SubmitField('Update Profile')


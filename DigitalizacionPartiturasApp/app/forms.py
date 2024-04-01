from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match.')
    ])
    confirm_password = PasswordField('Repeat Password', validators=[validators.DataRequired()])
    submit = SubmitField('Register')

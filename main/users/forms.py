from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import Email, Length, DataRequired, EqualTo, ValidationError
from main.models import UsersTable
from flask_login import current_user


class Register(FlaskForm):
    '''This is a class that creates the register form'''
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=10)])
    email = StringField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        '''Method to validated field from the database'''
        user = UsersTable.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Sorry, username already exists. Try another one!')

    def validate_email(self, email):
        '''Method to validated field from the database'''
        user = UsersTable.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Sorry, email already exists. Try another one!')


class Login(FlaskForm):
    '''This is a class that defines the login form'''
    email = StringField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)])
    remember = BooleanField('Remember Me?')
    submit = SubmitField('Login')


class UpdateAccount(FlaskForm):
    '''This is a class that creates the account update form'''
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=10)])
    email = StringField('Email', validators=[Email(), DataRequired()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg','png', 'jpeg'])])
    submit = SubmitField('Register')

    def validate_username(self, username):
        '''Method to validated field from the database'''
        if current_user.username != username.data:
            user = UsersTable.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Sorry, username already exists. Try another one!')

    def validate_email(self, email):
        '''Method to validated field from the database'''
        if current_user.email != email.data:
            user = UsersTable.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Sorry, email already exists. Try another one!')


class ResetRequest(FlaskForm):
    '''This is a class that creates the reset request form'''
    email = StringField('Email', validators=[Email(), DataRequired()])
    submit = SubmitField('Request')

    def validate_email(self, email):
        user = UsersTable.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Sorry, this email has not been registered!')


class ResetPassword(FlaskForm):
    '''This is a form that creates the reset password form'''
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
from main import mail
import os
import secrets
from flask_mail import Message
from flask import url_for, current_app


def save_profile_picture(picture):
    profile_picture_token = secrets.token_hex(8)
    _, picture_extension = os.path.splitext(picture.filename)
    image_name = profile_picture_token + picture_extension
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', image_name)
    picture.save(picture_path)

    return image_name


def send_reset_email(user):
    token = user.create_reset_token()
    msg = Message('Password Change', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, follow this link:
        {url_for('users.reset_password', token=token, _external=True)}

        Ignore if you did not initiate the request.'''
    mail.send(msg)
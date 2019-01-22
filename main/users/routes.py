from main import db, pass_generator
from flask import render_template, url_for, redirect, flash, request, Blueprint, current_app
from main.users.forms import Register, Login, UpdateAccount, ResetRequest, ResetPassword
from main.models import UsersTable, PostsTable
from flask_login import login_user, current_user, logout_user, login_required
from main.users.utils import save_profile_picture, send_reset_email

users = Blueprint('users', __name__)

@users.route('/login', methods=['POST', 'GET'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = UsersTable.query.filter_by(email=form.email.data).first()
        if user and pass_generator.check_password_hash(user.password, form.password.data):
            flash('Logged in successfully!', 'success')
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Recheck your credentials', 'danger')
    return render_template('login.html', form=form)


@users.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = Register()
    if form.validate_on_submit():
        hashed_password = pass_generator.generate_password_hash(form.password.data).decode('utf-8')
        user = UsersTable(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Created account. Please login', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)


@users.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    profile_image = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    form = UpdateAccount()
    if form.validate_on_submit():
        if form.picture.data:
            profile_picture = save_profile_picture(form.picture.data)
            current_user.image_file = profile_picture
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Updated account', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title="Account", profile_image=profile_image, form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/posts/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = UsersTable.query.filter_by(username=username).first_or_404()
    posts = PostsTable.query.filter_by(author=user).paginate(page=page, per_page=2)
    return render_template('users-posts.html', posts=posts, user=user)


@users.route('/reset-request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetRequest()
    if form.validate_on_submit():
        user = UsersTable.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Check your email for a reset link', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset-request.html', title='Reset Password', form=form)


@users.route('/reset-request/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = UsersTable.verify_reset_token(token)
    if user is None:
        flash('Token is expired or invalid. Retry again.', 'danger')
        return redirect(url_for('users.reset_request'))
    form = ResetPassword()
    if form.validate_on_submit():
        hashed_password = pass_generator.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset-password.html', title='Reset Password', form=form)
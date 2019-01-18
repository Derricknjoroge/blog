from main import app, db, pass_generator, mail
from flask import render_template, url_for, redirect, flash, request, abort
from main.forms import Register, Login, UpdateAccount, NewPost, ResetRequest, ResetPassword
from main.models import UsersTable, PostsTable
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = PostsTable.query.order_by(PostsTable.id.desc()).paginate(per_page=2, page=page)
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = UsersTable.query.filter_by(email=form.email.data).first()
        if user and pass_generator.check_password_hash(user.password, form.password.data):
            flash('Logged in successfully!', 'success')
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Recheck your credentials', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Register()
    if form.validate_on_submit():
        hashed_password = pass_generator.generate_password_hash(form.password.data).decode('utf-8')
        user = UsersTable(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Created account. Please login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


def save_profile_picture(picture):
    profile_picture_token = secrets.token_hex(8)
    _, picture_extension = os.path.splitext(picture.filename)
    image_name = profile_picture_token + picture_extension
    picture_path = os.path.join(app.root_path, 'static/profile_pics', image_name)
    picture.save(picture_path)

    return image_name


@app.route('/account', methods=['POST', 'GET'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title="Account", profile_image=profile_image, form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/new/post', methods=['GET', 'POST'])
def new_post():
    form = NewPost()
    if form.validate_on_submit():
        the_post = PostsTable(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(the_post)
        db.session.commit()
        flash('Post created successfully', 'success')
        return redirect(url_for('new_post'))
    return render_template('new-post.html', title='New Post', form=form, legend='New Post')


@app.route('/post/<int:post_id>')
def post(post_id):
    the_post = PostsTable.query.get_or_404(post_id)
    return render_template('post.html', post=the_post, title=the_post.title)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    the_post = PostsTable.query.get_or_404(post_id)
    if current_user.email != the_post.author.email:
        abort(403)
    form = NewPost()
    if form.validate_on_submit():
        the_post.title = form.title.data
        the_post.content = form.content.data
        db.session.commit()
        flash('Post updated successfully', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = the_post.title
        form.content.data = the_post.content
    return render_template('new-post.html', title=the_post.title, form=form, legend='Update Post')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    the_post = PostsTable.query.get(post_id)
    if current_user.email != the_post.author.email:
        abort(403)
    db.session.delete(the_post)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/posts/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = UsersTable.query.filter_by(username=username).first_or_404()
    posts = PostsTable.query.filter_by(author=user).paginate(page=page, per_page=2)
    return render_template('users-posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.create_reset_token()
    msg = Message('Password Change', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, follow this link:
        {url_for('reset_password', token=token, _external=True)}
        
        Ignore if you did not initiate the request.'''
    mail.send(msg)


@app.route('/reset-request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetRequest()
    if form.validate_on_submit():
        user = UsersTable.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Check your email for a reset link', 'success')
        return redirect(url_for('login'))
    return render_template('reset-request.html', title='Reset Password', form=form)


@app.route('/reset-request/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = UsersTable.verify_reset_token(token)
    if user is None:
        flash('Token is expired or invalid. Retry again.', 'danger')
        return redirect(url_for('reset_request'))
    form = ResetPassword()
    if form.validate_on_submit():
        hashed_password = pass_generator.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset-password.html', title='Reset Password', form=form)

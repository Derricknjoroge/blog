from main import db
from flask import render_template, url_for, current_app,  redirect, flash, request, abort, Blueprint
from main.models import PostsTable
from flask_login import current_user, login_required
from main.posts.forms import NewPost

posts = Blueprint('posts',__name__)


@posts.route('/new/post', methods=['GET', 'POST'])
def new_post():
    form = NewPost()
    if form.validate_on_submit():
        the_post = PostsTable(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(the_post)
        db.session.commit()
        flash('Post created successfully', 'success')
        return redirect(url_for('posts.new_post'))
    return render_template('new-post.html', title='New Post', form=form, legend='New Post')


@posts.route('/post/<int:post_id>')
def post(post_id):
    the_post = PostsTable.query.get_or_404(post_id)
    return render_template('post.html', post=the_post, title=the_post.title)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
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
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.title.data = the_post.title
        form.content.data = the_post.content
    return render_template('new-post.html', title=the_post.title, form=form, legend='Update Post')


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    the_post = PostsTable.query.get(post_id)
    if current_user.email != the_post.author.email:
        abort(403)
    db.session.delete(the_post)
    db.session.commit()
    return redirect(url_for('main.home'))
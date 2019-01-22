from flask import current_app
from flask import render_template, request, Blueprint
from main.models import PostsTable

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = PostsTable.query.order_by(PostsTable.id.desc()).paginate(per_page=2, page=page)
    return render_template('home.html', posts=posts)


@main.route('/about')
def about():
    return render_template('about.html', title='About')
from flask import render_template
from blueprints.blog import bp

@bp.route('/')
def index():
    return render_template('blog/index.html', title='Blog')

@bp.route('/create')
def create():
    return render_template('blog/create.html', title='Create Post')

@bp.route('/post/<int:id>')
def post(id):
    return render_template('blog/post.html', title='Post')

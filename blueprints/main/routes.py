from flask import render_template
from blueprints.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/about')
def about():
    return render_template('about.html', title='About')

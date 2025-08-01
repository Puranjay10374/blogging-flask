from flask import Blueprint

bp = Blueprint('blog', __name__)

from blueprints.blog import routes

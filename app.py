from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import Config
from models import db, User, Post
from datetime import datetime

# Initialize extensions
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Update user's last seen timestamp on each request
    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
    
    # Register blueprints
    from blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from blueprints.blog import bp as blog_bp
    app.register_blueprint(blog_bp, url_prefix='/blog')
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

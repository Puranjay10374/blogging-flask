from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
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

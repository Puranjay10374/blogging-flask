import os

class Config:
    """Basic configuration for personal blogging app"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pagination
    POSTS_PER_PAGE = 5
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
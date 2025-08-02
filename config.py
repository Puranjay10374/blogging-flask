import os

class Config:
    """Basic configuration for personal blogging app"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pagination settings
    POSTS_PER_PAGE = 5
    USERS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 10
    
    # Blog settings
    MAX_POST_TITLE_LENGTH = 200
    MAX_POST_CONTENT_LENGTH = 50000
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds
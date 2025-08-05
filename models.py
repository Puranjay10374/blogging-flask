from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Create db instance that will be imported by app.py
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Enhanced profile fields
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    avatar_url = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Social media links
    twitter_handle = db.Column(db.String(50))
    linkedin_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    
    # Privacy settings
    profile_public = db.Column(db.Boolean, default=True)
    show_email = db.Column(db.Boolean, default=False)
    
    # Relationship with posts
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    # Relationship with likes
    liked_posts = db.relationship('Like', foreign_keys='Like.user_id', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_liked_post(self, post):
        return self.liked_posts.filter_by(post_id=post.id).first() is not None
    
    def like_post(self, post):
        if not self.has_liked_post(post):
            like = Like(user_id=self.id, post_id=post.id)
            db.session.add(like)
            return like
        return None
    
    def unlike_post(self, post):
        like = self.liked_posts.filter_by(post_id=post.id).first()
        if like:
            db.session.delete(like)
            return True
        return False
    
    def get_liked_posts(self, limit=None):
        query = Post.query.join(Like).filter(Like.user_id == self.id).order_by(Like.created_at.desc())
        if limit:
            return query.limit(limit).all()
        return query.all()
    
    def get_liked_posts_count(self):
        return self.liked_posts.count()
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def avatar(self):
        if self.avatar_url:
            return self.avatar_url
        # Default avatar using Gravatar
        import hashlib
        email_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=128"
    
    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()
    
    def get_post_count(self):
        return self.posts.count()
    
    def get_recent_posts(self, limit=5):
        return self.posts.order_by(Post.created_at.desc()).limit(limit).all()
    
    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship with comments
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    # Relationship with likes
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_comment_count(self):
        return self.comments.filter_by(parent_id=None).count()
    
    def get_all_comments_count(self):
        return self.comments.count()
    
    def get_top_level_comments(self):
        return self.comments.filter_by(parent_id=None).order_by(Comment.created_at.asc()).all()
    
    def get_like_count(self):
        return self.likes.count()
    
    def is_liked_by(self, user):
        if user is None or not user.is_authenticated:
            return False
        return self.likes.filter_by(user_id=user.id).first() is not None
    
    def get_recent_likes(self, limit=5):
        return self.likes.order_by(Like.created_at.desc()).limit(limit).all()
    
    def __repr__(self):
        return f'<Post {self.title}>'

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    
    # Composite unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
    
    def __repr__(self):
        return f'<Like {self.id}: User {self.user_id} likes Post {self.post_id}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    
    # Relationships
    author = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), 
                             lazy='dynamic', cascade='all, delete-orphan')
    
    def get_replies(self):
        return self.replies.order_by(Comment.created_at.asc()).all()
    
    def get_replies_count(self):
        return self.replies.count()
    
    def is_reply(self):
        return self.parent_id is not None
    
    def get_thread_depth(self):
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.author.username}>'
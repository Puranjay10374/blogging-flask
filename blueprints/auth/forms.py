from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, URLField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, Optional, URL, Regexp
from models import User

# Simple email validation regex pattern
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[
        DataRequired(message='Username or email is required')
    ], render_kw={'placeholder': 'Enter username or email', 'class': 'form-control'})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ], render_kw={'placeholder': 'Enter your password', 'class': 'form-control'})
    
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In', render_kw={'class': 'btn btn-primary'})

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=4, max=20, message='Username must be between 4 and 20 characters'),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ], render_kw={'placeholder': 'Choose a unique username', 'class': 'form-control'})
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'), 
        Regexp(EMAIL_REGEX, message='Please enter a valid email address.')
    ], render_kw={'placeholder': 'your.email@example.com', 'class': 'form-control'})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', 
               message='Password must contain at least one lowercase letter, one uppercase letter, and one number')
    ], render_kw={'placeholder': 'Create a strong password', 'class': 'form-control'})
    
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(message='Password confirmation is required'),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'placeholder': 'Confirm your password', 'class': 'form-control'})
    
    terms_accepted = BooleanField('I accept the Terms of Service', validators=[
        DataRequired(message='You must accept the terms of service')
    ])
    
    submit = SubmitField('Create Account', render_kw={'class': 'btn btn-primary'})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=4, max=20, message='Username must be between 4 and 20 characters'),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ], render_kw={'class': 'form-control'})
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'), 
        Regexp(EMAIL_REGEX, message='Please enter a valid email address.')
    ], render_kw={'class': 'form-control'})
    
    first_name = StringField('First Name', validators=[
        Optional(),
        Length(max=50, message='First name cannot exceed 50 characters')
    ], render_kw={'class': 'form-control'})
    
    last_name = StringField('Last Name', validators=[
        Optional(),
        Length(max=50, message='Last name cannot exceed 50 characters')
    ], render_kw={'class': 'form-control'})
    
    bio = TextAreaField('Bio', validators=[
        Optional(),
        Length(max=500, message='Bio cannot exceed 500 characters')
    ], render_kw={'rows': 4, 'placeholder': 'Tell us about yourself...', 'class': 'form-control'})
    
    location = StringField('Location', validators=[
        Optional(),
        Length(max=100, message='Location cannot exceed 100 characters')
    ], render_kw={'class': 'form-control'})
    
    website = URLField('Website', validators=[
        Optional(),
        URL(message='Please enter a valid URL')
    ], render_kw={'placeholder': 'https://yourwebsite.com', 'class': 'form-control'})
    
    avatar_url = URLField('Avatar URL', validators=[
        Optional(),
        URL(message='Please enter a valid image URL')
    ], render_kw={'placeholder': 'https://example.com/avatar.jpg', 'class': 'form-control'})
    
    # Social media links
    twitter_handle = StringField('Twitter Username', validators=[
        Optional(),
        Length(max=15, message='Twitter username cannot exceed 15 characters'),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Invalid Twitter username format')
    ], render_kw={'placeholder': 'username (without @)', 'class': 'form-control'})
    
    linkedin_url = URLField('LinkedIn Profile', validators=[
        Optional(),
        URL(message='Please enter a valid LinkedIn URL')
    ], render_kw={'placeholder': 'https://linkedin.com/in/username', 'class': 'form-control'})
    
    github_url = URLField('GitHub Profile', validators=[
        Optional(),
        URL(message='Please enter a valid GitHub URL')
    ], render_kw={'placeholder': 'https://github.com/username', 'class': 'form-control'})
    
    # Privacy settings
    profile_public = BooleanField('Make Profile Public', default=True)
    show_email = BooleanField('Show Email Publicly')
    
    submit = SubmitField('Update Profile', render_kw={'class': 'btn btn-success'})

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_twitter_handle(self, twitter_handle):
        """Remove @ symbol if user includes it"""
        if twitter_handle.data and twitter_handle.data.startswith('@'):
            twitter_handle.data = twitter_handle.data[1:]

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ], render_kw={'placeholder': 'Enter current password', 'class': 'form-control'})
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', 
               message='Password must contain at least one lowercase letter, one uppercase letter, and one number')
    ], render_kw={'placeholder': 'Enter new password', 'class': 'form-control'})
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Password confirmation is required'),
        EqualTo('new_password', message='Passwords must match')
    ], render_kw={'placeholder': 'Confirm new password', 'class': 'form-control'})
    
    submit = SubmitField('Change Password', render_kw={'class': 'btn btn-warning'})

class DeleteAccountForm(FlaskForm):
    confirm_username = StringField('Type your username to confirm', validators=[
        DataRequired(message='Username confirmation is required')
    ], render_kw={'placeholder': 'Enter your username', 'class': 'form-control'})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ], render_kw={'placeholder': 'Enter your password', 'class': 'form-control'})
    
    submit = SubmitField('Delete My Account', render_kw={'class': 'btn btn-danger'})

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Regexp(EMAIL_REGEX, message='Please enter a valid email address.')
    ], render_kw={'placeholder': 'Enter your email address', 'class': 'form-control'})
    
    submit = SubmitField('Reset Password', render_kw={'class': 'btn btn-primary'})

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', 
               message='Password must contain at least one lowercase letter, one uppercase letter, and one number')
    ], render_kw={'placeholder': 'Enter new password', 'class': 'form-control'})
    
    password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Password confirmation is required'),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'placeholder': 'Confirm new password', 'class': 'form-control'})
    
    submit = SubmitField('Reset Password', render_kw={'class': 'btn btn-success'})

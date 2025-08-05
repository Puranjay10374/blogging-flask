from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from datetime import date

# Blog-related forms only (Auth forms moved to blueprints/auth/forms.py)

class PostForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters')
    ], render_kw={'placeholder': 'Enter an engaging title...', 'class': 'form-control'})
    
    content = TextAreaField('Content', validators=[
        DataRequired(message='Content is required'),
        Length(min=50, message='Content must be at least 50 characters')
    ], render_kw={'rows': 15, 'placeholder': 'Write your blog post content here...', 'class': 'form-control'})
    
    excerpt = TextAreaField('Excerpt (Optional)', validators=[
        Optional(),
        Length(max=300, message='Excerpt cannot exceed 300 characters')
    ], render_kw={'rows': 3, 'placeholder': 'Brief summary of your post...', 'class': 'form-control'})
    
    allow_comments = BooleanField('Allow comments', default=True)
    is_published = BooleanField('Publish immediately', default=True)
    
    submit = SubmitField('Publish Post', render_kw={'class': 'btn btn-primary'})

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[
        Optional(),
        Length(min=1, max=100, message='Search query must be between 1 and 100 characters')
    ], render_kw={'placeholder': 'Search posts, titles, content...', 'class': 'form-control'})
    
    submit = SubmitField('Search', render_kw={'class': 'btn btn-primary'})

class AdvancedSearchForm(FlaskForm):
    query = StringField('Search', validators=[
        Optional(),
        Length(min=1, max=100, message='Search query must be between 1 and 100 characters')
    ], render_kw={'placeholder': 'Search posts, titles, content...', 'class': 'form-control'})
    
    author = StringField('Author', validators=[Optional()], 
                        render_kw={'placeholder': 'Author username', 'class': 'form-control'})
    
    date_from = DateField('From Date', validators=[Optional()], format='%Y-%m-%d',
                         render_kw={'class': 'form-control'})
    date_to = DateField('To Date', validators=[Optional()], format='%Y-%m-%d',
                       render_kw={'class': 'form-control'})
    
    sort_by = SelectField('Sort By', choices=[
        ('newest', 'Newest First'),
        ('oldest', 'Oldest First'),
        ('most_liked', 'Most Liked'),
        ('most_commented', 'Most Commented'),
        ('title_asc', 'Title A-Z'),
        ('title_desc', 'Title Z-A')
    ], default='newest', render_kw={'class': 'form-control'})
    
    submit = SubmitField('Search', render_kw={'class': 'btn btn-primary'})
    
    def validate_date_range(self):
        if self.date_from.data and self.date_to.data:
            if self.date_from.data > self.date_to.data:
                raise ValidationError('Start date must be before end date')
            if self.date_from.data > date.today():
                raise ValidationError('Start date cannot be in the future')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[
        DataRequired(message='Comment cannot be empty'),
        Length(min=1, max=1000, message='Comment must be between 1 and 1000 characters')
    ], render_kw={'placeholder': 'Write your comment here...', 'rows': 4, 'class': 'form-control'})
    
    submit = SubmitField('Post Comment', render_kw={'class': 'btn btn-primary'})

class ReplyForm(FlaskForm):
    content = TextAreaField('Reply', validators=[
        DataRequired(message='Reply cannot be empty'),
        Length(min=1, max=500, message='Reply must be between 1 and 500 characters')
    ], render_kw={'placeholder': 'Write your reply here...', 'rows': 3, 'class': 'form-control'})
    
    submit = SubmitField('Post Reply', render_kw={'class': 'btn btn-primary btn-sm'})

class EditCommentForm(FlaskForm):
    content = TextAreaField('Edit Comment', validators=[
        DataRequired(message='Comment cannot be empty'),
        Length(min=1, max=1000, message='Comment must be between 1 and 1000 characters')
    ], render_kw={'rows': 4, 'class': 'form-control'})
    
    submit = SubmitField('Update Comment', render_kw={'class': 'btn btn-success'})

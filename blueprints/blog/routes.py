from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from blueprints.blog import bp
from models import db, Post
from forms import PostForm, SearchForm

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    return render_template('blog/index.html', title='Blog Posts', posts=posts)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        
        flash('Your post has been created!', 'success')
        return redirect(url_for('blog.index'))
    
    return render_template('blog/create.html', title='Create Post', form=form)

@bp.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('blog/post.html', title=post.title, post=post)

@bp.route('/post/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    
    if post.author != current_user:
        flash('You can only edit your own posts!', 'error')
        return redirect(url_for('blog.post', id=id))
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        
        flash('Your post has been updated!', 'success')
        return redirect(url_for('blog.post', id=id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    
    return render_template('blog/edit.html', title='Edit Post', form=form, post=post)

@bp.route('/post/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    
    if post.author != current_user:
        flash('You can only delete your own posts!', 'error')
        return redirect(url_for('blog.post', id=id))
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('blog.index'))

@bp.route('/my-posts')
@login_required
def my_posts():
    page = request.args.get('page', 1, type=int)
    posts = current_user.posts.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    return render_template('blog/my_posts.html', title='My Posts', posts=posts)

@bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if query:
        # Search in both title and content
        posts = Post.query.filter(
            db.or_(
                Post.title.contains(query),
                Post.content.contains(query)
            )
        ).order_by(Post.created_at.desc()).paginate(
            page=page, per_page=5, error_out=False
        )
    else:
        # If no query, return empty results
        posts = Post.query.filter(Post.id == -1).paginate(
            page=1, per_page=5, error_out=False
        )
    
    return render_template('blog/search.html', title='Search Results', 
                         posts=posts, query=query)

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from blueprints.blog import bp
from models import db, Post, Comment, Like
from forms import PostForm, SearchForm, CommentForm, ReplyForm, EditCommentForm

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
    comment_form = CommentForm()
    reply_form = ReplyForm()
    comments = post.get_top_level_comments()
    return render_template('blog/post.html', title=post.title, post=post, 
                         comments=comments, comment_form=comment_form, reply_form=reply_form)

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

# Comment Routes
@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Comment error: {error}', 'error')
    
    return redirect(url_for('blog.post', id=post_id) + '#comments')

@bp.route('/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def add_reply(comment_id):
    parent_comment = Comment.query.get_or_404(comment_id)
    form = ReplyForm()
    
    if form.validate_on_submit():
        reply = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=parent_comment.post_id,
            parent_id=parent_comment.id
        )
        db.session.add(reply)
        db.session.commit()
        flash('Your reply has been added!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Reply error: {error}', 'error')
    
    return redirect(url_for('blog.post', id=parent_comment.post_id) + f'#comment-{comment_id}')

@bp.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author != current_user:
        flash('You can only edit your own comments!', 'error')
        return redirect(url_for('blog.post', id=comment.post_id))
    
    form = EditCommentForm()
    
    if form.validate_on_submit():
        comment.content = form.content.data
        comment.updated_at = db.func.now()
        db.session.commit()
        flash('Your comment has been updated!', 'success')
        return redirect(url_for('blog.post', id=comment.post_id) + f'#comment-{comment_id}')
    elif request.method == 'GET':
        form.content.data = comment.content
    
    return render_template('blog/edit_comment.html', title='Edit Comment', 
                         form=form, comment=comment)

@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author != current_user:
        flash('You can only delete your own comments!', 'error')
        return redirect(url_for('blog.post', id=comment.post_id))
    
    post_id = comment.post_id
    
    # If comment has replies, replace content with deletion message
    if comment.get_replies_count() > 0:
        comment.content = "[This comment has been deleted]"
        comment.updated_at = db.func.now()
        db.session.commit()
        flash('Your comment has been deleted!', 'success')
    else:
        # If no replies, completely remove the comment
        db.session.delete(comment)
        db.session.commit()
        flash('Your comment has been removed!', 'success')
    
    return redirect(url_for('blog.post', id=post_id) + '#comments')

# Like System Routes
@bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if current_user.has_liked_post(post):
        # Unlike the post
        current_user.unlike_post(post)
        db.session.commit()
        action = 'unliked'
        message = 'Post removed from favorites!'
    else:
        # Like the post
        current_user.like_post(post)
        db.session.commit()
        action = 'liked'
        message = 'Post added to favorites!'
    
    # Check if request is AJAX
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({
            'success': True,
            'action': action,
            'like_count': post.get_like_count(),
            'is_liked': current_user.has_liked_post(post)
        })
    
    flash(message, 'success')
    return redirect(url_for('blog.post', id=post_id))

@bp.route('/post/<int:post_id>/like-status')
def like_status(post_id):
    """API endpoint to get like status for a post"""
    post = Post.query.get_or_404(post_id)
    
    return jsonify({
        'like_count': post.get_like_count(),
        'is_liked': current_user.has_liked_post(post) if current_user.is_authenticated else False,
        'post_id': post_id
    })

@bp.route('/favorites')
@login_required
def favorites():
    """Display user's favorite posts"""
    page = request.args.get('page', 1, type=int)
    liked_posts = current_user.get_liked_posts()
    
    # Manual pagination for liked posts
    per_page = 5
    total = len(liked_posts)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_posts = liked_posts[start:end]
    
    # Create pagination info as a simple object
    from types import SimpleNamespace
    
    posts = SimpleNamespace(
        items=paginated_posts,
        page=page,
        per_page=per_page,
        total=total,
        pages=(total + per_page - 1) // per_page,
        has_prev=page > 1,
        has_next=page < (total + per_page - 1) // per_page,
        prev_num=page - 1 if page > 1 else None,
        next_num=page + 1 if page < (total + per_page - 1) // per_page else None
    )
    
    return render_template('blog/favorites.html', title='My Favorites', 
                         posts=posts, favorite_count=total)

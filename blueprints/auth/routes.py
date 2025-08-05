from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from blueprints.auth import bp
from models import db, User
from blueprints.auth.forms import LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm, DeleteAccountForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/profile')
@login_required
def profile():
    from models import Post
    post_count = current_user.posts.count()
    recent_posts = current_user.posts.order_by(Post.created_at.desc()).limit(3).all()
    return render_template('auth/profile.html', title='Profile', user=current_user, post_count=post_count, recent_posts=recent_posts)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.website = form.website.data
        current_user.avatar_url = form.avatar_url.data
        current_user.twitter_handle = form.twitter_handle.data
        current_user.linkedin_url = form.linkedin_url.data
        current_user.github_url = form.github_url.data
        current_user.profile_public = form.profile_public.data
        current_user.show_email = form.show_email.data
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('auth.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.bio.data = current_user.bio
        form.location.data = current_user.location
        form.website.data = current_user.website
        form.avatar_url.data = current_user.avatar_url
        form.twitter_handle.data = current_user.twitter_handle
        form.linkedin_url.data = current_user.linkedin_url
        form.github_url.data = current_user.github_url
        form.profile_public.data = current_user.profile_public
        form.show_email.data = current_user.show_email
    
    return render_template('auth/edit_profile.html', title='Edit Profile', form=form)

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('auth/change_password.html', title='Change Password', form=form)

@bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if (form.confirm_username.data == current_user.username and 
            current_user.check_password(form.password.data)):
            
            # Delete user's posts first
            current_user.posts.delete()
            
            # Delete the user
            db.session.delete(current_user)
            db.session.commit()
            
            flash('Your account has been deleted successfully.', 'info')
            return redirect(url_for('main.index'))
        else:
            flash('Username or password is incorrect.', 'error')
    
    return render_template('auth/delete_account.html', title='Delete Account', form=form)

@bp.route('/profile/<username>')
def public_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Check if profile is public or if it's the current user's profile
    if not user.profile_public and (not current_user.is_authenticated or current_user.id != user.id):
        flash('This profile is private.', 'error')
        return redirect(url_for('main.index'))
    
    recent_posts = user.get_recent_posts(5)
    post_count = user.get_post_count()
    
    return render_template('auth/public_profile.html', title=f'{user.full_name} - Profile', 
                         user=user, recent_posts=recent_posts, post_count=post_count)

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

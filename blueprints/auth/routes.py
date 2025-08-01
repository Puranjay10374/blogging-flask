from flask import render_template, redirect, url_for, flash
from blueprints.auth import bp

@bp.route('/login')
def login():
    return render_template('auth/login.html', title='Login')

@bp.route('/register')
def register():
    return render_template('auth/register.html', title='Register')

@bp.route('/logout')
def logout():
    return redirect(url_for('main.index'))

from flask import render_template, request, url_for, redirect, flash
from virtual_hospital import app
from virtual_hospital.models import *
from virtual_hospital.forms import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin

# User Tracking Control
login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user
login_manager.login_view = 'login'


@app.route('/')
def index():
    return render_template('index.html', currPage="Home")

@app.route('/about')
def about():
    return render_template('about.html', currPage="About")

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        if username == user.email and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return render_template('index.html', currPage="Home")

        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html', currPage="Login")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')

@app.route("/test", methods=['GET', 'POST'])
def test():
    test_form = TestForm()
    test_form.validate_on_submit()
    return render_template("test.html", form=test_form)

from flask import render_template, request, url_for, redirect, flash
from virtual_hospital import app
from virtual_hospital.models import *
from virtual_hospital.forms import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import re

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
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()
        if not user:
            # add error message showing that user not exists
            flash('User not exist.')
            return redirect(url_for('login'))

        if user and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html', currPage="Login")

@app.route('/sign_up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_confirmed = request.form['password_confirmed']

        if not re.fullmatch(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$',email):
            # add showing error message
            flash('Invalid email.')
            return render_template('sign_up.html', currPage="SignUp")

        #if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            # add showing error message
        #    flash('Invalid password.')
        #    return render_template('sign_up.html', currPage="SignUp")
        if password != password_confirmed:
            # add showing error message
            flash('Invalid confirmed password.')
            return render_template('sign_up.html', currPage="SignUp")

        newUser = User(email = email)
        newUser.set_password(password)
        db.session.add(newUser)
        db.session.commit()
        flash('New User Created.')
        print('this step')
        return redirect(url_for('login'))
    else:
        return render_template('sign_up.html', currPage="SignUp")

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

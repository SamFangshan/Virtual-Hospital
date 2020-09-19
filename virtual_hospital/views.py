from flask import render_template, request, url_for, redirect, flash
from virtual_hospital import app
from virtual_hospital.models import *
from virtual_hospital.forms import *
from flask_login import login_user, login_required, logout_user, current_user


@app.route('/')
def index():
    return render_template('index.html', currPage="Home")


@app.route('/about')
def about():
    return render_template('about.html', currPage="About")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            # add error message showing that user not exists
            error = "User does not exist"
        elif not user.validate_password(password):
            error = "Wrong password"
        else:
            flash('You were successfully logged in.')
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html', currPage="Login", error=error)

def password_error(passwd):
    SpecialSym = ['$', '@', '#', '_']
    error = ''
    if len(passwd) < 8:
        error += 'Length should be at least 8. ' + '\n'
    elif len(passwd) > 20:
        error += 'Length should be not be greater than 20. ' + '\n'

    if not any(char.isdigit() for char in passwd):
        error += 'Password should have at least one numeral. ' + '\n'

    if not any(char.isupper() for char in passwd):
        error += 'Password should have at least one uppercase letter. ' + '\n'

    if not any(char.islower() for char in passwd):
        error += 'Password should have at least one lowercase letter. ' + '\n'

    if not any(char in SpecialSym for char in passwd):
        error += 'Password should have at least one of the symbols $@#_' + '\n'

    return error.strip('\n')

@app.route('/sign_up', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_confirmed =request.form['password_confirmed']

        # check uniqueness of email
        if User.query.filter_by(email=email).first():
            error = "Already Registered"
        elif len(password_error(password))!=0:
            error = password_error(password)
        elif password != password_confirmed:
            error = "Please ensure that two password are the same."
        else:
            newUser = User(email=email)
            newUser.set_password(password)
            db.session.add(newUser)
            db.session.commit()
            flash('New User Created.')
            login_user(newUser)
            return redirect(url_for('index'))

    return render_template('sign_up.html', currPage="SignUp", error=error)


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

        user = User.query.filter_by(email=current_user.email).first()
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

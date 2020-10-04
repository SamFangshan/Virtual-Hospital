from flask import render_template, request, url_for, redirect, flash
from virtual_hospital import app
from virtual_hospital.models import *
from virtual_hospital.forms import *
from flask_login import login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO,emit

socketio = SocketIO(app)

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')
@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)
@socketio.on('image-upload')
def imageUpload(image):
    emit('send-image', image, broadcast = True)

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
            return (render_template('login.html', currPage="Login", error=error), 404)
        elif not user.validate_password(password):
            error = "Wrong password"
            return (render_template('login.html', currPage="Login", error=error), 401)
        else:
            flash('You were successfully logged in.', 'info')
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html', currPage="Login", error=error)

def password_error(passwd):
    SpecialSym = ['$', '@', '#', '_', '!']
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
        error += 'Password should have at least one of the symbols $@#_!' + '\n'

    return error.strip('\n')

@app.route('/sign_up', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        password_confirmed =request.form['password_confirmed']
        user_type = request.form['user_type']

        # check uniqueness of email
        if User.query.filter_by(email=email).first():
            error = "Already Registered"
        elif len(password_error(password))!=0:
            error = password_error(password)
            return (render_template('sign_up.html', currPage="SignUp", error=error), 500)
        elif password != password_confirmed:
            error = "Please ensure that two password are the same."
            return (render_template('sign_up.html', currPage="SignUp", error=error), 500)
        else:
            if user_type == 'patient':
                newUser = Patient(email=email, name=name)
            elif user_type == 'doctor':
                newUser = Doctor(email=email, name=name)

            newUser.set_password(password)
            db.session.add(newUser)
            db.session.commit()
            flash('New User Created.', 'info')
            login_user(newUser)
            return redirect((url_for('index')), 200)

    return (render_template('sign_up.html', currPage="SignUp", error=error), 500)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.', 'info')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_confirmed =request.form['password_confirmed']

        if current_user.email != email and User.query.filter_by(email=email).first():
            error = "Already Registered"
        elif len(password) != 0:
            if len(password_error(password))!=0:
                error = password_error(password)
            elif password != password_confirmed:
                error = "Please ensure that two password are the same."
            else:
                user = User.query.filter_by(email=current_user.email).first()
                user.email = email
                user.set_password(password)
                db.session.commit()
                flash('Settings updated.', 'info')
                return redirect(url_for('index'))
        else:
            user = User.query.filter_by(email=current_user.email).first()
            user.email = email
            db.session.commit()
            flash('Settings updated.', 'info')
            return redirect(url_for('index'))

    return render_template('settings.html', error=error)

@app.route('/setprofile', methods=['GET', 'POST'])
@login_required
def setprofile():
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number']
        nric = request.form['nric']
        gender = request.form['gender']

        if not name or len(name) > 20 or len(nric) > 10 or len(phone_number) > 20 or len(gender) > 6:
                flash('Invalid input.', 'error')
                return redirect(url_for('setprofile'))

        user = User.query.filter_by(email=current_user.email).first()
        user.name = name
        user.phone_number = phone_number
        user.nric = nric
        user.gender = gender

        if current_user.type == 'patient':
            date_of_birth = request.form['date_of_birth']
            user.date_of_birth = date_of_birth
        elif current_user.type == 'doctor':
            credentials = request.form['credentials']
            specialties = request.form['specialties']
            office_hour_start_time = request.form['office_hour_start_time']
            office_hour_end_time = request.form['office_hour_end_time']
            department_id = request.form['department_id']
            user.credentials = credentials
            user.specialties = specialties
            user.office_hour_start_time = office_hour_start_time
            user.office_hour_end_time = office_hour_end_time
            user.department_id = department_id

        db.session.commit()
        flash('Profile updated.', 'info')
        return redirect(url_for('index'))

    return render_template('setprofile.html')

@app.route("/chatroom",methods=['Get','Post'])
def chatroom():
    return render_template("chatroom.html")

@app.route("/test", methods=['GET', 'POST'])
def test():
    test_form = TestForm()
    test_form.validate_on_submit()
    return render_template("test.html", form=test_form)

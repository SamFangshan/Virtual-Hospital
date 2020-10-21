import json
import os
import re

import stripe
from sqlalchemy.orm.collections import InstrumentedList
from flask import flash, jsonify, redirect, render_template, request, url_for, session, make_response

from flask_login import current_user, login_required, login_user, logout_user
from virtual_hospital import app
from virtual_hospital.forms import *

from flask_login import login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO,emit

from datetime import datetime, timedelta
from typing import NamedTuple

from collections import defaultdict

import operator

socketio = SocketIO(app)
FINISHED = "done"

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)


@socketio.on('image-upload')
def imageUpload(json):
    print('image received')
    socketio.emit('send-image', json)


@socketio.on('connect')
def connected():
    print('connect')
@socketio.on('disconnect')
def disconnect():
    print('disconnect')

from virtual_hospital.models import *

stripe.api_key = os.environ['STRIPE_SECRET_KEY']

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
            return redirect(url_for('index'))

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
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        password_confirmed = request.form.get('password_confirmed', None)
        if current_user.email != email and User.query.filter_by(email=email).first():
            error = "Already Registered"
        elif password and len(password) != 0:
            if len(password_error(password))!=0:
                error = password_error(password)
            elif password != password_confirmed:
                error = "Please ensure that two password are the same."
            else:
                user = User.query.filter_by(email=current_user.email).first()
                user.email = current_user.email if email is None else email
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


@app.route("/chatroom/<appointment_id>",methods=['Get','Post'])
@login_required
def chatroom(appointment_id):
    prescription_given = False
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    if not appointment:
        return render_template('errors/404.html'), 404
    if appointment.status == FINISHED+'p'+FINISHED+'d' or appointment.status == FINISHED+'d'+FINISHED+'p' or appointment.status == 'cancelled':
        return render_template('errors/403.html'), 403
    appointment_time_slot = AppointmentTimeSlot.query.filter_by(id=appointment.appointment_time_slot_id).first()
    #if datetime.now() < appointment_time_slot.appointment_start_time - datetime.timedelta(minutes=15):
    #    return render_template('errors/403.html'), 403

    if current_user.type == 'doctor':
        if current_user.id != appointment_time_slot.doctor_id:
            return render_template('errors/403.html'), 403
        chatting_user = User.query.filter_by(id=appointment.patient_id).first()
        department = Department.query.filter_by(id=current_user.department_id).first()
        if request.method == 'POST':
            try:
                prescription = request.form['prescription']
                prescription_given = True
                if appointment.status == 'Scheduled':
                    appointment.status = FINISHED + 'd'
                elif FINISHED + 'd' not in appointment.status:
                    appointment.status += FINISHED + 'd'
                db.session.commit()
            except KeyError as e:
                print(e)
            if not prescription_given:
                try:
                    diagnosis = request.form['InputDiagnosis']
                    presrciption = Prescription.query.filter_by(id=appointment.prescription_id).first()
                    print(presrciption)
                    if not presrciption:
                        new_presrciption = Prescription(patient_id=chatting_user.id, doctor_id=current_user.id,
                                                        diagnosis=diagnosis, pick_up_status="no payment")
                        db.session.add(new_presrciption)
                        db.session.commit()
                        appointment.prescription_id = new_presrciption.id
                    else:
                        presrciption.diagnosis = diagnosis
                    db.session.commit()
                except KeyError:
                    assert request.form['submit']
                    presrciption = Prescription.query.filter_by(id=appointment.prescription_id).first()
                    if not presrciption:
                        presrciption = Prescription(patient_id=chatting_user.id, doctor_id=current_user.id,
                                                    diagnosis="No diagnosis", pick_up_status="no payment")
                        db.session.add(presrciption)
                        db.session.commit()
                        appointment.prescription_id = presrciption.id
                    if request.form['submit'] == "complete":
                        return redirect(url_for('prescription', prescription_id=presrciption.id))
                    elif request.form['submit'] == "complete-appointment":
                        if appointment.status == 'Scheduled':
                            appointment.status = FINISHED + 'd'
                        elif FINISHED + 'd' not in appointment.status:
                            appointment.status += FINISHED + 'd'
                        db.session.commit()
                        return redirect(url_for('index'))

        return render_template("chatroom.html", appointment_id=appointment_id, chatting_user=chatting_user,
                               department=department, prescription_given=prescription_given)
    elif current_user.type == 'patient':
        if appointment.patient_id != current_user.id:
            return render_template('errors/403.html'), 403
        if request.method == 'POST':
            if appointment.status == 'Scheduled':
                appointment.status = FINISHED + 'p'
            elif FINISHED+'p' not in appointment.status:
                appointment.status += FINISHED + 'p'
            db.session.commit()
            presrciption = Prescription.query.filter_by(id=appointment.prescription_id).first()
            if not presrciption:
                flash('You have finished the appointment and there is no prescription from the doctor side.', 'info')
                return redirect(url_for('index'))
            return redirect(url_for('payment', prescription_id=presrciption.id))
        chatting_user = User.query.filter_by(id=appointment_time_slot.doctor_id).first()
        department = Department.query.filter_by(id=chatting_user.department_id).first()
        print(prescription_given)
        return render_template("chatroom.html", appointment_id=appointment_id, chatting_user=chatting_user,
                               department=department, prescription_given=prescription_given)

@app.route("/prescription/<prescription_id>",methods=['Get','Post'])
@login_required
def prescription(prescription_id):
    prescription = Prescription.query.filter_by(id=prescription_id).first()
    patient = User.query.filter_by(id=prescription.patient_id).first()
    drugs = Drug.query.order_by(Drug.category).all()
    categories = defaultdict(list)
    given_drug_id = PrescriptionDrug.query.filter_by(prescription_id=prescription_id).all()
    given_drug = []
    prescription_drug_count = defaultdict(int)
    for drug_id in given_drug_id:
        given_drug.append(Drug.query.filter_by(id=drug_id.drug_id).first())
        prescription_drug_count[drug_id.drug_id] = drug_id.count
    title = ""

    if len(title) == 0:
        for drug in drugs:
            categories[drug.category].append(drug)

    if request.method == 'POST':
        post_item = next(request.form.keys())
        if post_item == 'selected_drug':
            request_value = request.form['selected_drug']
            drug_info = re.split(r' - | : ', request_value)
            drug = Drug.query.filter_by(name=drug_info[0], category=drug_info[2]).first()

            exist_prescription = PrescriptionDrug.query.filter_by(prescription_id=prescription_id, drug_id=drug.id).first()
            if exist_prescription:
                exist_prescription.count += 1
                prescription_drug_count[exist_prescription.drug_id] = exist_prescription.count
            else:
                new_added_drug = PrescriptionDrug(prescription_id=prescription_id, drug_id=drug.id, count=1)
                db.session.add(new_added_drug)
                given_drug.append(Drug.query.filter_by(id=new_added_drug.drug_id).first())
                prescription_drug_count[new_added_drug.drug_id] = new_added_drug.count
            for drug in drugs:
                categories[drug.category].append(drug)
            db.session.commit()

        elif post_item == 'added_drug':
            request_value = request.form['added_drug']
            drug_info = re.split(r' - | : ', request_value)
            drug = Drug.query.filter_by(name=drug_info[0], category=drug_info[2]).first()
            try:
                PrescriptionDrug.query.filter_by(prescription_id=prescription_id, drug_id=drug.id).delete()
                given_drug.remove(Drug.query.filter_by(id=drug.id).first())
                del prescription_drug_count[drug.drug_id]
            except :
                pass
            finally:
                db.session.commit()
                for drug in drugs:
                    categories[drug.category].append(drug)
        elif post_item == 'search_drug':
            title = request.form['search_drug']
            if len(title) > 0:
                drugs = Drug.query.filter(Drug.category.ilike("%" + title + "%")).all()
                for drug in drugs:
                    categories[drug.category].append(drug)
                drugs = Drug.query.filter(Drug.name.ilike("%" + title + "%")).all()
            else:
                for drug in drugs:
                    categories[drug.category].append(drug)

    categories = dict(sorted(categories.items(), key=lambda x: x[0]))
    total_price = sum([drug.price for drug in given_drug]) if len(given_drug) > 0 else 0

    appointment = Appointment.query.filter_by(prescription_id=prescription_id).first()
    return render_template("presrciption.html", title=title, prescription_id=prescription_id, patient=patient,
                           prescription=prescription, drugs=drugs, categories=categories, given_drug=given_drug,
                           total_price=total_price, prescription_drug_count=prescription_drug_count,
                           appointment_id=appointment.id)

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        text = request.form['title']
        if text:
            return redirect(url_for('search', title=text))
        else:
            return redirect(url_for('search', title=None))
    if request.values.__contains__("title"):
        text = request.values["title"]
        doctors = Doctor.query.filter(Doctor.name.ilike("%" + text + "%")).all()
        return (render_template('search.html', search=text, doctors=doctors), 200)
    else:
        return render_template('search.html', search="", doctors=None)

@app.route("/departments")
@login_required
def departments():
    depts = Department.query.order_by(Department.name).all()
    return render_template('departments.html', departments=depts)

@app.route("/department/<id>")
@login_required
def department(id):
    if id.isdigit():
        dept = Department.query.filter_by(id=id).all()
    else:
        return render_template('errors/404.html')
    if dept:
        doctors = Doctor.query.filter_by(department_id=id).all()
        return render_template('department.html', department=dept[0], doctors=doctors)
    else:
        return render_template('errors/404.html')


@app.route("/test", methods=['GET', 'POST'])
def test():
    test_form = TestForm()
    test_form.validate_on_submit()
    return render_template("test.html", form=test_form)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    if request.method == 'POST':
        try:
            session['prescription_id']
        except Exception:
            return render_template('errors/403.html'), 403
        amount = int(round(float(request.form['amount']), 2) * 100)
        response = make_response(render_template('checkout.html', amount=amount, publishable_key=os.environ['STRIPE_PUBLISHABLE_KEY']))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response


@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = json.loads(request.data)
        intent = stripe.PaymentIntent.create(
            amount=int(data['amount']),
            currency='sgd'
        )

        return jsonify({
          'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/payment-success/<payment_intent_id>')
@login_required
def payment_success(payment_intent_id):
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    except Exception:
        return render_template('errors/404.html'), 404
    if intent.status == 'succeeded':
        appointment_id = session['appointment_id']
        del session['appointment_id']

        prescription_id = session['prescription_id']
        del session['prescription_id']
        prescription = Prescription.query.get(int(prescription_id))
        prescription.pick_up_status = 'pending'

        # pickup on the next week day
        pickup_date = datetime.today() + timedelta(days=1)
        if pickup_date.weekday() == 5:
            pickup_date += timedelta(days=2)
        elif pickup_date.weekday() == 6:
            pickup_date += timedelta(days=1)
        prescription.pick_up_start_date = pickup_date
        db.session.commit()

        return redirect(url_for('rate_doctor', appointment_id=appointment_id))
    else:
        return render_template('errors/403.html'), 403


@app.route('/payment/prescription/<prescription_id>', methods=['POST', 'GET'])
@login_required
def payment(prescription_id):
    prescription = Prescription.query.get(int(prescription_id))

    if request.method == 'POST':
        prescription.pick_up_location = request.form['location']
        db.session.commit()

    if not prescription:
        return render_template('errors/404.html'), 404
    appointment = Appointment.query.filter_by(prescription_id=prescription.id).first()
    if current_user.type == 'doctor' or appointment.patient_id != current_user.id:
        return render_template('errors/403.html'), 403
    if prescription.pick_up_status != 'no payment':  # this payment has already been completed
        return render_template('errors/404.html'), 404

    total_price = 0
    drugs = prescription.drugs
    for drug in drugs:
        total_price += drug.price
    appointment_time_slot = AppointmentTimeSlot.query.get(appointment.appointment_time_slot_id)
    doctor = Doctor.query.get(appointment_time_slot.doctor_id)
    department = Department.query.get(doctor.department_id)

    pick_up_location = prescription.pick_up_location

    session['appointment_id'] = appointment.id
    session['prescription_id'] = prescription_id
    return render_template('payment.html', doctor=doctor, department=department,
                           drugs=drugs, total_price=total_price, appointment_time_slot=appointment_time_slot,
                           pick_up_location=pick_up_location)


@app.route('/ratedoctor/appointment/<appointment_id>', methods=['GET', 'POST'])
@login_required
def rate_doctor(appointment_id):
    appointment = Appointment.query.get(int(appointment_id))
    if not appointment:
        return render_template('errors/404.html'), 404
    if current_user.type == 'doctor' or appointment.patient_id != current_user.id:
        return render_template('errors/403.html'), 403
    if appointment.rating != None:  # this rating has already been completed
        return render_template('errors/404.html'), 404

    if request.method == 'POST':
        appointment = Appointment.query.get(int(appointment_id))
        appointment.rating = int(request.form['rate'])
        db.session.commit()
        return redirect(url_for('index'))
    appointment = Appointment.query.get(int(appointment_id))
    appointment_time_slot = AppointmentTimeSlot.query.get(appointment.appointment_time_slot_id)
    doctor = Doctor.query.get(appointment_time_slot.doctor_id)
    department = Department.query.get(doctor.department_id)
    return render_template('ratedoctor.html',
                           doctor=doctor,
                           department=department,
                           appointment_time_slot=appointment_time_slot)

class AptUser(NamedTuple):
    aptTS: AppointmentTimeSlot
    user: User # user refers to the user that the currently logged on user will see (e.g. patient will see doctor info)
    apt: Appointment
    prescpt: Prescription

@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    id = current_user.id
    user = User.query.filter_by(id=id).first()
    if current_user.type == 'doctor': # user is a doctor, can fetch time slot directly
        apptTimeSlot = AppointmentTimeSlot.query.filter_by(doctor_id=id).all()
    elif current_user.type == 'patient': # user is a patient, need to fetch all appointments, then all corresponding time slots
        apptTimeSlot = []
        apptSlot = Appointment.query.filter_by(patient_id=id).all()
        for a in apptSlot:
                slot = AppointmentTimeSlot.query.filter_by(id=a.appointment_time_slot_id).first()
                if (slot is not None) and (slot not in apptTimeSlot):
                    apptTimeSlot.append(slot)

    canEnterChat = []
    todayAppt = []
    futureAppt = []
    pastAppt = []

    for appt in apptTimeSlot:
        exe = 0

        if (datetime.now().date() == appt.appointment_start_time.date()): #today's appt (cannot enter chatroom)
            exe = 1

        if(datetime.now() > appt.appointment_start_time): #past appt (date & time)
            exe = 4

        if (datetime.now() <= (appt.appointment_start_time + timedelta(minutes=15)) and (datetime.now() >= (appt.appointment_start_time - timedelta(minutes=15)))): # +/- 15 minutes of appointment_start_time
            exe = 2

        if(datetime.now().date() < appt.appointment_start_time.date()): #future dates appt
            exe = 3

        u = None
        fetchapt = Appointment.query.filter_by(appointment_time_slot_id=appt.id).all()

        for apt in fetchapt:
            if current_user.type == 'patient':
                u = User.query.filter_by(id=appt.doctor_id).first()
            elif current_user.type == 'doctor':
                u = User.query.filter_by(id=apt.patient_id).first()

            prescr = Prescription.query.filter_by(id=apt.prescription_id).first()

            if u is not None:
                d = AptUser(appt, u, apt, prescr)
                if exe == 1:
                    todayAppt.append(d)
                elif exe == 2:
                    if (d.apt.status == 'finished') or (d.apt.status == FINISHED+'p'+FINISHED+'d' or d.apt.status == FINISHED+'d'+FINISHED+'p' or d.apt.status == 'cancelled'):
                        pastAppt.append(d)
                    else:
                        canEnterChat.append(d)
                elif exe == 3:
                    futureAppt.append(d)
                elif exe == 4:
                    pastAppt.append(d)

    todayAppt.sort(key=operator.attrgetter('aptTS.appointment_start_time'))
    futureAppt.sort(key=operator.attrgetter('aptTS.appointment_start_time'))
    pastAppt.sort(key=operator.attrgetter('aptTS.appointment_start_time'), reverse=True) # most recent on top

    futureApptDates = {apt.aptTS.appointment_start_time.date() for apt in futureAppt}
    pastApptDates = {apt.aptTS.appointment_start_time.date() for apt in pastAppt}

    if request.method =='POST':
        if user is None:
            return render_template("errors/404.html")
        else:
            print(request.form)
            deleteApptId = request.form['appt_id']
            deleteApptSlot = Appointment.query.filter_by(id=deleteApptId).delete()
            db.session.commit()
            flash('Appointment deleted.', 'info')
            return redirect(url_for('appointments'))

    if request.method == 'GET':
        if user is None:
            return render_template("errors/404.html")
        else:
            return render_template('appointments.html', currPage='Appointments', user=user, todayAppt=todayAppt, canEnterChat=canEnterChat, futureAppt=futureAppt, pastAppt=pastAppt, futureApptDates=futureApptDates, pastApptDates=sorted(pastApptDates, reverse=True))

@app.route('/newappointment', methods=['POST', 'GET'])
@login_required
def newappointment():
    doctor_id = request.args.get('doctor_id')
    doctor = User.query.filter_by(id=doctor_id).first()
    if doctor is None:
        return render_template("errors/404.html")

    current_Datetime = datetime.now()
    selected_date = request.args.get('date')
    if (selected_date is not None) and (selected_date != str(current_Datetime.date())):
        info = selected_date.split('-', 2)
        year = info[0]
        month = info[1]
        day = info[2]
        current_Datetime = datetime(int(year), int(month), int(day));

    time_slot_data_today = []
    time_slot_data = AppointmentTimeSlot.query.filter_by(doctor_id=doctor_id).all()

    for data in time_slot_data:
        if (current_Datetime < data.appointment_start_time) and (data.number_of_vacancies > 0) and (current_Datetime.date() == data.appointment_start_time.date()):
            time_slot_data_today.append(data)

    if request.method == 'GET':
        return render_template('newappointment.html', date=current_Datetime.date(), error=None, doctor=doctor, currPage='Book an Appointment', time_slot_data_today = time_slot_data_today)

    elif request.method == 'POST':
        appointment_time_slot_id = request.form['appointment_time_slot_id']
        doctor_id = request.form['doctor_id']
        if appointment_time_slot_id == "0":
            return render_template('newappointment.html', date=current_Datetime.date(), error="Invalid selections! Please try again.", doctor=doctor, currPage='Book an Appointment', time_slot_data_today = time_slot_data_today)
        else:
            appointmentSlot = AppointmentTimeSlot.query.filter_by(id=appointment_time_slot_id).first()
            appointmentCount = Appointment.query.filter_by(appointment_time_slot_id=appointment_time_slot_id).count()
            if appointmentCount < int(appointmentSlot.number_of_vacancies):
                apt = Appointment(patient_id=current_user.id, status="Scheduled", queue_number=(appointmentCount+1), appointment_time_slot_id=appointment_time_slot_id)
                db.session.add(apt)
                db.session.commit()
                flash('Appointment booked.', 'info')
                return redirect(url_for('appointments'))
            else:
                return render_template('newappointment.html', date=current_Datetime.date(), error="Sorry, this timeslot has been fully booked.", doctor=doctor, currPage='Book an Appointment', time_slot_data_today = time_slot_data_today)

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    if request.method == 'GET':
        id = request.args.get('id')
        user = User.query.filter_by(id=id).first()
        if user is None:
            return render_template("errors/404.html")
        else:
            if user.type == 'patient':
                if current_user.type == 'doctor' or current_user.id == user.id:
                    return render_template('patientprofile.html', user=user, current_user=current_user, currPage="Patient's Profile")
                else:
                    return render_template('errors/403.html'), 403

        dept = Department.query.filter_by(id=user.department_id).first()
        return render_template('doctorprofile.html', user=user, dept=dept, currPage="Doctor's Profile")

@app.route('/forceapt', methods=['GET'])
def forceapt():
    if request.method == 'GET':
        patient_id = request.args.get('pid')
        doctor_id = request.args.get('did')

        if (patient_id is None or doctor_id is None):
            flash('Error: no patient or doctor id.', 'error')
        else:
            today = datetime.today()
            end = today + timedelta(minutes=180)
            '''Create time slot'''
            time_slot = AppointmentTimeSlot(appointment_start_time=today,
                                            appointment_end_time=end,
                                            number_of_vacancies=2,
                                            doctor_id=doctor_id)
            db.session.add(time_slot)
            db.session.flush()
            apt = Appointment(patient_id=patient_id, status="Scheduled", queue_number=1, appointment_time_slot_id=time_slot.id)
            db.session.add(apt)
            db.session.commit()
            flash('Appointment booked.', 'info')
            return redirect(url_for('appointments'))

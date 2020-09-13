from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from flask_login import UserMixin
from virtual_hospital import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True)
    phone_number = db.Column(db.String(20))
    nric = db.Column(db.String(10))
    gender = db.Column(db.String(6))
    type = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Patient(User):
    date_of_birth = db.Column(db.Date)

    __mapper_args__ = {
        'polymorphic_identity': 'patient',
    }


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    doctors = db.relationship('Doctor', lazy='select',
                              backref=db.backref('department', lazy='joined'))


class Doctor(User):
    credentials = db.Column(db.String(200))
    specialties = db.Column(db.ARRAY(db.String(100)))
    office_hour_start_time = db.Column(db.String(10))
    office_hour_end_time = db.Column(db.String(10))
    department_id = db.Column(db.Integer, db.ForeignKey(Department.id), nullable=True)
    appointment_time_slots = db.relationship('AppointmentTimeSlot', lazy='select',
                                             backref=db.backref('doctor', lazy='joined'))

    __mapper_args__ = {
        'polymorphic_identity': 'doctor',
    }


class AppointmentTimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_start_time = db.Column(db.DateTime, nullable=False)
    appointment_end_time = db.Column(db.DateTime, nullable=False)
    number_of_vacancies = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey(Doctor.id), nullable=False)
    appointments = db.relationship('Appointment', lazy='select',
                                   backref=db.backref('appointment_time_slot', lazy='joined'))


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey(Patient.id), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    queue_number = db.Column(db.Integer)
    appointment_time_slot_id = db.Column(db.Integer, db.ForeignKey(AppointmentTimeSlot.id), nullable=False)
    rating = db.Column(db.Float)


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey(Patient.id), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey(Doctor.id), nullable=False)

    pick_up_start_date = db.Column(db.Date, nullable=False)
    pick_up_status = db.Column(db.String(10), nullable=False)
    medicines = db.Column(db.ARRAY(db.String(100)))
    prescription_instructions = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    drugs = db.relationship('Drug', secondary='prescription_drugs')


class Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)


class Prescription_Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey(Prescription.id), nullable=False)
    drug_id = db.Column(db.Integer, db.ForeignKey(Drug.id), nullable=False)

    prescription = db.relationship(Prescription, backref=db.backref('prescription_drugs'))
    drug = db.relationship(Drug, backref=db.backref('prescription_drugs'))

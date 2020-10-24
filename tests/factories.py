from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Factory as FakeFactory
from virtual_hospital import db
from virtual_hospital.models import *

faker = FakeFactory.create()


class DoctorFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x + 1)
    name = factory.Faker('name')
    password_hash = generate_password_hash('password')
    email = factory.LazyAttribute(lambda x: '{}.{}@example.com'.format(
                                                                       x.name.split()[0],
                                                                       x.name.split()[1]).lower()
                                                                       )
    specialties = "Dermatology"
    office_hour_start_time = factory.LazyAttribute(
        lambda x: ['08:30', None, '09:00'][(x.id - 1) % 3])
    office_hour_end_time = factory.LazyAttribute(
        lambda x: ['18:00', None, '19:00'][(x.id - 1) % 3])
    # office_hour_start_time = factory.Sequence(
    #     lambda x: ['08:30', None, '09:00'][x % 3])
    # office_hour_end_time = factory.Sequence(
    #     lambda x: ['18:00', None, '19:00'][x % 3])
    # department_id = 1

    class Meta:
        model = Doctor
        sqlalchemy_session = db.session


# class DepartmentFactoryForRateDoctor(SQLAlchemyModelFactory):
#     id = factory.Sequence(lambda x: x + 1)
#     name = 'Anaesthesia'
#     description = 'no description'
#
#     class Meta:
#         model = Department
#         sqlalchemy_session = db.session


class PatientFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x + 1 + 100)
    name = factory.Faker('name')
    password_hash = generate_password_hash('password')
    email = factory.LazyAttribute(lambda x: '{}.{}@example.com'.format(
                                                                       x.name.split()[0],
                                                                       x.name.split()[1]).lower()
                                                                       )

    class Meta:
        model = Patient
        sqlalchemy_session = db.session


class PrescriptionFactoryForPayment(SQLAlchemyModelFactory):
    id = 1
    patient_id = 101
    doctor_id = 1
    pick_up_start_date = datetime.today().date()
    pick_up_status = 'no payment'
    diagnosis = 'cold'
    created_at = datetime.now()

    class Meta:
        model = Prescription
        sqlalchemy_session = db.session

class AppointmentFactoryForPayment(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x + 1)
    patient_id = 101
    status = "Scheduled"
    queue_number = 1
    appointment_time_slot_id = 1
    # rating = 4.0
    prescription_id = factory.Sequence(lambda x: x + 1)

    class Meta:
        model = Appointment
        sqlalchemy_session = db.session

class PrescriptionFactoryPaid(SQLAlchemyModelFactory):
    id = 2
    patient_id = 101
    doctor_id = 1
    pick_up_start_date = datetime.today().date()
    pick_up_status = 'pending'
    diagnosis = 'cold'
    created_at = datetime.now()

    class Meta:
        model = Prescription
        sqlalchemy_session = db.session


class DrugFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x + 1)
    name = factory.LazyAttribute(lambda x: ['Apomorphine', 'Cupric Sulfate', 'Ipecac'][(x.id - 1) % 3])
    price = factory.LazyAttribute(lambda x: [26, 18.5, 30.5][(x.id - 1) % 3])
    category = 'Emetics'

    class Meta:
        model = Drug
        sqlalchemy_session = db.session


class PrescriptionDrugFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x + 1)
    prescription_id = 1
    drug_id = factory.LazyAttribute(lambda x: [1, 2, 3][(x.id - 1) % 3])
    count = 1

    class Meta:
        model = PrescriptionDrug
        sqlalchemy_session = db.session


class AppointmentTimeSlotFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x + 1)
    appointment_start_time = datetime.now()
    appointment_end_time = factory.LazyAttribute(
        lambda x: x.appointment_start_time + timedelta(minutes=30))
    number_of_vacancies = 2
    doctor_id = factory.Sequence(lambda x: x + 1)

    class Meta:
        model = AppointmentTimeSlot
        sqlalchemy_session = db.session

class TestUserFactory(SQLAlchemyModelFactory):
    id = 10001
    name = "test_user"
    password_hash = generate_password_hash('password')
    email = "test_user@gmail.com"

    class Meta:
        model = Patient
        sqlalchemy_session = db.session

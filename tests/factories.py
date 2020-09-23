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

    office_hour_start_time = factory.LazyAttribute(
        lambda x: ['08:30', None, '09:00'][(x.id - 1) % 3])
    office_hour_end_time = factory.LazyAttribute(
        lambda x: ['18:00', None, '19:00'][(x.id - 1) % 3])
    # office_hour_start_time = factory.Sequence(
    #     lambda x: ['08:30', None, '09:00'][x % 3])
    # office_hour_end_time = factory.Sequence(
    #     lambda x: ['18:00', None, '19:00'][x % 3])

    class Meta:
        model = Doctor
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

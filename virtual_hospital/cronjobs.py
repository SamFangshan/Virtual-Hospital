import datetime

from virtual_hospital.utils.time_slot_utils import *
from virtual_hospital import crontab, db
from virtual_hospital.models import Doctor, AppointmentTimeSlot


@crontab.job(minute='0', hour='0', day='*', month='*', day_of_week='1')  # At 00:00 on Monday
def generate_time_slots():
    doctors = Doctor.query.all()
    today = datetime.datetime.today().date()
    dates = get_dates_of_current_and_next_weeks(today)
    for doctor in doctors:
        for date in dates:
            if not time_slots_exist(doctor.id, date):
                time_slots = generate_time_slots_for_a_day(date,
                                                           doctor.office_hour_start_time,
                                                           doctor.office_hour_end_time)
                for ts in time_slots:
                    time_slot = AppointmentTimeSlot(appointment_start_time=ts[0],
                                                    appointment_end_time=ts[1],
                                                    number_of_vacancies=2,
                                                    doctor_id=doctor.id)
                    db.session.add(time_slot)
                db.session.commit()

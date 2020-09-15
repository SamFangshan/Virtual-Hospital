from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, ValidationError

from virtual_hospital.models import User

class TestForm(FlaskForm):
    """ Test form"""
    email = StringField('email_label', validators=[InputRequired(message="Email required")])
    check_button = SubmitField('Check')

    def validate_email(self, email):
        user_object = User.query.filter_by(email=email.data).first()
        if user_object:
            raise ValidationError("Email exists")
        else:
            raise ValidationError("Email does not exist")

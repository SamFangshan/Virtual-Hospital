from flask import render_template
from virtual_hospital import app
from virtual_hospital.models import *


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

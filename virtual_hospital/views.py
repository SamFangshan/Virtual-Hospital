from flask import Flask, render_template
from virtual_hospital import app
from virtual_hospital.models import *
from virtual_hospital.forms import *

@app.route('/')
def index():
    return render_template('index.html', currPage="Home")

@app.route('/about')
def about():
    return render_template('about.html', currPage="About")

@app.route("/test", methods=['GET', 'POST'])
def test():
    test_form = TestForm()
    test_form.validate_on_submit()
    return render_template("test.html", form=test_form)

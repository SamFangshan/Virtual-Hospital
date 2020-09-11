from flask import render_template
from virtual_hospital import app


@app.route('/')
def index():
    return render_template('index.html', currPage="Home")
    
@app.route('/about')
def about():
    return render_template('about.html', currPage="About")
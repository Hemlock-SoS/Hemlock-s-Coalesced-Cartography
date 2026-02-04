from flask import render_template, redirect, url_for
from app import app
from app.forms import NewWorldForm

@app.route('/')
@app.route('/index')
def index():
    worlds = [
        { 'name': 'Vrioska'},
        { 'name': 'Avalon'},
        { 'name': 'Equinox'}
        ]
    return render_template('index.html', worlds=worlds)

@app.route('/new-world', methods=['GET', 'POST'])
def new_world():
    form = NewWorldForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('new-world.html', title = "Create world", form=form)
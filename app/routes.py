from flask import render_template, redirect, url_for
from app import app, db
from app.forms import NewWorldForm
import sqlalchemy as sa
from app.models import World

@app.route('/')
@app.route('/index')
def index():
    worlds = db.session.scalars(
        sa.select(World).order_by(World.created.desc())
    ).all()
    print(worlds)
    return render_template('index.html', worlds=worlds)

@app.route('/new-world', methods=['GET', 'POST'])
def new_world():
    form = NewWorldForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('new-world.html', title = "Create world", form=form)
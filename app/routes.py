from flask import render_template, flash, url_for, make_response
from app import app, db
from app.forms import NewWorldForm
import sqlalchemy as sa
from app.models import World
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timezone

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
        # Handle thumbnail upload
        thumbnail_path = 'images/default.png'  # Default value
        
        if form.thumbnail.data:
            file = form.thumbnail.data
            filename = secure_filename(file.filename)
            
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            unique_filename = f"{timestamp}_{name}{ext}"
            
            upload_dir = os.path.join(app.root_path, 'static', 'user_data')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            thumbnail_path = f'user_data/{unique_filename}'
        
        world = World(
            name=form.worldName.data,
            thumbnail_path=thumbnail_path,
            info=form.worldInfo.data
        )
        db.session.add(world)
        db.session.commit()
        flash('World created')
        response = make_response('', 204)
        response.headers['HX-Redirect'] = url_for('index')
        return response
    return render_template('new-world.html', title="Create world", form=form)

@app.route('/world/<id>')
def display_world(id):
    world = db.first_or_404(sa.select(World).where(World.id == id))
    return render_template('world.html', world=world)
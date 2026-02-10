from flask import render_template, flash, url_for, make_response, request
from app import app, db
from app.forms import NewWorldForm, UpdateWorldForm
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
        thumbnail_path = 'images/default.png'
        
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

@app.route('/update-world/<id>', methods=['GET', 'POST'])
def update_world(id):
    form = UpdateWorldForm()
    world = db.session.query(World).filter(World.id == id).first()
    if form.validate_on_submit():
        changes = False
        if form.worldName.data and form.worldName.data != world.name:
            world.name = form.worldName.data
            changes = True
        if form.thumbnail.data:
            file = form.thumbnail.data
            filename = secure_filename(file.filename)
            
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            unique_filename = f"{timestamp}_{name}{ext}"
            
            upload_dir = os.path.join(app.root_path, 'static', 'user_data')
            os.makedirs(upload_dir, exist_ok=True)
            
            if world.thumbnail_path != 'images/default.png':
                old_file_path = os.path.join(app.root_path, 'static', world.thumbnail_path)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
        
            world.thumbnail_path = f'user_data/{unique_filename}'
            changes = True
        if form.worldInfo.data and form.worldInfo.data != world.info:
            world.info = form.worldInfo.data
            changes = True

        if changes:
            db.session.commit()
            print(world.thumbnail_path)
            flash('World updated')
        else:
            flash('No changes made')
        response = make_response('', 204)
        response.headers['HX-Redirect'] = url_for('display_world', id=id)
        return response
    return render_template('update-world.html', title='Update world',id=id, form=form)
        




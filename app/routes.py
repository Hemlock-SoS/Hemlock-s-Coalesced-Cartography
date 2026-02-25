from flask import render_template, flash, redirect, url_for, request, make_response
from app import app, db
from app.forms import NewWorldForm, UpdateWorldForm, UploadMapForm
from app.models import World, Map
import sqlalchemy as sa
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import os

@app.route('/')
@app.route('/index')
def index():
    worlds = db.session.scalars(
        sa.select(World).order_by(World.created.desc())
    ).all()
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
            info=form.worldInfo.data if form.worldInfo.data else None
        )
        db.session.add(world)
        db.session.flush()
        
        if form.primaryMap.data:
            file = form.primaryMap.data
            filename = secure_filename(file.filename)
            
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            unique_filename = f"{timestamp}_{name}{ext}"
            
            upload_dir = os.path.join(app.root_path, 'static', 'user_data')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            primary_map = Map(
                world_id=world.id,
                body_path=f'user_data/{unique_filename}'
            )
            db.session.add(primary_map)
            db.session.flush()
            
            world.primary_map_id = primary_map.id
        
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
    
    if not world:
        flash('World not found')
        return redirect(url_for('index'))
    
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
        
        if form.worldInfo.data is not None and form.worldInfo.data != world.info:
            world.info = form.worldInfo.data
            changes = True
        
        if form.primaryMap.data:
            file = form.primaryMap.data
            filename = secure_filename(file.filename)
            
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            unique_filename = f"{timestamp}_{name}{ext}"
            
            upload_dir = os.path.join(app.root_path, 'static', 'user_data')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            if world.primary_map_id is not None:
                old_primary_map = db.session.get(Map, world.primary_map_id)
                if old_primary_map:
                    old_map_file = os.path.join(app.root_path, 'static', old_primary_map.body_path)
                    if os.path.exists(old_map_file):
                        os.remove(old_map_file)
                    db.session.delete(old_primary_map)
            
            new_primary_map = Map(
                world_id=world.id,
                body_path=f'user_data/{unique_filename}'
            )
            db.session.add(new_primary_map)
            db.session.flush()
            
            world.primary_map_id = new_primary_map.id
            changes = True
        
        if changes:
            db.session.commit()
            flash('World updated successfully')
        else:
            flash('No changes made')
        
        response = make_response('', 204)
        response.headers['HX-Redirect'] = url_for('display_world', id=id)
        return response
    return render_template('update-world.html', title='Update world', form=form, id=id, world=world)

@app.route('/world/<world_id>/delete', methods=['POST'])
def delete_world(world_id):
    world = db.first_or_404(sa.select(World).where(World.id == world_id))
    db.session.delete(world)
    db.session.commit()

    flash('{{world.name}} successfully deleted')
    return index()



@app.route('/world/<world_id>/upload-map', methods=['GET', 'POST'])
def upload_map(world_id):
    form = UploadMapForm()
    world = db.first_or_404(sa.select(World).where(World.id == world_id))
    
    if form.validate_on_submit():
        file = form.mapFile.data
        filename = secure_filename(file.filename)
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        unique_filename = f"{timestamp}_{name}{ext}"
        
        upload_dir = os.path.join(app.root_path, 'static', 'user_data')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        new_map = Map(
            name=form.mapName.data if form.mapName.data else None,
            body_path=f'user_data/{unique_filename}'
        )
        world.maps.append(new_map)
        db.session.flush()
        
        if world.primary_map_id is None:
            world.primary_map_id = new_map.id
        elif form.set_as_primary.data:
            world.primary_map_id = new_map.id
        
        db.session.commit()
        flash('Map uploaded successfully')
        response = make_response('', 204)
        response.headers['HX-Redirect'] = url_for('display_world', id=world_id)
        return response
    
    return render_template('upload-map.html', title='Upload Map', form=form, world_id=world_id)

@app.route('/map/<int:map_id>/edit', methods=['GET', 'POST'])
def edit_map(map_id):
    """Edit map name and primary status"""
    from app.forms import EditMapForm 
    
    map_obj = db.first_or_404(sa.select(Map).where(Map.id == map_id))
    world = db.first_or_404(sa.select(World).where(World.id == map_obj.world_id))
    
    form = EditMapForm()
    
    if form.validate_on_submit():
        map_obj.name = form.name.data.strip() if form.name.data else None
        
        if form.set_as_primary.data:
            world.primary_map_id = map_id
        
        db.session.commit()
        flash('Map updated successfully')
        response = make_response('', 204)
        response.headers['HX-Redirect'] = url_for('display_world', id=world.id)
        return response
    
    if request.method == 'GET':
        form.name.data = map_obj.name
        form.set_as_primary.data = (world.primary_map_id == map_id)
    
    return render_template('edit-map.html', form=form, map=map_obj, world=world)

@app.route('/map/<map_id>')
def get_map(map_id):
    map_obj = db.first_or_404(sa.select(Map).where(Map.id == map_id))
    return f'''<img src="{url_for('static', filename=map_obj.body_path)}" 
                    alt="{map_obj.name or 'Map'}" 
                    style="max-width: 100%; max-height: 100%; object-fit: contain;">'''

@app.route('/map/<int:map_id>/delete', methods=['POST'])
def delete_map(map_id):
    map_obj = db.first_or_404(sa.select(Map).where(Map.id == map_id))
    world = db.first_or_404(sa.select(World).where(World.id == map_obj.world_id))
    
    if world.primary_map_id == map_id:
        world.primary_map_id = None
    
    map_file_path = os.path.join(app.root_path, 'static', map_obj.body_path)
    if os.path.exists(map_file_path):
        os.remove(map_file_path)
    
    db.session.delete(map_obj)
    db.session.commit()
    
    flash('Map deleted successfully')
    response = make_response('', 204)
    response.headers['HX-Redirect'] = url_for('display_world', id=world.id)
    return response
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_wtf.file import FileField, FileAllowed
import sqlalchemy as sa
from app import db
from app.models import World

class NewWorldForm(FlaskForm):
    worldName = StringField('World name', validators=[DataRequired()])
    thumbnail = FileField('Thumbnail Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    worldInfo = TextAreaField('World info', validators=[Length(min=0, max=140)])
    primaryMap = FileField('Primary Map (Optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    submit = SubmitField('Create')

    def validate_worldName(self, worldName):
        world = db.session.scalar(
            sa.select(World).where(
                World.name == worldName.data
            )
        )
        if world is not None:
            raise ValidationError('World already exists')

class UpdateWorldForm(FlaskForm):
    worldName = StringField('World name', validators=[Length(min=0, max=140)])
    thumbnail = FileField('Thumbnail Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    worldInfo = TextAreaField('World info', validators=[Length(min=0, max=140)])
    primaryMap = FileField('Primary Map', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    submit = SubmitField('Update')

class UploadMapForm(FlaskForm):
    mapName = StringField('Map name (Optional)', validators=[Length(min=0, max=64)])
    mapFile = FileField('Map Image', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    set_as_primary = BooleanField('Primary?')
    submit = SubmitField('Upload Map')
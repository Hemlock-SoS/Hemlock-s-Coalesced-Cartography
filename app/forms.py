from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length
import sqlalchemy as sa
from app import db
from app.models import World

class NewWorldForm(FlaskForm):
    worldName = StringField('World name', validators=[DataRequired()])
    thumbnail = FileField('Thumbnail Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    worldInfo = TextAreaField('World info', validators=[Length(min=0, max=140)])
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
    submit = SubmitField('Update')
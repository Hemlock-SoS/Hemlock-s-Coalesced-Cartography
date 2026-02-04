from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
import sqlalchemy as sa
from app import db
from app.models import World

class NewWorldForm(FlaskForm):
    worldName = StringField('World name', validators=[DataRequired()])
    submit = SubmitField('Create')

    def validate_name(self, new_name):
        world = db.session.scalar(
            sa.select(World).where(
                World.name == new_name.data
            )
        )
        if world is not None:
            raise ValidationError('World already exists')
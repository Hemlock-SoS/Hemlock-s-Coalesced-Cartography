from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class NewWorldForm(FlaskForm):
    worldName = StringField('World name', validators=[DataRequired()])
    submit = SubmitField('Create')
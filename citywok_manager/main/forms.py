from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from citywok_manager.models import Job, Country


class SearchForm(FlaskForm):
    content = StringField('内容')


class AddJobForm(FlaskForm):
    job = StringField('职务名称', validators=[InputRequired('必填'), Length(max=5)])

    def validate_job(self, job):
        if Job.query.filter_by(name=self.job.data).first():
            raise ValidationError('职务已存在')


class AddCountryForm(FlaskForm):
    country = StringField('国家名称', validators=[
                          InputRequired('必填'), Length(max=10)])

    def validate_country(self, country):
        if Country.query.filter_by(zh=self.country.data).first():
            raise ValidationError('国家已存在')

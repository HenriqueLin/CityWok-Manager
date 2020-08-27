from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import InputRequired, Length, ValidationError
from citywok_manager.models import Job, Country, Setting


class SettingForm(FlaskForm):
    job = StringField(label='职务名称',
                      validators=[InputRequired('必填'),
                                  Length(max=5)])
    country = StringField(label='国家名称',
                          validators=[InputRequired('必填'),
                                      Length(max=10)])
    base_salary = DecimalField(label='最低工资',
                               validators=[InputRequired('必填')],
                               default=Setting.get_base_salary)
    tax_rate = DecimalField(label='税率',
                            places=4,
                            validators=[InputRequired('必填')],
                            default=Setting.get_tax_rate)

    def validate_job(self, job):
        if Job.query.filter_by(name=self.job.data).first():
            raise ValidationError('职务已存在')

    def validate_country(self, country):
        if Country.query.filter_by(zh=self.country.data).first():
            raise ValidationError('国家已存在')

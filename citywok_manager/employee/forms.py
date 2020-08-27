from flask import current_app, g
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, PasswordField, SubmitField, SelectField, IntegerField, FileField, TextAreaField, BooleanField, RadioField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Optional, ValidationError, NumberRange
from datetime import date
import os

from citywok_manager.models import Sex, Job, Id_type, Country, Employee, File
from citywok_manager.main.utils import get_pk


class EmployeeForm(FlaskForm):
    id = IntegerField('ID')
    first_name = StringField('名字', validators=[InputRequired('必填')])
    last_name = StringField('姓氏', validators=[InputRequired('必填')])
    zh_name = StringField('中文名')
    sex = SelectField('性别', choices=Sex.choices(),
                      validators=[InputRequired('必填')])
    birthday = DateField('出生日期', validators=[Optional()],
                         render_kw={'type': 'date'})
    contact = IntegerField('联系电话', validators=[Optional()],
                           render_kw={'type': 'tel'})
    email = StringField('邮箱地址', validators=[Optional(), Email('邮箱地址无效')],
                        render_kw={'type': 'email'})
    job = QuerySelectField('职务', query_factory=Job.get_query,
                           get_pk=lambda x: x.id, get_label='name')
    id_type = SelectField('证件类型', choices=Id_type.choices())
    id_number = StringField('证件号码')
    id_validity = DateField('证件有效期', validators=[Optional()],
                            render_kw={'type': 'date'})
    nationality = QuerySelectField(
        '国籍', query_factory=Country.get_query, get_pk=get_pk)
    nif = IntegerField('NIF', validators=[Optional()])
    niss = IntegerField('NISS', validators=[Optional()])
    start_date = DateField('就职日期', validators=[Optional()],
                           render_kw={'type': 'date'})
    total_salary = IntegerField(
        '工资', validators=[Optional(), NumberRange(min=0, message='不得小于0')])
    tax_salary = IntegerField(
        '报税金额', validators=[Optional(), NumberRange(min=0, message='不得小于0')], default=600)

    def validate_id_validity(self, id_validity):
        if (self.id_validity.data and self.id_validity.data < date.today()):
            raise ValidationError('证件已过期')

    def validate_nif(self, nif):
        e = Employee.query.filter_by(nif=nif.data).first()
        if nif.data and e and (e.id != self.id.data):
            raise ValidationError('NIF已存在')

    def validate_niss(self, niss):
        e = Employee.query.filter_by(niss=niss.data).first()
        if niss.data and e and (e.id != self.id.data):
            raise ValidationError('NISS已存在')


class EmployeeFileForm(FlaskForm):
    file_name = StringField(
        '文件名', validators=[Optional(), Length(max=30)])
    file = FileField('文件')
    file_note = TextAreaField('备注', validators=[Optional()])

    def validate_file_name(self, file_name):
        f = File.query.filter_by(
            employee_id=g.id, file_name=file_name.data).first()
        if file_name and f:
            raise ValidationError('文件名已存在')

    def validate_file(self, file):
        if not self.file:
            raise ValidationError('请选择文件')
        file.data.seek(0, os.SEEK_END)
        file_length = file.data.tell()
        file.data.seek(0, 0)
        if file_length > (5 * 1024 * 1024):
            raise ValidationError('文件过大(5MB)')


class EmployeeFilterForm(FlaskForm):
    name = StringField('名字')
    sex = SelectField('性别',
                      choices=(Sex.choices(blank=True)))
    job = QuerySelectField('职务',
                           query_factory=Job.get_query,
                           get_pk=get_pk,
                           get_label='name',
                           allow_blank=True,
                           blank_text="---")
    nationality = QuerySelectField('国籍', query_factory=Country.get_query,
                                   get_pk=get_pk,
                                   allow_blank=True,
                                   blank_text="---")


class EmployeeExportForm(FlaskForm):
    language = RadioField('语言', choices=[('zh', '中文'), ('pt', '葡语')])

    first_name = BooleanField('名字', default=True)
    last_name = BooleanField('姓氏', default=True)
    zh_name = BooleanField('中文名', default=True)
    sex = BooleanField('性别')
    birthday = BooleanField('出生日期')
    contact = BooleanField('联系电话')
    email = BooleanField('邮箱地址')
    job = BooleanField('职务')
    id_type = BooleanField('证件类型')
    id_number = BooleanField('证件号码')
    id_validity = BooleanField('证件有效期')
    nationality = BooleanField('国籍')
    nif = BooleanField('NIF')
    niss = BooleanField('NISS')
    start_date = BooleanField('就职日期')
    total_salary = BooleanField('工资')
    tax_salary = BooleanField('报税金额')

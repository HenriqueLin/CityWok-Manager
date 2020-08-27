from wtforms import IntegerField, StringField, SelectField, FileField, TextAreaField
from wtforms.validators import InputRequired, Optional, NumberRange, Email, ValidationError, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf import FlaskForm
from flask import g

from citywok_manager.models import Supplier, File
from citywok_manager.main.utils import get_pk
import os


class SupplierForm(FlaskForm):
    id = IntegerField('ID')
    name = StringField('公司名称', validators=[InputRequired('必填')])
    principal = StringField('负责人', validators=[Optional()])
    contact = IntegerField('联系电话', validators=[Optional()],
                           render_kw={'type': 'tel'})
    email = StringField('邮箱地址', validators=[Optional(), Email('邮箱地址无效')],
                        render_kw={'type': 'email'})
    nif = IntegerField('NIF', validators=[Optional()])
    iban = StringField('IBAN', validators=[Optional()], filters=[
                       lambda x: x or None])
    address = StringField('地址', validators=[Optional()])
    postcode = StringField('邮编', validators=[Optional()])
    city = StringField('城市', validators=[Optional()])

    def validate_nif(self, nif):
        s = Supplier.query.filter_by(nif=nif.data).first()
        if nif.data and s and (s.id != self.id.data):
            raise ValidationError('NIF已存在')

    def validate_iban(self, iban):
        s = Supplier.query.filter_by(iban=iban.data).first()
        if iban.data and s and (s.id != self.id.data):
            raise ValidationError('IBAN已存在')


class SupplierFilter(FlaskForm):
    context = StringField()
    order = SelectField(choices=[('id', '排序: ID'), ('name', '排序: 名称')])


class SupplierFileForm(FlaskForm):
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

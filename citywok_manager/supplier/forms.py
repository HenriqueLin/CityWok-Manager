from wtforms import IntegerField, StringField, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange, Email, ValidationError
from flask_wtf import FlaskForm

from citywok_manager.models import Supplier


class SupplierForm(FlaskForm):
    id = IntegerField('ID')
    name = StringField('公司名称', validators=[DataRequired('必填')])
    principal = StringField('负责人', validators=[Optional()])
    contact = IntegerField('联系电话', validators=[Optional()])
    email = StringField('邮箱地址', validators=[Optional(), Email('邮箱地址无效')])
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

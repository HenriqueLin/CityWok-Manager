from flask import request
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, IntegerField, FileField, MultipleFileField, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, ValidationError, NumberRange
from wtforms.fields.html5 import DateField, DecimalField
from datetime import datetime

from citywok_manager.models import Diary, Supplier, ExpenseType, PaymentMethod, Employee


class DailyIncomeForm(FlaskForm):
    date = DateField(label='日期',
                     default=datetime.today,
                     validators=[InputRequired('必填')])

    theoretical = DecimalField(label='理论收入',
                               validators=[InputRequired('必填'),
                                           NumberRange(min=0, message='不得小于0')],
                               render_kw={'step': '0.01', 'min': '0'})

    cash = DecimalField(label='现金收入',
                        validators=[InputRequired('必填'),
                                    NumberRange(min=0, message='不得小于0')],
                        render_kw={'step': '0.01', 'min': '0'})

    mb_1_total = DecimalField(label='MB-1-总收入',
                              validators=[InputRequired('必填')],
                              render_kw={'step': '0.01', 'min': '0'})

    mb_1_actual = DecimalField(label='MB-1-实际收入',
                               validators=[InputRequired('必填'),
                                           NumberRange(min=0, message='不得小于0')],
                               render_kw={'step': '0.01', 'min': '0'})
    mb_2_total = DecimalField(label='MB-2-总收入',
                              validators=[InputRequired('必填'),
                                          NumberRange(min=0, message='不得小于0')],
                              render_kw={'step': '0.01', 'min': '0'})
    mb_2_actual = DecimalField(label='MB-2-实际收入',
                               validators=[InputRequired('必填'),
                                           NumberRange(min=0, message='不得小于0')],
                               render_kw={'step': '0.01', 'min': '0'})
    mb_3_total = DecimalField(label='MB-3-总收入',
                              validators=[InputRequired('必填'),
                                          NumberRange(min=0, message='不得小于0')],
                              render_kw={'step': '0.01', 'min': '0'})
    mb_3_actual = DecimalField(label='MB-3-实际收入',
                               validators=[InputRequired('必填'),
                                           NumberRange(min=0, message='不得小于0')],
                               render_kw={'step': '0.01', 'min': '0'})
    mb_file = MultipleFileField('MB-文件')
    signature = FileField('参与人签字', validators=[InputRequired('请选择文件')])

    def validate_mb_1_total(self, mb_1_total):
        if self.mb_1_actual.data and self.mb_1_actual.data > self.mb_1_total.data:
            raise ValidationError('总收入应大于实际收入，请重新核对')

    def validate_mb_2_total(self, mb_2_total):
        if self.mb_1_actual.data and self.mb_2_actual.data > self.mb_2_total.data:
            raise ValidationError('总收入应大于实际收入，请重新核对')

    def validate_mb_3_total(self, mb_3_total):
        if self.mb_1_actual.data and self.mb_3_actual.data > self.mb_3_total.data:
            raise ValidationError('总收入应大于实际收入，请重新核对')

    def validate_date(self, date):
        d = Diary.query.get(self.date.data)
        if d and d.is_init:
            raise ValidationError('日期已存在')

    def validate_mb_file(self, mb_file):
        l = request.files.getlist('mb_file')
        if not l[0].filename:
            raise ValidationError('请选择文件')


class ExpenseForm(FlaskForm):
    date = DateField(label='日期',
                     default=datetime.today,
                     validators=[InputRequired('必填')])

    amount = DecimalField(label='金额',
                          validators=[InputRequired('必填'),
                                      NumberRange(min=0, message='不得小于0')],
                          render_kw={'step': '0.01', 'min': '0'})

    supplier = QuerySelectField(label='付款对象',
                                validators=[InputRequired('必选')],
                                query_factory=Supplier.get_query,
                                get_pk=lambda x: x.id,
                                get_label=Supplier.get_label)

    expense_type = QuerySelectField(label='类别',
                                    validators=[InputRequired('必填')],
                                    query_factory=ExpenseType.get_query,
                                    get_pk=lambda x: x.id,
                                    get_label=ExpenseType.get_label)

    method = SelectField(label='付款方式',
                         validators=[InputRequired('必选')],
                         choices=PaymentMethod.choices())

    files = MultipleFileField(label='文件')

    def validate_files(self, files):
        l = request.files.getlist('files')
        if not l[0].filename:
            raise ValidationError('请选择文件')


class LaborExpenseForm(FlaskForm):
    date = DateField(label='日期',
                     default=datetime.today,
                     validators=[InputRequired('必填')])

    amount = DecimalField(label='金额',
                          validators=[InputRequired('必填'),
                                      NumberRange(min=0, message='不得小于0')],
                          render_kw={'step': '0.01', 'min': '0'})

    employee = QuerySelectField(label='付款对象',
                                validators=[InputRequired('必选')],
                                query_factory=Employee.get_query,
                                get_pk=lambda x: x.id,
                                get_label=Employee.get_label)

    expense_type = QuerySelectField(label='类别',
                                    validators=[InputRequired('必填')],
                                    query_factory=ExpenseType.get_salary_query,
                                    get_pk=lambda x: x.id,
                                    get_label=ExpenseType.get_label)

    method = SelectField(label='付款方式',
                         validators=[InputRequired('必选')],
                         choices=PaymentMethod.choices())

    files = MultipleFileField(label='文件')

    def validate_files(self, files):
        l = request.files.getlist('files')
        if not l[0].filename:
            raise ValidationError('请选择文件')

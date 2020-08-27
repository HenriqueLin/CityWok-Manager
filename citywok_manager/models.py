from citywok_manager import db, login_manager, bcrypt
from flask_login import UserMixin, current_user
from flask import current_app, request, redirect, url_for, flash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import not_, Column, String, Integer, ForeignKey, DateTime, Date, Enum, Boolean, Text
from sqlalchemy.orm import relationship, backref
import enum
import os
from decimal import Decimal
from datetime import datetime
from functools import wraps
from sqlalchemy.types import TypeDecorator, Integer


class SqliteDecimal(TypeDecorator):
    # This TypeDecorator use Sqlalchemy Integer as impl. It converts Decimals
    # from Python to Integers which is later stored in Sqlite database.
    impl = Integer

    def __init__(self, scale):
        # It takes a 'scale' parameter, which specifies the number of digits
        # to the right of the decimal point of the number in the column.
        TypeDecorator.__init__(self)
        self.scale = scale
        self.multiplier_int = 10 ** self.scale

    def process_bind_param(self, value, dialect):
        # e.g. value = Column(SqliteDecimal(2)) means a value such as
        # Decimal('12.34') will be converted to 1234 in Sqlite
        if value is not None:
            value = int(Decimal(value) * self.multiplier_int)
        return value

    def process_result_value(self, value, dialect):
        # e.g. Integer 1234 in Sqlite will be converted to Decimal('12.34'),
        # when query takes place.
        if value is not None:
            value = Decimal(value) / self.multiplier_int
        return value


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class MyMixin(object):
    create_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=datetime.utcnow,
                       onupdate=datetime.utcnow)

    @declared_attr
    def create_by_id(self):
        return Column(Integer, ForeignKey('user.id'), default=User.get_current_user_id)

    @declared_attr
    def update_by_id(self):
        return Column(Integer, ForeignKey('user.id'), default=User.get_current_user_id, onupdate=User.get_current_user_id)

    @declared_attr
    def create_by(self):
        return relationship("User", foreign_keys=f'{self.__name__}.create_by_id')

    @declared_attr
    def update_by(self):
        return relationship("User", foreign_keys=f'{self.__name__}.update_by_id')


class MyEnum(enum.Enum):
    @classmethod
    def choices(cls, blank=False):
        res = [(e.name, e.value) for e in cls]
        if blank:
            res.insert(0, ("", "---"))
        return res


class Role(MyEnum):
    Admin = '编辑/查看'
    Visiter = '查看'


class Setting(db.Model):
    id = Column(Integer, primary_key=True)
    base_salary = Column(SqliteDecimal(2), nullable=False)
    tax_rate = Column(SqliteDecimal(4), nullable=False)

    @classmethod
    def get_base_salary(cls):
        return cls.query.get(1).base_salary

    @classmethod
    def set_base_salary(cls, value):
        cls.query.get(1).base_salary = value

    @classmethod
    def get_tax_rate(cls):
        return cls.query.get(1).tax_rate

    @classmethod
    def set_tax_rate(cls, value):
        cls.query.get(1).tax_rate = value


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)

    def __repr__(self):
        return f"User('{self.role}','{self.username}','{self.email}')"

    def need_permission(permission):
        def warp_1(func):
            @wraps(func)
            def warp_2(*args, **kwargs):
                if not current_user.is_authenticated:
                    return current_app.login_manager.unauthorized()
                elif (current_user.role.name == 'Visiter' and permission != 'Visiter'):
                    flash('无访问权限', 'warning')
                    return redirect(url_for('main.home'))
                return func(*args, **kwargs)
            return warp_2
        return warp_1

    @staticmethod
    def create_invite_token(role, expires_sec=3600):
        """Create a random token for inviting new users

        Keyword Arguments:
            expires_sec {int} -- time the token can be used (seconds) (default: {3600})

        Returns:
            stirng -- A random token
        """
        s = Serializer(current_app.secret_key, expires_sec)
        return s.dumps({'key': 20190512, 'role': role}).decode('utf-8')

    @staticmethod
    def verify_invite_token(token):
        """Verify if the invite token is valid

        Arguments:
            token {String} -- A random token

        Returns:
            Boolean -- The verify resulte
        """
        s = Serializer(current_app.secret_key)
        try:
            if 20190512 != s.loads(token)['key']:
                return None
            role = s.loads(token)['role']
        except:
            return None
        return role

    @staticmethod
    def get_current_user_id():
        if current_user:
            return current_user.id
        else:
            return None

    @classmethod
    def authenticate_user(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user


class Sex(MyEnum):
    M = '男'
    F = '女'


class Id_type(MyEnum):
    Passport = '护照'
    C_Cidadao = '身份证'
    T_Residencia = '居留证'
    C_R_Permanente = '永久居住证'


class Employee(db.Model, MyMixin):
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    zh_name = Column(String, default='-')
    sex = Column(Enum(Sex), nullable=False)
    birthday = Column(Date)
    contact = Column(Integer)
    email = Column(String)
    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job", uselist=False)
    id_type = Column(Enum(Id_type))
    id_number = Column(String)
    id_validity = Column(Date)
    nationality_id = Column(Integer, ForeignKey('country.id'))
    nationality = relationship("Country", uselist=False)
    nif = Column(Integer, unique=True)
    niss = Column(Integer, unique=True)
    start_date = Column(Date)
    total_salary = Column(Integer)
    tax_salary = Column(Integer)
    is_active = Column(Boolean, default=True)
    arrear = Column(SqliteDecimal(2), default=0, nullable=False)

    files = relationship('File', back_populates="employee")

    salarys = relationship('SalaryEmployee', back_populates="employee")

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def __repr__(self):
        return f"Employee('{self.first_name}','{self.last_name}')"

    def get_data(self):
        return {'id': self.id,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'zh_name': self.zh_name,
                'sex': self.sex.value,
                'birthday': self.birthday,
                'contact': self.contact,
                'email': self.email,
                'job': (self.job.name if self.job is not None else None),
                'id_type': self.id_type.value,
                'id_number': self.id_number,
                'id_validity': self.id_validity,
                'nationality': (self.nationality.zh if self.nationality is not None else None),
                'nif': self.nif,
                'niss': self.niss,
                'start_date': self.start_date,
                'total_salary': self.total_salary,
                'tax_salary': self.tax_salary
                }

    def get_link(self):
        return url_for('employee.detail', employee_id=self.id)

    def get_folder(self):
        return os.path.join(current_app.root_path, 'employee', str(self.id))

    def get_label(self):
        return f'{self.id}: {self.full_name} ({self.zh_name})'

    @classmethod
    def get_query(cls):
        return cls.query

    @staticmethod
    def get_heads():
        return {'id': '#',
                'first_name': '名字',
                'last_name': '姓氏',
                'zh_name': '中文名',
                'sex': '性别',
                'birthday': '生日',
                'contact': '联系电话',
                'email': '邮箱',
                'job': '职务',
                'id_type': '证件类型',
                'id_number': '证件号码',
                'id_validity': '证件有效期',
                'nationality': '国籍',
                'nif': 'NIF',
                'niss': 'NISS',
                'start_date': '就职日期',
                'total_salary': '工资',
                'tax_salary': '报税金额'}

    @staticmethod
    def get_keys():
        return('id',
               'first_name',
               'last_name',
               'zh_name',
               'sex',
               'birthday',
               'contact',
               'email',
               'job',
               'id_type',
               'id_number',
               'id_validity',
               'nationality',
               'nif',
               'niss',
               'start_date',
               'total_salary',
               'tax_salary')


class Country(db.Model):
    id = Column(Integer, primary_key=True)
    zh = Column(String(30), nullable=False)

    @classmethod
    def get_query(cls):
        return cls.query

    def get_delete_link(self):
        return url_for('main.delete_country', country_id=str(self.id))

    def __repr__(self):
        return f"Country('{self.zh}')"

    def __str__(self):
        return f'{self.zh}'


class Job(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False)

    @classmethod
    def get_query(cls):
        return cls.query

    def get_delete_link(self):
        return url_for('main.delete_job', job_id=str(self.id))

    def __repr__(self):
        return f"Job('{self.name}')"

    def __str__(self):
        return f'{self.name}'


class File(db.Model, MyMixin):
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    file_ext = Column(String, nullable=False)
    file_note = Column(Text, nullable=True)

    employee_id = Column(Integer, ForeignKey('employee.id'))
    employee = relationship("Employee", back_populates="files")
    supplier_id = Column(Integer, ForeignKey('supplier.id'))
    supplier = relationship("Supplier", back_populates="files")
    income_id = Column(Integer, ForeignKey('income.id'))
    income = relationship("Income", back_populates="files")
    dairy_id = Column(Date, ForeignKey('diary.date'))
    expense_id = Column(Integer, ForeignKey('expense.id'))
    expense = relationship("Expense", back_populates="files")
    salary_id = Column(Integer, ForeignKey('salary.id'))

    @hybrid_property
    def full_name(self):
        return self.file_name + self.file_ext

    @property
    def file_size(self):
        if self.employee_id:
            return os.path.size(
                os.path.join(current_app.config['EMPLOYEE_FILE'], self.employee_id, self.full_name))
        elif self.supplier_id:
            return os.path.size(
                os.path.join(current_app.config['SUPPLIER_FILE'], self.supplier_id, self.full_name))

    @property
    def download_link(self):
        if self.employee_id:
            return url_for('employee.get_file',
                           employee_id=self.employee_id,
                           filename=self.full_name)
        elif self.supplier_id:
            return url_for('supplier.get_file',
                           supplier_id=self.supplier_id,
                           filename=self.full_name)

    @property
    def delete_link(self):
        if self.employee_id:
            return url_for('employee.delete_file',
                           employee_id=self.employee_id,
                           filename=self.full_name)
        elif self.supplier_id:
            return url_for('supplier.delete_file',
                           supplier_id=self.supplier_id,
                           filename=self.full_name)

    @staticmethod
    def get_heads():
        return ['文件名', '备注', '删除']

    def data_list(self):
        return [self.file_name,
                self.file_note]


class Supplier(db.Model, MyMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    principal = Column(String)
    contact = Column(Integer)
    email = Column(String)
    nif = Column(Integer, unique=True)
    iban = Column(String, unique=True)
    address = Column(String)
    postcode = Column(String)
    city = Column(String)
    files = relationship('File', back_populates="supplier")

    def __repr__(self):
        return f"Supplier('{self.name}')"

    @classmethod
    def get_query(cls):
        return cls.query

    def get_label(self):
        return f"{self.id}: {self.name}"

    def get_data(self):
        return {'id': self.id,
                'name': self.name,
                'principal': self.principal,
                'contact': self.contact,
                'email': self.email,
                'nif': self.nif,
                'iban': self.iban,
                'address': self.address,
                'postcode': self.postcode,
                'city': self.city
                }

    def get_link(self):
        return url_for('supplier.detail', supplier_id=self.id)

    def get_folder(self):
        return os.path.join(current_app.root_path, 'supplier', str(self.id))

    @staticmethod
    def get_heads():
        return {'id': '#',
                'name': '公司名称',
                'principal': '负责人',
                'contact': '联系电话',
                'email': '邮箱地址',
                'nif': 'NIF',
                'iban': 'IBAN',
                'address': '地址',
                'postcode': '邮编',
                'city': '城市'}

    @staticmethod
    def get_keys():
        return('id',
               'name',
               'principal',
               'contact',
               'email',
               'nif',
               'iban',
               'address',
               'postcode',
               'city')


class PaymentMethod(MyEnum):
    Cash = '现金'
    Card = '刷卡'
    Transfer = '转账'
    Check = '支票'
    Mix = '混合'


class IncomeType(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    changeable = Column(Boolean, default=True)


class ExpenseType(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    changeable = Column(Boolean, default=True)

    parent_id = Column(Integer, ForeignKey('expense_type.id'))
    children = relationship(
        'ExpenseType', backref=backref('parent', remote_side=[id]))

    @classmethod
    def get_query(cls):
        return cls.query.filter(cls.parent_id != 1)

    @classmethod
    def get_salary_query(cls):
        return cls.query.filter(cls.parent_id == 1)

    def get_label(self):
        return f'{self.parent.name}: {self.name}'


class Diary(db.Model):
    date = Column(Date, primary_key=True)
    theoretical_income = Column(SqliteDecimal(2), nullable=False)
    movements = relationship('Movement')
    signature = relationship('File', uselist=False)
    is_init = Column(Boolean, default=False)


class Movement(db.Model, MyMixin):
    id = Column(Integer, primary_key=True)
    date = Column(Date, ForeignKey('diary.date'))
    method = Column(Enum(PaymentMethod), nullable=False)
    type = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'movement',
        'polymorphic_on': type
    }

    def __str__(self):
        return f'{self.amount}'


class Income(Movement):
    id = Column(Integer, ForeignKey('movement.id'), primary_key=True)
    amount = Column(SqliteDecimal(2), nullable=False)
    income_type_id = Column(Integer, ForeignKey('income_type.id'))
    income_type = relationship("IncomeType", backref="income")

    files = relationship('File', back_populates="income")

    __mapper_args__ = {
        'polymorphic_identity': 'income',
    }


class Expense(Movement):
    id = Column(Integer, ForeignKey('movement.id'), primary_key=True)
    amount = Column(SqliteDecimal(2), nullable=False)

    expense_type_id = Column(Integer, ForeignKey('expense_type.id'))
    expense_type = relationship("ExpenseType")

    supplier_id = Column(Integer, ForeignKey('supplier.id'))
    supplier = relationship("Supplier", backref='expense')

    employee_id = Column(Integer, ForeignKey('employee.id'))
    employee = relationship("Employee", backref='expense')

    files = relationship('File', back_populates="expense")

    __mapper_args__ = {
        'polymorphic_identity': 'expense',
    }


class Salary(Movement):
    id = Column(Integer, ForeignKey('movement.id'), primary_key=True)
    expense_type_id = Column(Integer, ForeignKey('expense_type.id'), default=5)
    expense_type = relationship("ExpenseType")

    month = Column(Date, nullable=False)
    base_salary = Column(SqliteDecimal(2), nullable=False)
    tax_rate = Column(SqliteDecimal(4), nullable=False)

    employees = relationship('SalaryEmployee', back_populates='salary')
    files = relationship('File', backref="salary")

    __mapper_args__ = {
        'polymorphic_identity': 'salary',
    }

    @property
    def cash(self):
        res = 0
        for e in self.employees:
            res += e.cash
        return res

    @property
    def transfer(self):
        res = 0
        for e in self.employees:
            res += e.transfer
        return res

    @property
    def amount(self):
        return self.cash + self.transfer


class SalaryEmployee(db.Model, MyMixin):
    salary_id = Column(Integer, ForeignKey('salary.id'), primary_key=True)
    employee_id = Column(Integer, ForeignKey('employee.id'), primary_key=True)

    cash = Column(SqliteDecimal(2), nullable=False)
    transfer = Column(SqliteDecimal(2), nullable=False)
    repayment = Column(SqliteDecimal(2), nullable=False, default=0)
    month = Column(Date, nullable=False)

    employee = relationship("Employee", back_populates="salarys")
    salary = relationship("Salary", back_populates="employees")

    @property
    def total(self):
        return self.cash + self.transfer



from citywok_manager import db, login_manager, bcrypt
from flask_login import UserMixin, current_user
from flask import current_app, request, redirect, url_for, flash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.ext.declarative import declared_attr
import enum
import os
from datetime import datetime
from functools import wraps
from citywok_manager.main.utils import get_current_user_id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class MyMixin(object):
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    update_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    def create_by_id(self):
        return db.Column(db.Integer, db.ForeignKey(
            'user.id'), default=get_current_user_id)

    @declared_attr
    def update_by_id(self):
        return db.Column(db.Integer, db.ForeignKey(
            'user.id'), default=get_current_user_id, onupdate=get_current_user_id)

    @declared_attr
    def create_by(self):
        return db.relationship("User", foreign_keys=f'{self.__name__}.create_by_id')

    @declared_attr
    def update_by(self):
        return db.relationship("User", foreign_keys=f'{self.__name__}.update_by_id')


class Enum(enum.Enum):
    @classmethod
    def choices(cls, blank=False):
        res = [(e.name, e.value) for e in cls]
        if blank:
            res.insert(0, ("", "---"))
        return res


class Role(Enum):
    Admin = '编辑/查看'
    Visiter = '查看'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)

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

    @classmethod
    def authenticate_user(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user


class Sex(Enum):
    M = '男'
    F = '女'


class Id_type(Enum):
    Passport = '护照'
    C_Cidadao = '身份证'
    T_Residencia = '居留证'
    C_R_Permanente = '永久居住证'


class Employee(db.Model, MyMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    zh_name = db.Column(db.String(20))
    sex = db.Column(db.Enum(Sex), nullable=False)
    birthday = db.Column(db.Date)
    contact = db.Column(db.Integer)
    email = db.Column(db.String(120))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", uselist=False)
    id_type = db.Column(db.Enum(Id_type))
    id_number = db.Column(db.String(10))
    id_validity = db.Column(db.Date)
    nationality_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    nationality = db.relationship("Country", uselist=False)
    nif = db.Column(db.Integer, unique=True)
    niss = db.Column(db.Integer, unique=True)
    start_date = db.Column(db.Date)
    total_salary = db.Column(db.Integer)
    tax_salary = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    files = db.relationship('EmployeeFile', backref="owner")

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
    id = db.Column(db.Integer, primary_key=True)
    zh = db.Column(db.String(30), nullable=False)

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)

    @classmethod
    def get_query(cls):
        return cls.query

    def get_delete_link(self):
        return url_for('main.delete_job', job_id=str(self.id))

    def __repr__(self):
        return f"Job('{self.name}')"


class File(db.Model, MyMixin):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(30))
    note = db.Column(db.Text)
    type = db.Column(db.String(20))
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'file'
    }


class EmployeeFile(File):
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'employee_file'
    }

    @staticmethod
    def get_heads():
        return ['#', '文件名', '备注', '下载', '删除']

    def data_list(self):
        return [self.id,
                self.file_name,
                self.note]

    def get_download_link(self):
        return url_for('employee.get_file', employee_id=str(self.owner_id), filename=self.file_name)

    def get_delete_link(self):
        return url_for('employee.delete_file', employee_id=str(self.owner_id), filename=self.file_name)


class SupplierFile(File):
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'supplier_file'
    }

    @staticmethod
    def get_heads():
        return ['#', '文件名', '备注', '下载', '删除']

    def data_list(self):
        return [self.id,
                self.file_name,
                self.note]

    # def get_download_link(self):
    #     return url_for('employee.get_file', employee_id=str(self.owner_id), filename=self.file_name)

    # def get_delete_link(self):
    #     return url_for('employee.delete_file', employee_id=str(self.owner_id), filename=self.file_name)


class Supplier(db.Model, MyMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    principal = db.Column(db.String(50))
    contact = db.Column(db.Integer)
    email = db.Column(db.String(120))
    nif = db.Column(db.Integer, unique=True)
    iban = db.Column(db.String(30), unique=True)
    address = db.Column(db.String(100))
    postcode = db.Column(db.String(15))
    city = db.Column(db.String(15))
    files = db.relationship('SupplierFile', backref="owner")

    def __repr__(self):
        return f"Supplier('{self.name}')"

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

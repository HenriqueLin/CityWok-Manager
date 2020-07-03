from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, Email, EqualTo, ValidationError
from flask_login import current_user

from citywok_manager.models import User, Role


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[
                           DataRequired(), Length(min=2, max=20)])
    password = PasswordField('密码', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱',
                        validators=[Optional(), Email(message='邮箱地址无效')],
                        filters=[lambda x: x or None])
    password = PasswordField('密码', validators=[DataRequired()])
    confirm_password = PasswordField('确认密码',
                                     validators=[DataRequired(), EqualTo('password')])

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('用户名已被使用')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('邮箱已被使用')


class InviteForm(FlaskForm):
    email = StringField('受邀人邮箱', validators=[
                        DataRequired('请填写受邀人的邮箱地址'), Email('邮箱地址无效')])
    link = StringField('邀请链接', validators=[DataRequired('请生成链接')])
    role = SelectField('权限', validators=[
                       DataRequired()], choices=Role.choices(), default='Visiter')


class AccountUpdateForm(FlaskForm):
    username = StringField('用户名', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱',
                        validators=[Optional(), Email(message='邮箱地址无效')],
                        filters=[lambda x: x or None])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and (user != current_user):
            raise ValidationError('用户名已被使用')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and (user != current_user):
            raise ValidationError('邮箱已被使用')


class PasswordChangeForm(FlaskForm):
    old_pw = PasswordField('密码', validators=[DataRequired()])
    new_pw = PasswordField('密码', validators=[DataRequired()])
    confirm_new_pw = PasswordField('确认密码', validators=[DataRequired(),
                                                       EqualTo('new_pw')])

    def validate_old_pw(self, old_pw):
        if not User.authenticate_user(current_user.username, old_pw.data):
            raise ValidationError('密码错误')

    def validate_new_pw(self, new_pw):
        if self.new_pw.data == self.old_pw.data:
            raise ValidationError('新密码与旧密码相同')

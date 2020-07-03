from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, logout_user, current_user

from citywok_manager import db, bcrypt
from citywok_manager.models import User
from citywok_manager.users.forms import LoginForm, RegistrationForm, InviteForm, AccountUpdateForm, PasswordChangeForm

users = Blueprint('users', __name__)


@users.route("/", methods=['GET', 'POST'])
@users.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        user = User.authenticate_user(username=form.username.data,
                                      password=form.password.data)
        if user:
            login_user(user)
            flash('登录成功', category='success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('登录失败，请检查账号和密码', category='danger')
    return render_template('login.html', title='登录', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route("/registration/<token>", methods=['GET', 'POST'])
def registration(token):
    if current_user.is_authenticated:
        flash('您已登录，请登出后重试', 'info')
        return redirect(url_for('main.home'))
    role = User.verify_invite_token(token)
    if not role:
        flash('链接无效/已过期', 'warning')
        return redirect(url_for('users.login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.role = role
        user.password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'注册成功', category='success')
        return redirect(url_for('main.home'))
    else:
        return render_template('registration.html', title='注册', form=form)


@users.route("/invite", methods=['GET', 'POST'])
@User.need_permission('Admin')
def invite():
    form = InviteForm()
    if form.is_submitted():
        if 'create_link' in request.form:
            token = User.create_invite_token(form.role.data)
            form.link.data = url_for(
                'users.registration', token=token, _external=True)
        elif 'invite' in request.form and form.validate():
            # TODO send email
            flash(f'已发送邀请至对方邮箱：{form.email.data}', 'info')
            form.email.data = ""
    return render_template('invite.html', title='Invite', form=form)


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    update_form = AccountUpdateForm()
    change_pw_form = PasswordChangeForm()
    if request.method == 'POST':
        if 'update' in request.form and update_form.validate():
            update_form.populate_obj(current_user)
            db.session.commit()
            flash('账户信息更新成功', 'success')
            return redirect(url_for('users.account'))
        elif 'update_pw' in request.form and change_pw_form.validate():
            current_user.password = bcrypt.generate_password_hash(
                change_pw_form.new_pw.data).decode('utf-8')
            db.session.commit()
            flash('账户密码更新成功', 'success')
            return redirect(url_for('users.account'))
    update_form.process(obj=current_user)
    return render_template('account.html', title='账户', update_form=update_form, change_pw_form=change_pw_form)

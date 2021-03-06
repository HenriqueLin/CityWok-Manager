from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request, current_app
from decimal import Decimal
import os
from sqlalchemy import not_
from datetime import date, datetime
from citywok_manager import db
from citywok_manager.models import Income, Diary, PaymentMethod, IncomeType, File, Expense, ExpenseType, Employee, Salary, SalaryEmployee, Setting
from citywok_manager.registry.forms import DailyIncomeForm, ExpenseForm, LaborExpenseForm, SalaryForm, SalarySubForm

registry = Blueprint('registry', __name__, url_prefix="/registry")


@registry.route('/', methods=['GET'])
def index():
    return render_template('registry/index.html',
                           title='登记处')


@registry.route('/daily_income', methods=['GET', 'POST'])
def daily_income():
    form = DailyIncomeForm()
    if form.validate_on_submit():
        # Cash instance
        cash = Income(date=form.date.data,
                      method=PaymentMethod.Cash,
                      amount=form.cash.data,
                      income_type=IncomeType.query.get(1))

        # MultiBanco instance
        mb_actual = form.mb_1_actual.data + form.mb_2_actual.data + form.mb_3_actual.data
        mb_total = form.mb_1_total.data + form.mb_2_total.data + form.mb_3_total.data
        mb = Income(date=form.date.data,
                    method=PaymentMethod.Card,
                    amount=mb_actual,
                    income_type=IncomeType.query.get(1))

        # tax of the back
        tax = Expense(date=form.date.data,
                      method=PaymentMethod.Transfer,
                      amount=mb_total - mb_actual,
                      expense_type=ExpenseType.query.get(1))

        # Diary instance
        diary = Diary(theoretical_income=form.theoretical.data,
                      date=form.date.data,
                      movements=[cash, mb, tax],
                      is_init=True)

        # signature file
        sig = form.signature.data
        _, f_ext = os.path.splitext(sig.filename)
        # add file to diary
        diary.signature = File(file_name=form.date.data.strftime('%Y%m%d') + '-signature',
                               file_ext=f_ext)
        path = os.path.join(
            current_app.config['MOVEMENT_FILE'], form.date.data.strftime('%Y%m%d') + '-signature' + f_ext)
        sig.save(path)

        # mb files
        i = 1
        for file in request.files.getlist('mb_file'):
            _, f_ext = os.path.splitext(file.filename)
            # add file to income
            mb.files.append(File(file_name=form.date.data.strftime('%Y%m%d') + '-mb-' + str(i),
                                 file_ext=f_ext))
            path = os.path.join(
                current_app.config['MOVEMENT_FILE'], form.date.data.strftime('%Y%m%d') + '-mb-' + str(i) + f_ext)
            file.save(path)
            i += 1

        # add and commit to db
        db.session.add(diary)
        db.session.commit()
        flash('添加成功', 'success')
        return redirect(url_for('registry.index'))

    return render_template('registry/daily_income.html',
                           form=form,
                           title='每日进账')


@registry.route('/expense', methods=['GET', 'POST'])
def expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(date=form.date.data,
                          amount=form.amount.data,
                          expense_type=form.expense_type.data,
                          method=form.method.data,
                          supplier=form.supplier.data)

        db.session.add(expense)
        db.session.flush()

        i = 1
        for file in request.files.getlist('files'):
            _, f_ext = os.path.splitext(file.filename)
            # add file to expense
            File(file_name=form.date.data.strftime('%Y%m%d') + '-' + str(expense.id) + '-' + str(i),
                 file_ext=f_ext,
                 expense=expense)
            path = os.path.join(
                current_app.config['MOVEMENT_FILE'], form.date.data.strftime('%Y%m%d') + '-' + str(expense.id) + '-' + str(i) + f_ext)
            file.save(path)
            i += 1

        db.session.commit()

        flash('添加成功', 'success')
        return redirect(url_for('registry.index'))

    return render_template('registry/expense.html',
                           form=form,
                           title='非人工支出')


@registry.route('/labor_expense', methods=['GET', 'POST'])
def labor_expense():
    form = LaborExpenseForm()
    if form.validate_on_submit():
        expense = Expense(date=form.date.data,
                          amount=form.amount.data,
                          expense_type=form.expense_type.data,
                          method=form.method.data,
                          employee=form.employee.data)

        db.session.add(expense)
        db.session.flush()

        i = 1
        for file in request.files.getlist('files'):
            _, f_ext = os.path.splitext(file.filename)
            # add file to expense
            File(file_name=form.date.data.strftime('%Y%m%d') + '-' + str(expense.id) + '-' + str(i),
                 file_ext=f_ext,
                 expense=expense)
            path = os.path.join(
                current_app.config['MOVEMENT_FILE'], form.date.data.strftime('%Y%m%d') + '-' + str(expense.id) + '-' + str(i) + f_ext)
            file.save(path)
            i += 1

        if expense.expense_type.name == '预支':
            expense.employee.arrear += expense.amount

        db.session.commit()

        flash('添加成功', 'success')
        return redirect(url_for('registry.index'))

    return render_template('registry/labor_expense.html',
                           form=form,
                           title='人工支出')


@registry.route('/salary/', defaults={'month': date.today().strftime("%Y-%m")}, methods=['GET', 'POST'])
@registry.route('/salary/<month>', methods=['GET', 'POST'])
def salary(month):
    form = SalaryForm(month=datetime.strptime(month, "%Y-%m"))

    if form.is_submitted():
        if "update" in request.form:
            return redirect(url_for('registry.salary', month=form.month.data.strftime("%Y-%m")))
            #month = form.month.data
        elif "add" in request.form and form.validate():
            S = Salary(month=form.month.data,
                       date=form.date.data,
                       method=PaymentMethod.Mix,
                       base_salary=Setting.get_base_salary(),
                       tax_rate=Setting.get_tax_rate())
            for subform in form.salarys:
                if not subform.skip.data:
                    s = SalaryEmployee(employee_id=subform.ID.data,
                                       transfer=Decimal(
                                           str(subform.transfer_salary.data)),
                                       cash=Decimal(
                                           str(subform.real_cash_salary.data)),
                                       month=form.month.data)
                    S.employees.append(s)
            db.session.add(S)
            db.session.commit()
            flash('添加成功', 'success')
            return redirect(url_for('registry.salary'))

    employees = Employee.query.filter_by(is_active=True).\
        filter(not_(Employee.salarys.
                    any(SalaryEmployee.month == datetime.strptime(month, "%Y-%m").date()))).all()
    for e in employees:
        subform = SalarySubForm()
        subform.ID = e.id
        subform.skip = 0
        subform.transfer_salary = 0
        subform.cash_salary = 0
        subform.repayment = e.arrear
        subform.real_cash_salary = 0
        subform.sub_total = 0
        form.salarys.append_entry(subform)

    return render_template('registry/salary.html',
                           form=form,
                           data=zip(employees,
                                    form.salarys,
                                    range(len(employees))),
                           base_salary=Setting.get_base_salary(),
                           tax_rate=Setting.get_tax_rate(),
                           title='工资结算')


@registry.route('/test', methods=['GET', 'POST'])
def test():
    return str(Expense.query.first().employee.arrear)

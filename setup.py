# coding:utf-8
from citywok_manager import create_app, db, bcrypt
from citywok_manager.models import Country, User, Job, IncomeType, Supplier, ExpenseType, Setting
from decimal import Decimal
import os
import shutil


def clean_path(path_to_clean):
    for filename in os.listdir(path_to_clean):
        file_path = os.path.join(path_to_clean, filename)
        if filename != '.gitkeep':
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


app = create_app()


with app.app_context():

    clean_path(os.path.join(app.config['EMPLOYEE_FILE']))
    clean_path(os.path.join(app.config['SUPPLIER_FILE']))
    clean_path(os.path.join(app.config['MOVEMENT_FILE']))

    # clear the database if needed
    db.drop_all()

    # create the database
    db.create_all()

    # settings
    db.session.add(Setting(base_salary=Decimal("635"),
                           tax_rate=Decimal("0.3475")))

    # add basic coutries into database
    countries = ['中国', '葡萄牙', '巴西', '孟加拉', '尼泊尔', '阿根廷', '巴基斯坦']
    for county in countries:
        new_country = Country(zh=county)
        db.session.add(new_country)

    # add jobs to db
    jobs = ['跑堂', '大厨', '油锅', '寿司', '铁板', '沙拉', '出菜']
    for job in jobs:
        new_job = Job(name=job)
        db.session.add(new_job)

    # add income types to db
    income_type = ['每日入账', '其他']
    for t in income_type:
        new_t = IncomeType(name=t)
        db.session.add(new_t)

    # add expense types to db
    expense_type = [['人工', ['工资', '加班', '预支']],
                    ['运营', ['房租', '水费', '电费', '煤气', '通讯', '汽油', '其他']],
                    ['物料', ['肉类', '海鲜', '蔬菜', '办公用品', '杂项']],
                    ['税务', ['所得税(IRS)', '增值税(IVA)', '社保(S.S)', '汽车税(IUC)', '其他']]]
    for t, l in expense_type:
        new_t = ExpenseType(name=t)
        for sub in l:
            sub_t = ExpenseType(name=sub)
            new_t.children.append(sub_t)
        db.session.add(new_t)

    # add some supplier to db
    db.session.add(Supplier(name='mil'))

    # add Admin-user
    user = User()
    user.username = 'Henrique Lin'
    user.role = 'Admin'
    user.password = bcrypt.generate_password_hash(
        'Hlin9952').decode('utf-8')
    db.session.add(user)
    db.session.commit()

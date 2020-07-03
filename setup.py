# coding:utf-8
from citywok_manager import create_app, db, bcrypt
from citywok_manager.models import Country, User, Job, Employee
import os
import shutil

app = create_app()


def clean_path(path_to_clean):
    for filename in os.listdir(path_to_clean):
        file_path = os.path.join(path_to_clean, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


with app.app_context():

    clean_path(os.path.join(app.root_path, 'download', 'employee'))
    clean_path(os.path.join(app.root_path, 'download', 'supplier'))

    # clear the database if needed
    db.drop_all()

    # create the database
    db.create_all()

    # add basic coutries into database
    countries = ['中国', '葡萄牙', '巴西', '孟加拉', '尼泊尔', '阿根廷', '巴基斯坦']
    for county in countries:
        new_country = Country(zh=county)
        db.session.add(new_country)

    jobs = ['跑堂', '大厨', '油锅', '寿司', '铁板', '沙拉', '出菜']
    for job in jobs:
        new_job = Job(name=job)
        db.session.add(new_job)

    # add Admin-user
    user = User()
    user.username = 'Henrique Lin'
    user.role = 'Admin'
    user.password = bcrypt.generate_password_hash(
        'Hlin9952').decode('utf-8')
    db.session.add(user)
    db.session.commit()

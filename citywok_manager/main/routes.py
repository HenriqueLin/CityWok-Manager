from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from citywok_manager.main.forms import AddCountryForm, AddJobForm
from citywok_manager.models import Job, Country
from citywok_manager import db

main = Blueprint('main', __name__)


@main.route("/home")
@login_required
def home():
    return render_template('home.html', title='主页')


@main.route("/setting", methods=['GET', 'POST'])
@login_required
def setting():
    add_job_form = AddJobForm()
    add_country_form = AddCountryForm()
    if request.method == 'POST':
        if 'add_job' in request.form and add_job_form.validate():
            job = Job(name=add_job_form.job.data)
            db.session.add(job)
            db.session.commit()
            flash('成功添加职务', 'success')
            return redirect(url_for('main.setting'))
        elif 'add_country' in request.form and add_country_form.validate():
            country = Country(zh=add_country_form.country.data)
            db.session.add(country)
            db.session.commit()
            flash('成功添加国家', 'success')
            return redirect(url_for('main.setting'))

    jobs = Job.query.all()
    countries = Country.query.all()
    return render_template('setting.html', title='系统设置',
                           add_job_form=add_job_form,
                           add_country_form=add_country_form,
                           jobs=jobs, countries=countries)


@main.route("/setting/delete_job/<int:job_id>", methods=['GET'])
def delete_job(job_id):
    job = Job.query.get(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('成功删除职务', 'success')
    return redirect(url_for('main.setting'))


@main.route("/setting/delete_country/<int:country_id>", methods=['GET'])
def delete_country(country_id):
    country = Country.query.get(country_id)
    db.session.delete(country)
    db.session.commit()
    flash('成功删除国家', 'success')
    return redirect(url_for('main.setting'))

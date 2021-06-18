import citywok_ms.file.messages as file_msg
from citywok_ms.auth.permissions import manager, shareholder
from citywok_ms.file.forms import FileUpdateForm
from citywok_ms.file.models import File
from flask import Blueprint, flash, redirect, render_template, url_for
from flask.helpers import send_file

file = Blueprint("file", __name__, url_prefix="/file")


@file.route("/<file_id>/download", strict_slashes=False)
@file.route("/<file_id>/download/<file_name>", strict_slashes=False)
@shareholder.require(403)
def download(file_id, file_name=None):
    f: File = File.get_or_404(file_id)
    if f.full_name != file_name:
        return redirect(
            url_for("file.download", file_id=file_id, file_name=f.full_name)
        )
    return send_file(f.path, cache_timeout=0)


@file.route("/<file_id>/delete", methods=["POST"])
@manager.require(403)
def delete(file_id):
    f: File = File.get_or_404(file_id)
    if f.delete_date:
        flash(file_msg.DELETE_DUPLICATE.format(name=f.full_name), "info")
    else:
        f.delete()
        flash(file_msg.DELETE_SUCCESS.format(name=f.full_name), "success")
    return redirect(f.owner_url)


@file.route("/<file_id>/restore", methods=["POST"])
@manager.require(403)
def restore(file_id):
    f: File = File.get_or_404(file_id)
    if not f.delete_date:
        flash(file_msg.RESTORE_DUPLICATE.format(name=f.full_name), "info")
    else:
        f.restore()
        flash(file_msg.RESTORE_SUCCESS.format(name=f.full_name), "success")
    return redirect(f.owner_url)


@file.route("/<file_id>/update", methods=["GET", "POST"])
@manager.require(403)
def update(file_id):
    f: File = File.get_or_404(file_id)
    form = FileUpdateForm()
    if form.validate_on_submit():
        f.update_by_form(form)
        flash(file_msg.UPDATE_SUCCESS.format(name=f.full_name), "success")
        return redirect(f.owner_url)
    form.file_name.data = f.base_name
    form.remark.data = f.remark
    return render_template(
        "file/update.html", title=file_msg.UPDATE_TITLE, form=form, file=f
    )

from citywok_ms import db, f_admin
from citywok_ms.auth.models import User
from citywok_ms.auth.permissions import admin
from citywok_ms.employee.models import Employee
from citywok_ms.file.models import File
from citywok_ms.supplier.models import Supplier
from flask import Blueprint, current_app
from flask_admin.contrib import sqla
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.form import SecureForm
from flask_admin.menu import MenuLink

admin_bp = Blueprint("f_admin", __name__)


class BaseView(sqla.ModelView):
    def is_accessible(self):
        return admin.can()

    form_base_class = SecureForm
    can_export = True
    column_display_pk = True
    can_view_details = True


class UserView(BaseView):
    column_exclude_list = [
        "password",
    ]
    form_excluded_columns = [
        "password",
    ]
    column_searchable_list = ["username", "email"]
    column_filters = ["role"]


f_admin.add_link(MenuLink(name="Home", url="/home"))
f_admin.add_link(MenuLink(name="Logout", url="/logout"))
f_admin.add_view(UserView(User, db.session, endpoint="_user"))
f_admin.add_view(BaseView(Employee, db.session, endpoint="_employee"))
f_admin.add_view(BaseView(Supplier, db.session, endpoint="_supplier"))
f_admin.add_view(
    BaseView(File, db.session, endpoint="_file", name="Database", category="Files")
)
f_admin.add_view(
    FileAdmin(
        current_app.config["UPLOAD_FOLDER"],
        name="Storage",
        category="Files",
        endpoint="_storage",
    )
)

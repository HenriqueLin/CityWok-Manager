from flask_admin import AdminIndexView
from citywok_ms.auth.permissions import admin


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return admin.can()

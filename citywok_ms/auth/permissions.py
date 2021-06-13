from flask_principal import Permission, RoleNeed

# needs
admin_need = RoleNeed("admin")
manager_need = RoleNeed("manager")
shareholder_need = RoleNeed("shareholder")
worker_need = RoleNeed("worker")
visitor_need = RoleNeed("visitor")

admin = Permission(admin_need)
manager = Permission(manager_need)
shareholder = Permission(shareholder_need)
worker = Permission(worker_need)
visitor = Permission(visitor_need)

from flask_babel import lazy_gettext as _l

# views' titles
INDEX_TITLE = _l("Employees")
NEW_TITLE = _l("New Employee")
DETAIL_TITLE = _l("Employee Detail")
UPDATE_TITLE = _l("Update Employee")

# flash messages
NEW_SUCCESS = _l('New employee "{name}" has been added.')
UPDATE_SUCCESS = _l('Employee "{name}" has been updated.')
ACTIVATE_SUCCESS = _l('Employee "{name}" has been activated.')
SUSPEND_SUCCESS = _l('Employee "{name}" has been suspended.')

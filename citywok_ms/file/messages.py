from flask_babel import lazy_gettext as _l

# titles
UPDATE_TITLE = _l("Update File")

# flashes
UPLOAD_SUCCESS = _l('File "{name}" has been uploaded.')
INVALID_FORMAT = _l('Invalid file format "{format}".')
NO_FILE = _l("No file has been uploaded.")
DELETE_SUCCESS = _l('File "{name}" has been deleted.')
DELETE_DUPLICATE = _l('File "{name}" has already been deleted.')
RESTORE_SUCCESS = _l('File "{name}" has been restored.')
RESTORE_DUPLICATE = _l('File "{name}" hasn\'t been deleted.')
UPDATE_SUCCESS = _l('File "{name}" has been updated.')

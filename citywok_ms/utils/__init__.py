from flask_babel import lazy_gettext as _l

SEX = [("M", _l("Male")), ("F", _l("Female"))]

ID = [
    ("passport", _l("Passport")),
    ("id_card", _l("ID Card")),
    ("green_card", _l("Permanent Resident Card")),
    ("residence_permit", _l("Residence Permit")),
    ("other", _l("Other")),
]

FILEALLOWED = tuple(
    """txt jpg jpe jpeg png gif svg bmp rtf
    odf ods gnumeric abw doc docx xls xlsx
    csv ini json plist xml yaml yml gz bz2
    zip tar tgz txz 7z pdf""".split()
)

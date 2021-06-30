import os
from citywok_ms import db
from citywok_ms.file.models import File

import datetime


def test_delete_file(client):
    f_active = File(
        full_name="active.txt",
    )
    f_recent = File(
        full_name="recent.txt",
        delete_date=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
    )
    f_old = File(
        full_name="old.txt",
        delete_date=datetime.datetime.utcnow() - datetime.timedelta(days=60),
    )
    files = [f_active, f_recent, f_old]

    db.session.add_all(files)
    db.session.commit()

    for f in files:
        open(f.path, "w").close()

    deleted_path = f_old.path

    from citywok_ms.task import delete_file

    delete_file()

    assert db.session.query(File).count() == 2
    assert db.session.query(File).filter_by(full_name="old.txt").count() == 0
    assert not os.path.isfile(deleted_path)

import os
import tempfile

from flask import current_app
from PIL import Image

from citywok_ms import db, rq
from citywok_ms.file.models import File


@rq.job
def compress_file(file_id):
    f = db.session.query(File).get(file_id)
    if f is None:
        return

    if f.format == ".pdf":
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        os.system(
            f"ps2pdf -dPDFSETTINGS=/ebook {f.path} {temp_file.name};"
            f"mv -f {temp_file.name} {f.path}"
        )

    elif f.format in [".jpg", ".jpe", ".jpeg", ".png"]:
        with Image.open(f.path) as image:
            x, y = image.size
            image = image.resize((int(x * 0.9), int(y * 0.9)), Image.ANTIALIAS)
            image.save(f.path, optimize=True, quality=85)

    f.size = os.path.getsize(f.path)
    db.session.commit()
    current_app.logger.info(f"Compress {f} to {f.size} bytes")


@rq.exception_handler
def error(job, *exc_info):
    db.session.rollback()
    job.cancel()
    current_app.logger.error(f"task {job} error.", exc_info=exc_info)
    return False

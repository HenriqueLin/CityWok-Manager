import csv
from decimal import Decimal
import io
import pandas as pd

from sqlalchemy.sql.expression import nullslast

from citywok_ms import db
from flask_wtf import FlaskForm
from sqlalchemy import Integer
from sqlalchemy.types import TypeDecorator


class SqliteDecimal(TypeDecorator):
    # This TypeDecorator use Sqlalchemy Integer as impl. It converts Decimals
    # from Python to Integers which is later stored in Sqlite database.
    impl = Integer
    cache_ok = False

    def __init__(self, scale):
        # It takes a 'scale' parameter, which specifies the number of digits
        # to the right of the decimal point of the number in the column.
        TypeDecorator.__init__(self)
        self.scale = scale
        self.multiplier_int = 10 ** self.scale

    def process_bind_param(self, value, dialect):
        # e.g. value = Column(SqliteDecimal(2)) means a value such as
        # Decimal('12.34') will be converted to 1234 in Sqlite
        if value is not None:
            value = int(Decimal(value) * self.multiplier_int)
        return value

    def process_result_value(self, value, dialect):
        # e.g. Integer 1234 in Sqlite will be converted to Decimal('12.34'),
        # when query takes place.
        if value is not None:
            value = (Decimal(value) / self.multiplier_int).quantize(
                Decimal(10) ** -self.scale
            )
        return value


class CRUDMixin(object):
    @classmethod
    def create_by_form(cls, form: FlaskForm):
        instance = cls()
        form.populate_obj(instance)
        db.session.add(instance)
        return instance

    def update_by_form(self, form: FlaskForm):
        form.populate_obj(self)

    @classmethod
    def get_all(cls, sort="id", desc=False):
        result = db.session.query(cls)
        if desc:
            result = result.order_by(nullslast(getattr(cls, sort).desc())).all()
        else:
            result = result.order_by(nullslast(getattr(cls, sort))).all()
        return result

    @classmethod
    def get_or_404(cls, id: int):
        return db.session.query(cls).get_or_404(id)

    @classmethod
    def export_to_csv(cls) -> io.BytesIO:
        sio = io.StringIO()
        writer = csv.writer(sio)
        writer.writerow(cls.columns_name.values())
        for e in cls.query.all():
            writer.writerow([getattr(e, col) or "-" for col in cls.columns_name.keys()])
        bio = io.BytesIO()
        bio.write(sio.getvalue().encode("utf_8_sig"))
        bio.seek(0)
        return bio

    @classmethod
    def export_to_excel(cls):
        bio = io.BytesIO()
        df = pd.read_sql(db.session.query(cls).statement, db.session.bind)
        df.columns = cls.columns_name.values()
        df.to_excel(bio, index=False)
        bio.seek(0)
        return bio

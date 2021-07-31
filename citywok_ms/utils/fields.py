import operator
from collections import abc
from functools import total_ordering

import six
from sqlalchemy_utils import i18n
from sqlalchemy_utils.primitives.country import Country
from sqlalchemy_utils.utils import str_coercible
from werkzeug.datastructures import FileStorage
from wtforms import MultipleFileField as _MultipleFileField
from wtforms.validators import DataRequired, StopValidation
from wtforms_components import SelectField


class BlankSelectField(SelectField):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = message
        self.choices = [("", self.messages)] + self.choices

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0] or None


class BlankCountryField(SelectField):
    def __init__(self, message, *args, **kwargs):
        kwargs["coerce"] = self.Coerce
        super(BlankCountryField, self).__init__(*args, **kwargs)
        self.choices = self._get_choices
        self.m = message

    def _get_choices(self):
        # Get all territories and filter out continents (3-digit code)
        # and some odd territories such as "Unknown or Invalid Region"
        # ("ZZ"), "European Union" ("QU") and "Outlying Oceania" ("QO").
        territories = [
            (code, name)
            for code, name in six.iteritems(i18n.get_locale().territories)
            if len(code) == 2 and code not in ("QO", "QU", "ZZ")
        ]
        return [("", self.m)] + sorted(territories, key=operator.itemgetter(1))

    @staticmethod
    def Coerce(value):
        if value == "":
            return None
        else:
            return BlankCountry(value)


@total_ordering
@str_coercible
class BlankCountry(Country):
    def __init__(self, code_or_country):
        super(BlankCountry, self).__init__(code_or_country)

    @classmethod
    def validate(self, code):
        try:
            i18n.babel.Locale("en").territories[code]
        except KeyError:  # test: no cover
            if code == "":
                pass
            else:
                raise ValueError(
                    "Could not convert string to country code: {0}".format(code)
                )


class MultipleFileField(_MultipleFileField):
    """Werkzeug-aware subclass of :class:`wtforms.fields.MultipleFileField`."""

    def process_formdata(self, valuelist):
        valuelist = (x for x in valuelist if isinstance(x, FileStorage) and x)
        data = list(valuelist) or None

        if data is not None:
            self.data = data
        else:  # test: no cover
            self.raw_data = ()


class FilesRequired(DataRequired):
    """Validates that all entries are Werkzeug
    :class:`~werkzeug.datastructures.FileStorage` objects.
    :param message: error message
    You can also use the synonym ``files_required``.
    """

    def __call__(self, form, field):
        if not (
            field.data and all(isinstance(x, FileStorage) and x for x in field.data)
        ):
            raise StopValidation(
                self.message or field.gettext("This field is required."),
            )


files_required = FilesRequired


class FilesAllowed(object):
    """Validates that all the uploaded files are allowed by a given list of
    extensions or a Flask-Uploads :class:`~flaskext.uploads.UploadSet`.
    :param upload_set: A list of extensions or an
        :class:`~flaskext.uploads.UploadSet`
    :param message: error message
    You can also use the synonym ``files_allowed``.
    """

    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        if not (
            field.data and all(isinstance(x, FileStorage) and x for x in field.data)
        ):
            return  # test: no cover

        for data in field.data:
            filename = data.filename.lower()

            if isinstance(self.upload_set, abc.Iterable):
                if any(filename.endswith("." + x) for x in self.upload_set):
                    continue

                raise StopValidation(
                    self.message
                    or field.gettext(
                        "File does not have an approved extension: {extensions}"
                    ).format(extensions=", ".join(self.upload_set))
                )  # test: no cover

            if not self.upload_set.file_allowed(data, filename):  # test: no cover
                raise StopValidation(
                    self.message
                    or field.gettext("File does not have an approved extension.")
                )


files_allowed = FilesAllowed

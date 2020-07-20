from flask_babel import lazy_gettext as _
from wtforms import ValidationError

from zopsedu.lib.helpers import ALLOWED_EXTENSIONS


class LessThan(object):
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """

    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Geçersiz alan ismi: '%s'.") % self.fieldname)
        if field.data >= other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            message = self.message
            if message is None:
                message = field.gettext(
                    'Alan değeri %(other_name) alan değerinden küçük olmalıdır.')

            raise ValidationError(message % d)


class FileExtensionRestriction(object):
    """
        File uzantısı kontrol etmek icin kullanılır.
        File yuklenmemiş ise hata dönmez.
    """

    def __init__(self, error_message, allowed_extentions=ALLOWED_EXTENSIONS):
        self.allowed_extentions = allowed_extentions
        self.error_message = error_message

    def __call__(self, form, field):
        from flask import request
        file = request.files.get(field.name)
        if file:
            file_mimetype = file.mimetype
            if file_mimetype not in self.allowed_extentions.values():
                raise ValidationError(self.error_message)


class FileRequired(object):
    """
    Filerequired validator
    """

    def __init__(self, error_message=_("Dosya yüklemek zorundasınız")):
        self.error_message = error_message

    def __call__(self, form, field):
        from flask import request
        file = request.files.get(field.name)
        if not file:
            raise ValidationError(self.error_message)


class CustomFileFieldRequired(object):
    """
    Custom file field required validator
    Custom file fieldin bulundugu forma daha önce bir dosya kaydedilmiş ise guncellenecegi zaman
    file id hidden input value olarak gelir. Validator yazilirken ve kullanılırken buna dikkat
    edilmelidir
    """

    def __init__(self, error_message=_("Dosya yüklemek zorundasınız")):
        self.error_message = error_message

    def __call__(self, form, field):
        from flask import request
        file = request.files.get(field.name)
        field_data = field.data
        if not file and not field_data:
            raise ValidationError(self.error_message)


class DecimalLength(object):
    def __init__(self, max_length, error_message=_("Alan limiti aşıldı")):
        self.error_message = error_message
        self.max_length = max_length

    def __call__(self, form, field):
        try:
            string_data = str(field.data)
            # wtform decimal fielddan gelen degeri stringe cevirip virgulden onceki
            # kismin uzunluguna bakılır
            data_length = len(string_data.split(".")[0])
        except KeyError:
            raise ValidationError("Geçersiz sayi formatı")
        if data_length > self.max_length:
            raise ValidationError(self.error_message)

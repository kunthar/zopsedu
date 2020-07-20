"""Helper Siniflari"""
import enum
from PIL import Image

from flask_babel import LazyString
from depot.fields.upload import UploadedFile
from depot.io import utils
from depot.io.interfaces import FileStorage
from flask_babel import gettext as _

ALLOWED_EXTENSIONS = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'excel': 'application/excel',
    'xls': 'application/vnd.ms-excel',
    'x-excel': 'application/x-excel',
    'odg': 'application/vnd.oasis.opendocument.graphics',
    'odt': 'application/vnd.oasis.opendocument.text',
    'odp': 'application/vnd.oasis.opendocument.presentation',
    'ods': 'application/vnd.oasis.opendocument.spreadsheet',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'png': 'image/png',
    'jpeg': 'image/jpeg',
    'jfif': 'image/pjpeg',
    'bmp': 'image/bmp',
    'xbm': 'image/x-windows-bmp'
}
SABLON_FILE_EXTENTIONS = {
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'xls': 'application/vnd.ms-excel',
    'odt': 'application/vnd.oasis.opendocument.text',
    'ods': 'application/vnd.oasis.opendocument.spreadsheet'
}


class UploadedImageWithMaxDimensions(UploadedFile):
    """
    Yuklenen resmin dimensionlarina gore kontrol yapar
    """
    max_width = 1024
    max_height = 1024
    accepted_file_types = ["image/png", "image/jpeg"]

    def process_content(self, content, filename=None, content_type=None):
        """process_content"""
        __, filename, content_type = FileStorage.fileinfo(content)

        # Get a file object even if content was bytes
        content = utils.file_from_content(content)

        uploaded_image = Image.open(content)
        width, height = uploaded_image.size
        if content_type not in self.accepted_file_types:
            raise ValueError(_("Yüklenen resim bu dosya türlerinden biri olmalıdır : {}".format(
                ', '.join([i.split('/')[1] for i in self.accepted_file_types]))))
        if width > self.max_width or height > self.max_height:
            raise ValueError(_(f"Yüklenen resim boyutu {self.max_width}x{self.max_height}"
                               f" pikselden büyük olamaz."))

        content.seek(0)
        super(UploadedImageWithMaxDimensions, self).process_content(content,
                                                                    filename,
                                                                    content_type)


class LimitedSizeUploadedFile(UploadedFile):
    """
    Yuklenen resmin sizena gore kontrol yapar
    """

    max_size = 102400

    def process_content(self, content, filename=None, content_type=None):
        """process_content"""
        __, filename, content_type = FileStorage.fileinfo(content)

        # Get a file object even if content was bytes
        content = utils.file_from_content(content)
        content.seek(0, 2)
        if content.tell() >= self.max_size:
            raise ValueError(_(f"Yüklenen resim boyutu {self.max_size/1024} KB büyük olamaz."))
        content.seek(0)
        super(LimitedSizeUploadedFile, self).process_content(content,
                                                             filename,
                                                             content_type)


class AllowedUploadedFile(UploadedFile):
    """
    Yuklenebilecek dosya turlerine gore kontrol yapar.
    """

    def process_content(self, content, filename=None, content_type=None):
        """process_content"""
        __, filename, content_type = FileStorage.fileinfo(content)

        if content_type not in ALLOWED_EXTENSIONS.values():
            raise ValueError(_(f"Yüklenen dosya uygun formatta değildir."))

        super(AllowedUploadedFile, self).process_content(content,
                                                         filename,
                                                         content_type)


# todo: daha genel biryere taşınmasi gerekiyor.
class WTFormEnum(enum.Enum):
    """
    wtform enum class
    """

    @classmethod
    def choices(cls):
        """Choices"""
        return [(choice, choice.value) for choice in cls]

    @classmethod
    def coerce(cls, item):
        """Coerce"""
        if type(item) == cls:
            return item

        for key, value in cls.__members__.items():
            if key == item:
                return cls[item]
            elif value == item:
                return cls(item)

    def __str__(self):
        """Str"""
        return self.name


def form_errors_dict_to_set(error_dict, errors):
    """
    Formdan gelen hata stringlerini alip "errors" isimli set turunde degiskene ekler.
    Bu degiskenin fonksiyonun cagrildigi yerde bulunmasi gerekir

    :param error_dict: formdan gelen errors dict. form.errors
    :param errors: localde hatalarin tutuldugu "set" turundeki degisken
    """
    for key, value in error_dict.items():
        if isinstance(value, dict):
            form_errors_dict_to_set(value, errors)
        elif isinstance(value, list):
            for error in value:
                if isinstance(error, str) or isinstance(error, LazyString):
                    errors.add(error)
                else:
                    form_errors_dict_to_set(error, errors)
        else:
            errors.add(value)

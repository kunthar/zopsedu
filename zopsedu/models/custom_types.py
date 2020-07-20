"""
Özel olarak yarattıgımız sqlalchemy tiplerini kaydetmek için kullanırız.
"""
import simplejson
from sqlalchemy.ext import mutable
from sqlalchemy.types import TypeDecorator, Text


# pylint: disable=abstract-method
class JSONEncodedDict(TypeDecorator):
    """
    Özel json tip. JSON değerler orm seviyesinde kullanır database e Text olarak kaydedilir.
    """
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = simplejson.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = simplejson.loads(value)
        return value
# pylint: enable=abstract-method


class JSONEncodedList(TypeDecorator):
    """
    Listeler icin ozel json tip. JSON değerler orm seviyesinde kullanılır, veritabanina
    Text olarak kaydedilir.
    """
    impl = Text

    @property
    def python_type(self):
        pass

    def process_literal_param(self, value, dialect):
        pass

    def process_result_value(self, value, dialect):
        if value is not None:
            value = simplejson.loads(value)
        return value

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = simplejson.dumps(value)
        return value


mutable.MutableDict.associate_with(JSONEncodedDict)
mutable.MutableList.associate_with(JSONEncodedList)

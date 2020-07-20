"""Genel Hata Siniflari"""


class ZopseduModelValueError(ValueError):
    """Validation gecemeyen model verileri icin exception."""
    def __init__(self, *args, field_name, **kwargs):
        self.field_name = field_name
        super().__init__(*args, **kwargs)

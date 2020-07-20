"""Decorators"""
from functools import wraps

SIGNAL_LISTENERS = {}


def signal_listener(name):
    """registers decorated methods to SIGNAL_LISTENERS dict"""
    if name not in SIGNAL_LISTENERS:
        SIGNAL_LISTENERS[name] = []

    def true_decorator(func):
        """real decorator"""
        SIGNAL_LISTENERS[name].append(func)

        @wraps(func)
        def wrapped(*args, **kwargs):
            """wrapped"""
            ret = func(*args, **kwargs)
            return ret
        return wrapped
    return true_decorator


def no_crud_log(cls):
    """
    Set False crud_log attr to disable logging crud events
    Args:
        cls: data model class

    Returns:
        data model class
    """
    cls.crud_log = False
    return cls

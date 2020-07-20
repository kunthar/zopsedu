"""REST API modulu"""
import flask_restless
from sqlalchemy.exc import SQLAlchemyError


def build_api(app):
    """
    from https://stackoverflow.com/a/26518401/3986439
    Args:
        app:

    Returns:

    """
    from zopsedu.lib.db import BASE_MODEL, DB

    url_prefix = "/v1/api"
    manager = flask_restless.APIManager(app, flask_sqlalchemy_db=DB)

    classes, models, table_names = [], [], []

    for clazz in BASE_MODEL._decl_class_registry.values():  # pylint: disable=protected-access
        try:
            table_names.append(clazz.__tablename__)
            classes.append(clazz)
        except AttributeError:
            pass
        except SQLAlchemyError:
            pass

    for table in BASE_MODEL.metadata.tables.items():
        if table[0] in table_names:
            models.append(classes[table_names.index(table[0])])

    assert classes == models, 'Esit degil'

    for mod in models:
        manager.create_api(mod, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                           url_prefix=url_prefix)

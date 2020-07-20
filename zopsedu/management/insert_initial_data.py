"""Insert Initial Data"""
import importlib
import os
import json
from flask_script import Command

from zopsedu.lib.db import DB
from zopsedu.fixture.file_list import FILE_LIST


class InsertInitialData(Command):
    """Inserts initial data"""

    # pylint: disable=method-hidden
    def run(self):
        """
            Inserts data into db from given json paths.
        """
        session = DB.session
        data_path = os.path.abspath('.') + '/fixture/initial_data'
        # data = sorted(os.listdir(data_path))

        # pylint: disable=broad-except
        if FILE_LIST:
            for file in FILE_LIST:
                data = json.load(open(data_path + '/' + file))
                for key, val in data.items():
                    models = importlib.import_module('zopsedu.models')
                    class_name = getattr(models, key.title().replace('_', ''))
                    dc = session.query(class_name).count()
                    update_data = data[key][:dc+1]
                    insert_data = data[key][dc+1:]
                    session.bulk_insert_mappings(class_name, insert_data)
                    for i in update_data:
                        obj = class_name(**i)
                        session.merge(obj)
                        session.flush()
                    if 'id' in class_name.__table__.columns.keys():
                        session.execute(
                            "select setval('{0}_id_seq',"
                            "(select max(id) from {0}) + 1);".format(class_name.__tablename__))

            # pylint: enable=broad-except
        session.commit()
        session.close()
        # pylint: enable=method-hidden

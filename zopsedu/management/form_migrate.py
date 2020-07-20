"""Zopsedu Management Commands"""
import os
import importlib
import inspect
from flask_script import Command, Option
from sqlalchemy.exc import IntegrityError
from wtforms.form import Form
from redis.exceptions import RedisError

from zopsedu.server import app
from zopsedu.lib.db import DB
from zopsedu.models.form import Form as FormModel


CACHE = app.extensions['redis']


class MigrateForms(Command):
    """Form migrater, discover forms and persist them into database"""
    option_list = (
        Option('--path', '-p', dest='path'),
    )

    CACHE_PREFIX = app.config['CACHE_FORM_PREFIX']

    def save_form(self, frm_cls, import_path, session, pipe):
        """
        If given cls is a subclass of wtforms.form.Form saves it to both CACHE
        and db via pipe and session objects.
        Args:
            frm_cls: class object can be any class
            import_path (str):
            session:
            pipe:

        Returns:

        """
        try:
            if frm_cls is not Form and issubclass(frm_cls, Form) and hasattr(
                    frm_cls.Meta,
                    'will_explored') and frm_cls.Meta.will_explored:
                pipe.set(
                    self.CACHE_PREFIX.format(form_name=frm_cls.Meta.form_name),
                    import_path
                )
                form = FormModel()
                form.form_name = frm_cls.Meta.form_name
                form.form_type = frm_cls.Meta.form_type
                form.form_module = frm_cls.Meta.form_module
                form.form_class_name = frm_cls.__name__
                form.form_import_path = import_path
                form.will_explored = frm_cls.Meta.will_explored
                form.will_listed = frm_cls.Meta.will_listed
                session.merge(form)

        except TypeError as exc:
            app.logger.error(
                "Type Error while trying to detect "
                "wtforms.form.Form classes: %s", exc)

    def save(self, import_path, session, pipe):
        """
        Traverses the classes in the `import_path` and sends them to the save
        form method.
        Args:
            import_path(str):
            session: db.session
            pipe: redis pipeline object

        Returns:

        """
        try:
            imported_module = importlib.import_module(import_path)
            clsmembers = inspect.getmembers(imported_module,
                                            inspect.isclass)
            for _, cls in clsmembers:
                self.save_form(cls, cls.__module__, session, pipe)

        except AttributeError as exc:
            app.logger.error(
                "Attribute Error while trying to detect "
                "wtforms.form.Form classes: %s", exc)

    @staticmethod
    def get_import_path(dir_path, file_name, len_abs_prefix):
        """
        Gets directory path and file name and returns a full path to import.
        Args:
            dir_path (str): directory path
            file_name (str): file name
            len_abs_prefix (int): length of the absolute prefix to reach the
                relative import path.
                E.g. for "/Users/crazy/zopsedu", len("/Users/crazy/")

        Returns:
            str: Path to import.
        """
        full_pathname = os.path.join(dir_path, file_name)
        # always 3 for the ".py"  extension.
        path_without_extension = full_pathname[:-3]
        # removes the absolute path prefix
        path_without_absolution = path_without_extension[len_abs_prefix:]
        # Converts "zopsedu/auth/models/auth" to "zopsedu.auth.models.auth"
        return '.'.join(path_without_absolution.split('/'))

    # pylint: disable=arguments-differ, method-hidden
    def run(self, path):
        """
        migrate_forms command's run method.
        Args:
            path (str): path to zopsedu module.

        Returns:

        """
        full_base_path_name = os.path.abspath(path)
        if full_base_path_name[-7:] != "zopsedu":
            raise KeyError("Invalid path!")

        _, del_keys = CACHE.scan(match=self.CACHE_PREFIX.format(form_name="*"))
        if del_keys:
            CACHE.delete(*del_keys)

        pipe = CACHE.pipeline()
        sess = DB.session
        sess.query(FormModel).delete()

        for dirpath, _, filenames in os.walk(full_base_path_name):
            if not dirpath == os.path.abspath('.') + '/migrations':
                for filename in filenames:
                    if filename.endswith('.py'):
                        path_to_import = self.get_import_path(
                            dirpath, filename, len(full_base_path_name[:-7]))
                        self.save(path_to_import, sess, pipe)

        try:
            pipe.execute()
            sess.commit()
        except IntegrityError as exc:
            app.logger.error(
                "Integrity Error occured while commiting. Some "
                "of the rows may already be written. %s", exc)
        except RedisError as exc:
            app.logger.error(
                "Redis Error occurred while executing the pipeline. %s", exc)
        finally:
            app.logger.info("Migration of forms finished!")
    # pylint: enable=arguments-differ, method-hidden

"""DB event listeners"""
from datetime import datetime

from flask import session
from flask_login import current_user
from sqlalchemy import event

from zopsedu.lib.db import BASE_MODEL, DB
from zopsedu.models.activity_log import AktiviteKaydi, CrudKaydi, CrudLogAction


def make_single_item_crud_log(conn, target, action):
    """Bulk olmayan operasyonlar icin log kaydi ureten fonksiyon"""
    table = CrudKaydi.__table__
    conn.execute(
        table.insert(),
        context=session.get('activity_context'),
        user_id=current_user.id,
        user_role_id=session.get('current_user_role'),
        role_id=session.get('current_role'),
        zaman=datetime.now(),
        nesne=target.__class__.__name__,
        nesne_id=target.id,
        aksiyon=action
    )


def make_multi_item_crud_log(sess, target, action, rows):
    """Bulk operasyonlar icin log kaydi ureten fonksiyon"""
    # pylint: disable=bare-except
    try:
        name = target.__name__
    except:
        name = target.__class__.__name__
    # pylint: enable=bare-except

    sess.add(
        CrudKaydi(
            context=session.get('activity_context'),
            user_id=current_user.id,
            user_role_id=session.get('current_user_role'),
            role_id=session.get('current_role'),
            zaman=datetime.now(),
            nesne=name,
            nesne_ids=rows,
            nesne_sayi=len(rows),
            aksiyon=action
        )
    )
    sess.commit()


# pylint: disable=unused-argument
def after_insert_listener(mapper, connection, target):
    """Insert hook"""
    if target.crud_log:
        make_single_item_crud_log(connection, target, CrudLogAction.insert)


def after_update_listener(mapper, connection, target):
    """update hook"""
    if target.crud_log:
        make_single_item_crud_log(connection, target, CrudLogAction.update)


def after_delete_listener(mapper, connection, target):
    """delete hook"""
    if target.crud_log:
        make_single_item_crud_log(connection, target, CrudLogAction.delete)


# pylint: enable=unused-argument

def after_bulk_update_listener(update_context):
    """bulk update hook"""
    if update_context.mapper.entity.crud_log:
        if hasattr(update_context, 'matched_rows'):
            matched_rows = [row[0] for row in update_context.matched_rows]
        else:
            matched_rows = list(update_context.result.context.compiled_parameters[0].values())

        make_multi_item_crud_log(update_context.session, update_context.mapper.entity,
                                 CrudLogAction.update, matched_rows)


def after_bulk_delete_listener(delete_context):
    """bulk delete hook"""
    if delete_context.mapper.entity.crud_log:
        if hasattr(delete_context, 'matched_rows'):
            matched_rows = [row[0] for row in delete_context.matched_rows]
        else:
            matched_rows = list(delete_context.result.context.compiled_parameters[0].values())
        make_multi_item_crud_log(delete_context.session, delete_context.mapper.entity,
                                 CrudLogAction.delete, matched_rows)


def register_db_event_listeners():
    """listenerlari sqlalchemy'e kaydeder"""
    event.listen(BASE_MODEL, 'after_insert', after_insert_listener, propagate=True)
    event.listen(BASE_MODEL, 'after_update', after_update_listener, propagate=True)
    event.listen(BASE_MODEL, 'after_delete', after_delete_listener, propagate=True)
    event.listen(DB.session, 'after_bulk_delete', after_bulk_delete_listener, propagate=True)
    event.listen(DB.session, 'after_bulk_update', after_bulk_update_listener, propagate=True)

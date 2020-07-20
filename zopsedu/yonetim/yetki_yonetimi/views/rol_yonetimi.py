""" Rol Yonetim Modülü """
import json

from flask import render_template, request, current_app, jsonify
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import UnmappedInstanceError

from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models import Role, Permission as PermissionModel, RolePermission
from zopsedu.auth.lib import build_permission_tree, auth, Permission
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.yonetim.yetki_yonetimi.forms import RolEkleForm


class RolView(FlaskView):
    """Rol Yönetimi View Class"""

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["yetki_yonetimi"]["rol_yetkilendirme"]),
                   menu_registry={'path': '.yonetim.yetki_yonetimi.rol_yetkilendirme',
                                  'title': _("Rol Yetkilendirme")})
    @route('/', methods=['GET'])
    def rolleri_listele():

        """Rol ekleme, listeleme, düzenleme ve silme işlemlerinin yapıldığı view metodudur"""
        qry = DB.session.query(Role).all()
        return render_template("rol_listeleme.html", results=qry)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["yetki_yonetimi"]["rol_yetkilendirme"]))
    @route('/yeni-rol', methods=['GET'], endpoint='yeni_rol_get')
    def rol_ekle_get():
        """Rol ekleme sayfasının oluşturulduğu view metodudur"""
        permission_tree = build_permission_tree()
        rol_ekle_form = RolEkleForm()
        return render_template("rol_ekle.html", form=rol_ekle_form,
                               tree=json.dumps(permission_tree))

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["yetki_yonetimi"]["rol_yetkilendirme"]))
    @route('/yeni-rol', methods=['POST'], endpoint='yeni_rol_ekle')
    def rol_ekle_set():
        """Request bodysinde gelen rolün veritabanına kaydedildiği metottur."""
        selected_permissions = set(request.get_json().get('selected_permissions', []))
        updated_rol_name = request.get_json().get('rol_adi')
        permissions_to_add_ids = [ptoa[0] for ptoa in
                                  PermissionModel.query.with_entities(PermissionModel.id).filter(
                                      PermissionModel.name.in_(selected_permissions)).all()]
        try:
            rol = Role(name=updated_rol_name)
            DB.session.add(rol)
            DB.session.commit()
            if permissions_to_add_ids:
                for perm in permissions_to_add_ids:
                    DB.session.add(RolePermission(role_id=rol.id, permission_id=perm))
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get(
                    "yeni_rol_ekle").type_index,
                "nesne": 'Role',
                "nesne_id": rol.id,
                "ekstra_mesaj": "Yeni rol eklendi: {}".format(rol.name),
            }
            signal_sender(**signal_payload)

        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler()

            return jsonify(status="error"), 400
        return jsonify(status="success")

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["yetki_yonetimi"]["rol_yetkilendirme"]))
    @route('/<int:role_id>', methods=['GET'], endpoint='rol_duzenle_get')
    def rol_duzenle_get(role_id):
        """
        Rol düzenleme işinin yapıldığı, rolün sahip olacağı permissionların düzenlendiği view

        Args:
            role_id (int):

        Returns:

        """
        rol = Role.query.get(role_id)
        permission_tree = build_permission_tree(rol.permissions)
        rol_ekle_form = RolEkleForm()
        rol_ekle_form.rol_adi.data = rol.name
        return render_template("rol_duzenleme.html", form=rol_ekle_form,
                               rol=rol,
                               tree=json.dumps(permission_tree))

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["yetki_yonetimi"]["rol_yetkilendirme"]))
    @route('/<int:role_id>', methods=['POST'], endpoint='rol_duzenle')
    def rol_duzenle(role_id):
        """
        Rol düzenlemesi sonucunda değişen rolü veritabanına kaydeden view.

        """
        rol = Role.query.get(role_id)
        permission_groups = set(
            [grp[0] for grp in DB.session.query(PermissionModel.group).distinct().all()])
        existing_permissions = set([perm.name for perm in rol.permissions])
        selected_permissions = set(request.get_json().get('selected_permissions', []))
        updated_rol_name = request.get_json().get('rol_adi')

        permissions_to_delete = existing_permissions.difference(selected_permissions)
        permissions_to_add = selected_permissions.difference(existing_permissions).difference(
            permission_groups)

        permissions_to_delete_ids = [ptod[0] for ptod in
                                     PermissionModel.query.with_entities(PermissionModel.id).filter(
                                         PermissionModel.name.in_(permissions_to_delete)).all()]

        permissions_to_add_ids = [ptoa[0] for ptoa in
                                  PermissionModel.query.with_entities(PermissionModel.id).filter(
                                      PermissionModel.name.in_(permissions_to_add)).all()]
        pipe = current_app.extensions['redis'].pipeline()
        try:
            if updated_rol_name and updated_rol_name != rol.name:
                rol.name = updated_rol_name
                DB.session.add(rol)

            if permissions_to_delete_ids:
                RolePermission.query.filter(
                    RolePermission.permission_id.in_(permissions_to_delete_ids),
                    RolePermission.role_id == rol.id
                ).delete(synchronize_session='fetch')

                pipe.srem(
                    current_app.config['ROLES_PERMISSIONS_CACHE_KEY'].format(
                        role_id=role_id), *permissions_to_delete
                )

            if permissions_to_add_ids:
                for ptoaid in permissions_to_add_ids:
                    DB.session.add(RolePermission(role_id=rol.id, permission_id=ptoaid))

                pipe.sadd(
                    current_app.config['ROLES_PERMISSIONS_CACHE_KEY'].format(
                        role_id=role_id), *permissions_to_add
                )

            DB.session.commit()
            pipe.execute()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get(
                    "rol_guncelle").type_index,
                "nesne": 'Rol',
                "nesne_id": rol.id,
                "ekstra_mesaj": "{} adlı kullanıcı {} id'li rolu guncelledi.".format(
                    current_user.username, rol.id)
            }
            signal_sender(**signal_payload)
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler()

            return jsonify(status="error"), 400
        return jsonify(status="success")

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["yetki_yonetimi"]["rol_yetkilendirme"]))
    @route('/<int:role_id>', methods=['DELETE'], endpoint='rol_sil')
    def rol_sil(role_id):
        """
        Rol silme işini yapan view metodu.
        Args:
            role_id:

        Returns:

        """
        try:
            Role.query.filter_by(id=role_id).delete()
            DB.session.commit()
            payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get("rol_sil").type_index,
                "nesne": "Rol",
                "nesne_id": role_id,
                "ekstra_mesaj": "{} isimli kullanıcı {} id'li rolu sildi.".format(
                    current_user.username, role_id),
                "notification_receiver": current_user.person.personel.id,
                "notification_title": "Rol silme başarılı",
            }
            # todo: notification mesajinda id(name kullanilabilir) var kullanici icin anlamli degil.
            ntf_message = "Rol silme başarılı. {} idli rol başarıyla kaldırıldı.".format(role_id)
            signal_sender(notification=True, notification_message=ntf_message, **payload)
            return jsonify(status="success")

        except UnmappedInstanceError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler()
        except IntegrityError as exc:
            # todo permission, user, gibi role ile alakalı modellerin listelerini döndür
            DB.session.rollback()
            CustomErrorHandler.error_handler()
            return jsonify(status="error"), 409
        return jsonify(status="error"), 400

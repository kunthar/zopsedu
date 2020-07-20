"""File Views Modülü"""
# pylint: disable=broad-except
from flask_babel import lazy_gettext as _
from flask import request, jsonify, current_app, send_file, Response
from flask_classful import FlaskView, route
from flask_login import current_user
from sqlalchemy.orm.exc import NoResultFound

from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models import File
from zopsedu.lib.db import DB
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


class FileView(FlaskView):
    """File View"""
    route_base = "/file"

    DOWNLOAD_URL = route_base + "/download/{}"
    DELETE_URL = route_base + "/delete/{}"
    DELETE_TYPE = "DELETE"

    @staticmethod
    @route('/upload', methods=['HEAD'])
    def file_upload_head():
        """
        Dosya yükleme cors check.

        Returns: 200

        """
        return Response()

    @route('/upload', methods=['POST'])
    def file_upload(self):
        """
        Dosya yüklemek  için kullanılır.
        jquery file upload ui kütüphanesine göre değer dönülür.

        Returns:

        """

        if len(request.files) > 1 or len(request.files) < 1:
            return jsonify({"error": _("Sadece 1 tane dosya yükleyebilirsiniz.")})
        files = list(request.files.values())
        file = File(content=files[0],
                    user_id=current_user.id)
        try:
            DB.session.add(file)
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("common").get("dosya_yuklendi").type_index,
                "nesne": 'File',
                "nesne_id": file.id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} adıyla yeni dosya yükledi.".format(
                    current_user.username,
                    file.content.filename)
            }
            signal_sender(**signal_payload)
        except Exception as exc:
            CustomErrorHandler.error_handler()
            return jsonify({"files": [{"error": _("Dosya Yüklenemedi"),
                                       "name": files[0].filename}]})
        return jsonify({"files": [{"name": file.content.filename,
                                   "type": file.content.content_type,
                                   "url": self.DOWNLOAD_URL.format(file.id),
                                   "deleteUrl": self.DELETE_URL.format(file.id),
                                   "deleteType": "DELETE",
                                   "fileId": file.id}]})

    @staticmethod
    @route('/download/<int:file_id>', methods=['GET'])
    def file_download(file_id):
        """
        Dosya indirmek için kullanılır.
        jquery file upload ui kütüphanesine göre değer dönülür.
        Args:
            file_id: dosya id

        Returns:

        """
        try:
            file = DB.session.query(File).filter_by(id=file_id).one()
        except NoResultFound:
            return jsonify({"files": [{"error": _("Dosya Bulunamadi")}]})
        except Exception as exc:
            CustomErrorHandler.error_handler()
            return jsonify({"files": [{"error": _("Bir Hata Olustu Daha Sonra Tekrar Deneyiniz")}]})

        return send_file(
            file.file_object,
            as_attachment=True,
            attachment_filename=file.content.filename,
            mimetype=file.content.content_type
        )

    @staticmethod
    @route('/delete/<int:file_id>', methods=[DELETE_TYPE])
    def file_delete(file_id):
        """
        Dosya silmek için kullanılır.
        jquery file upload ui kütüphanesine göre değer dönülür.
        Args:
            file_id: dosya id

        Returns: {filename: "True"}

        """
        try:
            file = DB.session.query(File).filter_by(id=file_id).one()
            filename = file.content.filename
            DB.session.delete(file)
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("common").get("dosya_sil").type_index,
                "nesne": 'File',
                "nesne_id": file_id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} adlı dosyayı sildi.".format(
                    current_user.username, filename)
            }
            signal_sender(**signal_payload)
        except NoResultFound:
            return jsonify({"files": [{"error": "dosya bulunamadi"}]})
        except Exception as exc:
            CustomErrorHandler.error_handler()
            return jsonify({"error": _("Bir Hata Olustu Daha Sonra Tekrar Deneyiniz")})

        return jsonify({filename: "True"})

    @route('/information/<int:file_id>', methods=['GET'], endpoint='file_information')
    def file_information(self, file_id):
        """
        Dosya hakkında bilgi almak için kullanılır
        Args:
            file_id: dosya id

        Returns:{"name": "dosya adı",
                "type": "image/png",
                "uploadedAt": "2018-03-29 06:51:30",
                "url": "/file/download/{}".format(file_id),
                "deleteUrl": "/file/delete/{}".format(file_id),
                "deleteType": "DELETE"}

        """
        try:
            file = DB.session.query(File).filter_by(id=file_id).one()
        except NoResultFound:
            return jsonify({"files": [{"error": _("Dosya Bulunamadi")}]})
        except Exception as exc:
            CustomErrorHandler.error_handler()
            return jsonify({"error": _("Bir Hata Olustu Daha Sonra Tekrar Deneyiniz")})

        return jsonify({"name": file.content.filename,
                        "type": file.content.content_type,
                        "uploadedAt": file.content.uploaded_at,
                        "url": self.DOWNLOAD_URL.format(file_id),
                        "deleteUrl": self.DELETE_URL.format(file_id),
                        "deleteType": self.DELETE_TYPE})

"""Zopsedu auth module which contains basic auth models and methods"""
import enum

from depot.fields.sqlalchemy import UploadedFileField
from flask import session
from flask_login.mixins import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, Enum
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.lib.helpers import LimitedSizeUploadedFile


class RolTipleri(str, enum.Enum):
    """Rol Tiplerini temsil eden enum class"""

    personel = "Personel"
    ogrenci = "Ogrenci"
    harici = "Harici"
    firma = "Firma"


# resmi yeniden boyutlandirmak icin kullanilabilir. pillow kutuphanesi gerektirir.
# # taken from: https://depot.readthedocs.io/en/latest/database.html#custom-attachments
# class UploadedImageWithMaxHWSize(UploadedFile):
#     """
#     Yuklenen Resmin HeightxWidth kontrolunu yapar ve istenilenden buyukse boyutunu kucultur.
#     """
#     max_size = 1024
#
#     def process_content(self, content, filename=None, content_type=None):
#         # As we are replacing the main file, we need to explicitly pass
#         # the filename and content_type, so get them from the old content.
#         __, filename, content_type = FileStorage.fileinfo(content)
#
#         # Get a file object even if content was bytes
#         content = utils.file_from_content(content)
#
#         uploaded_image = Image.open(content)
#         if max(uploaded_image.size) >= self.max_size:
#             uploaded_image.thumbnail((self.max_size, self.max_size),
#                                      Image.BILINEAR)
#             content = SpooledTemporaryFile(INMEMORY_FILESIZE)
#             uploaded_image.save(content, uploaded_image.format)
#
#         content.seek(0)
#         super(UploadedImageWithMaxHWSize, self).process_content(content,
#                                                                 filename,
#                                                                 content_type)
#

class UploadedAvatar(LimitedSizeUploadedFile):
    """
    Yuklenen resmin sizena gore kontrol yapar
    """

    max_size = 102400


class User(BASE_MODEL, ZopseduBase, UserMixin):
    """Simple user data model"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    password = Column(String(255))
    email = Column(String(255), unique=True)
    profile_photo = Column(
        UploadedFileField(upload_storage="local", upload_type=UploadedAvatar))
    avatar = Column(UploadedFileField(
        upload_type=UploadedAvatar))  # default upload storage kullanilir.

    durumu = Column(Boolean, default=True)
    session_id = Column(String(500))
    roles = relationship("Role", secondary="user_roles")
    person = relationship("Person", uselist=False)
    ozgecmis = relationship("Ozgecmis", uselist=False)

    # s3 tanimlanmis ise bu sekilde kullanilabilir
    # avatar = Column(UploadedFileField(upload_storage="s3"))

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def is_authenticated(self):
        return session.get('is_authenticated', False)

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return session.get('is_anonymous', False)

    def get_role(self, role_id):
        """
        User'in rolleri icinden verilen id'ye sahip rolü döndürür.
        Args:
            role_id(str):

        Returns:
            Role or None
        """
        if isinstance(role_id, str):
            role_id = int(role_id)
        role = Role.query.filter_by(id=role_id).first()
        return role


def load_user(user_id):
    """
    Flask-Login user loader callback.
    Args:
        user_id (str):

    Returns:

    """
    return User.query.filter_by(id=user_id).first()


class Role(BASE_MODEL, ZopseduBase):
    """
    Role data modeli
    Rol modeli yetkilerin gruplandığı temel role modelidir.
    """
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    users = relationship("User", secondary="user_roles")
    permissions = relationship("Permission", secondary="role_permissions")
    restrictions = relationship("RolePermissionRestriction")


class UserRole(BASE_MODEL, ZopseduBase):
    """
    UserRole data model
    Bu model user ve role modeli arasında many2many ilişki kurulmasını sağlar

    Kullanıcıların rol ile ilişkilendiği modeldir. Kullanıcıların birden
    fazla rolü olabilir.
    """
    __tablename__ = 'user_roles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    birim_id = Column(Integer, ForeignKey("birim.id"), nullable=True)

    rol_tipi = Column(Enum(RolTipleri))
    is_default = Column(Boolean, default=False)

    restrictions = relationship("Permission", secondary="user_role_permission_restrictions")
    role = relationship("Role", uselist=False)
    user = relationship("User", uselist=False)


class Permission(BASE_MODEL, ZopseduBase):
    """
    Permission data model
    Kullanıcı yetkilerinin tanımlandığı bilgilerin bulunguğu modeldir.
    """
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(100), unique=True)
    endpoint_name = Column(String(100), unique=True)
    group = Column(String(100))
    code = Column(String(100))
    description = Column(String(200))

    roles = relationship("Role", secondary="role_permissions")


class RolePermission(BASE_MODEL, ZopseduBase):
    """
    RolePermission data model
    Bu model role ve permission modeli arasında many2many ilişki kurulmasını sağlar.
    """
    __tablename__ = 'role_permissions'
    id = Column(Integer, primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)


class UserRolePermissionRestriction(BASE_MODEL, ZopseduBase):
    """
    UserRolePermissionRestriction Modeli
    UserRolePermissionRestriction modeli userın belirli bir rolü ile alakalı yetki sınırlandırması
    kurallarının saklandığı data modelidir.

    Başlangıç ve bitiş tarihleri kuralın geçerli olduğu zaman aralığını
    belirler.

    "izin_verilsin_mi" alanı kuralın yetkileri genişleteceğini mi yoksa
    sınırlandıracağını mı belirler.
    """
    __tablename__ = 'user_role_permission_restrictions'
    id = Column(Integer, primary_key=True)
    user_role_id = Column(Integer, ForeignKey("user_roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

    izin_verilsin_mi = Column(Boolean)

    baslama_tarihi = Column(Date)
    bitis_tarihi = Column(Date)

    permission = relationship("Permission")


class RolePermissionRestriction(BASE_MODEL, ZopseduBase):
    """
    RolePermissionRestriction Modeli
    RolePermissionRestriction modeli belirli bir rolün yetki sınırlandırması
    kurallarının saklandığı data modelidir.

    Başlangıç ve bitiş tarihleri kuralın geçerli olduğu zaman aralığını
    belirler.

    "izin_verilsin_mi" alanı kuralın yetkileri genişleteceğini mi yoksa
    sınırlandıracağını mı belirler.
    """
    __tablename__ = 'role_permission_restrictions'
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

    izin_verilsin_mi = Column(Boolean)

    baslama_tarihi = Column(Date)
    bitis_tarihi = Column(Date)

    permission = relationship("Permission")

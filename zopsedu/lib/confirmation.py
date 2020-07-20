import random
import string
from hashlib import sha512

from flask import current_app, flash, url_for, redirect
from itsdangerous import URLSafeTimedSerializer, BadSignature
from sqlalchemy import or_

from zopsedu.auth.models.auth import User, UserRole, RolTipleri, Role
from zopsedu.bap.models.firma import BapFirma
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.mail import send_mail_with_template
from zopsedu.models import Person
from zopsedu.server import app


def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECRET_SALT_KEY'])


def confirm_token(token, expiration=7200):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECRET_SALT_KEY'],
            max_age=expiration
        )
    except BadSignature as exc:
        CustomErrorHandler.error_handler(
            hata="Bir hata meydana geldi. Hata: {}".format(str(exc)))
        return False
    return email


def random_pw():
    chars = string.ascii_letters + string.digits
    return "".join([random.choice(chars) for i in range(8)])


@app.route('/onay/<token>', methods=['GET'], endpoint="onay")
def onay(token):
    email = None
    try:
        email = confirm_token(token)
    except Exception as exc:
        CustomErrorHandler.error_handler()

    person = DB.session.query(Person).filter(
        or_(Person.birincil_eposta == email, Person.ikincil_eposta == email)).first()
    firma = DB.session.query(BapFirma).filter(BapFirma.yetkili_email == email).first()

    if (person and person.personel) or not firma:  # personelse onaylama islemi yapilmaz
        return redirect(url_for('auth.login'))
    pw = random_pw()
    username = email
    password = sha512(pw.encode()).hexdigest()

    kullanici = User(
        username=username,
        password=password,
        email=email
    )
    DB.session.add(kullanici)

    if firma:
        kisi = Person(ad=firma.yetkili_adi, soyad=firma.yetkili_soyadi,
                      birincil_eposta=firma.yetkili_email)
        DB.session.add(kisi)
        kullanici.person = kisi
        bap_firma = DB.session.query(Role).filter(Role.name == "BAP Firma").first()
        firma_role = UserRole(
            user_id=kullanici.id,
            role_id=bap_firma.id,
            rol_tipi=RolTipleri.firma,

        )
        DB.session.add(firma_role)
    DB.session.commit()
    flash(
        "Eposta başarıyla onaylandı. Giriş bilgileriniz eposta adresinize yollanmıştır.")

    send_mail_with_template(recipients=[username],
                            subject="Zopsedu Sisteme Giriş Bilgileri",
                            content_text=f"Kullanıcı Adı: {username} Şifre {pw}")

    return redirect(url_for('auth.login'))

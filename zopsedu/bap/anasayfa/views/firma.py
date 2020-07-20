"""Bap anasayfa modulu"""

from flask_babel import lazy_gettext as _
from flask import render_template, request, flash
from flask_classful import FlaskView, route

from zopsedu.lib.db import DB
from zopsedu.models import BapFirma, File
from zopsedu.yonetim.firma_yonetimi.form import FirmaKayitFormu


class BapFirmaView(FlaskView):
    """Bap anasyafa view classi"""

    @staticmethod
    @route('/firma-kayit', methods=['POST', 'GET'], endpoint="firma_kayit")
    def firma_kayit():
        """Firma Kayit Ekrani"""
        firma_kayit_formu = FirmaKayitFormu(request.form)
        file = None

        if request.method == "GET" or not firma_kayit_formu.validate():
            return render_template("firma_kayit.html", firma_kayit_formu=firma_kayit_formu)

        firma_faaliyet_belgesi = request.files.get(firma_kayit_formu.firma_faaliyet_belgesi_id.name)
        if firma_faaliyet_belgesi:
            file = File(content=firma_faaliyet_belgesi)
            DB.session.add(file)
            DB.session.flush()
        firma_data = BapFirma.data_to_dict(firma_kayit_formu.data)
        firma_data.pop("firma_faaliyet_belgesi_id")

        yeni_firma = BapFirma(firma_faaliyet_belgesi_id=file.id if file else None,
                              **firma_data)
        DB.session.add(yeni_firma)
        DB.session.commit()

        flash(_("Firma Kayıt İşleminiz Başarıyla Gerçekleşti."))
        return render_template("firma_kayit.html", firma_kayit_formu=firma_kayit_formu)

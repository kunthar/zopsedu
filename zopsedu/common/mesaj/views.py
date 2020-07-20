"""Gelen Kutusu"""
from datetime import datetime

from flask import render_template, send_file, request, jsonify, render_template_string
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import desc

from zopsedu.app import DB
from zopsedu.auth.lib import auth, Permission
from zopsedu.auth.permissions import permission_dict
from zopsedu.common.mesaj.forms import MesajSearchForm
from zopsedu.common.mesaj.models import MesajEk
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models import Mesaj
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


# todo: Permissionlar duzenlenecek
class MesajView(FlaskView):
    """MesajView"""

    excluded_methods = [
        "qry"
    ]

    def process_data(self, result, form_data, total_record):
        data = [[
            render_template_string("""
             {% if okundu %}
                    <i id=mesaj{{id}} class="fa fa-2x fa-envelope-open"></i>
                {% else %}
                    <i id=mesaj{{id}} class="fa fa-2x fa-envelope" style="color:orange"></i>
                {% endif %}
            """, okundu=r.okundu, id=r.id),
            "{} {}".format(r.gonderen_kisi.ad, r.gonderen_kisi.soyad),
            "{}".format(r.baslik),
            "{}".format(r.gonderim_zamani.strftime('%d-%m-%Y')),
            r.mesaj_tipi.value,
            render_template_string("""
             <a href="#mesaj-oku-modal"
                   class="btn btn-success"
                   data-toggle="modal"
                   data-target="#mesaj-oku-modal"
                   onclick="mesaj_oku({{ id }});">
                    {{_('Oku')}}
                </a>
            """, id=r.id)
        ] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record}
                       )

    @property
    def qry(self):
        """
        Gelen Kutusu ve ilgili alanlari icin query nesnesi olustur.
        Returns:
        """
        return DB.session.query(Mesaj).options(
            joinedload(Mesaj.gonderen_kisi).load_only('ad', 'soyad', 'birincil_eposta')). \
            filter(Mesaj.alici == current_user.person.id)

    @login_required
    @auth.requires(Permission(*permission_dict["common"]["mesaj"]["gelen_kutusu_goruntuleme"]),
                   menu_registry={'path': '.gelen_kutusu', 'title': 'Gelen Kutusu'})
    @route('/', methods=["GET"])
    def gelen_kutusu(self):
        """Kullanicaya gelen mesajlarin listelendigi view."""

        search_form = MesajSearchForm()

        return render_template('gelen_kutusu.html', search_form=search_form)

    @login_required
    @route('/<int:mesaj_id>', methods=["GET"], endpoint='mesaj_detay')
    def mesaj_detay(self, mesaj_id):
        """ Gelen kutusuna dusen mesajlarin, icerigini, kimden geldigini vs. gosterir."""
        mesaj = DB.session.query(
            Mesaj
        ).filter_by(alici=current_user.person.id).filter_by(id=mesaj_id).options(
            joinedload(Mesaj.gonderen_kisi).load_only('ad', 'soyad', 'birincil_eposta')).one()
        if not mesaj.okundu:
            mesaj.okundu = True
            mesaj.okunma_zamani = datetime.now()
            okunma_tarihi = datetime.now().strftime('%d-%m-%Y')
            okunma_ip_adresi = request.remote_addr
            mesaj.okunma_ip_adresi = request.remote_addr
            DB.session.commit()
        else:
            okunma_tarihi = mesaj.okunma_zamani.strftime('%d-%m-%Y')
            okunma_ip_adresi = mesaj.okunma_ip_adresi

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("common").get("mesaj_okundu").type_index,
            "nesne": 'Mesaj',
            "nesne_id": mesaj_id,
            "ekstra_mesaj": "{} adlı kullanıcı {} id'li mesajı okudu.".format(
                current_user.username,
                mesaj_id)
        }
        signal_sender(**signal_payload)
        mesaj_detay = {'gonderim_tarihi':
                           mesaj.gonderim_zamani.strftime('%d-%m-%Y'),
                       'okunma_tarihi': okunma_tarihi,
                       'okunma_ip_adresi': okunma_ip_adresi,
                       'gonderen_kisi_ad_soyad': mesaj.gonderen_kisi.ad + " " +
                                                 mesaj.gonderen_kisi.soyad,
                       'gonderen_kisi_birincil_eposta': mesaj.gonderen_kisi.birincil_eposta,
                       'baslik': mesaj.baslik,
                       'metin': mesaj.metin,
                       'mesaj_ek': render_template_string("""
                       <ul class="attached-document clearfix">
                            {% for ek in mesaj_ek %}
                                {% if ek.belge_r.content %}
                                    <li>
                                        <div class="document-name">
                                         <form method="post">
                                                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                                            <button class="btn btn-link" id="ek_{{ ek.belge }}" name="ek_{{ ek.belge }}"
                                                            value="{{ ek.belge }}" style="white-space: normal;"
                                                            formaction="{{ url_for('mesaj.mesaj_ek', 
                                                                                    mesaj_id=mesaj_id, 
                                                                                    belge_id= ek.belge ) }}">
                                               {{ ek.belge_r.content.file.filename }}
                                                    </button>
                                               </form>
                                        </div>
                                    </li>
                                {% endif %}
                            {% endfor %}
                        </ul>""", mesaj_ek=mesaj.mesajek, mesaj_id=mesaj_id)}

        return jsonify(status="success",
                       mesaj=mesaj_detay,
                       mesaj_id=int(mesaj_id))

    @route('/<int:mesaj_id>,/<int:belge_id>', methods=["POST"], endpoint='mesaj_ek')
    @login_required
    def mesaj_ek(self, mesaj_id, belge_id):  # pylint: disable=unused-argument
        """Mesaj Ekleri"""
        msj = Mesaj.query.filter(Mesaj.id == mesaj_id).one()
        if msj:
            belge_ek = DB.session.query(MesajEk).filter(MesajEk.mesaj_id == msj.id).filter(
                MesajEk.belge == belge_id).one()

            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("common").get("mesaj_ek_indir").type_index,
                "nesne": 'MesajEk',
                "nesne_id": belge_id,
                "ekstra_mesaj": "{} adlı kullanıcı {} id'li mesajın {} id'li mesaj ekini indirdi.".format(
                    current_user.username,
                    mesaj_id,
                    belge_id
                )
            }
            signal_sender(**signal_payload)

            return send_file(
                belge_ek.belge_r.file_object,
                as_attachment=True,
                attachment_filename=belge_ek.belge_r.content.file.filename,
                mimetype=belge_ek.belge_r.content.content_type
            )
        return jsonify(status="error"), 400

    @login_required
    @auth.requires(Permission(*permission_dict["common"]["mesaj"]["gelen_kutusu_goruntuleme"]))
    @route('/data', methods=["POST"], endpoint="mesaj_search")
    def mesaj_arama(self):  # pylint: disable=too-many-branches
        """
        Bap mesajlarında POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """
        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = MesajSearchForm(**form_data)

        mesaj_turu = search_form.mesaj_turu.data
        mesaj_okunma_durumu = search_form.mesaj_okunma_durumu.data

        if mesaj_turu and (mesaj_turu != "-1"):
            if mesaj_turu == 'MesajTipleri.sms':
                qry = qry.filter(Mesaj.mesaj_tipi == 'sms')

            if mesaj_turu == 'MesajTipleri.eposta':
                qry = qry.filter(Mesaj.mesaj_tipi == 'eposta')

            if mesaj_turu == 'MesajTipleri.sistem':
                qry = qry.filter(Mesaj.mesaj_tipi == 'sistem')

        if mesaj_okunma_durumu == "0":
            qry = qry.filter(Mesaj.okundu == False)

        result = qry.order_by(desc(Mesaj.gonderim_zamani)).offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data(result, form_data, total_record)

"""Proje hakkinda gonderilen mesajlarin listelenmesi ve detaylarinin goruntulenmesi"""
from datetime import datetime

from flask_allows import Or, And

from flask import render_template, render_template_string, jsonify, request
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_mesajlari import ProjeMesaj
from zopsedu.lib.db import DB
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import Mesaj
from zopsedu.auth.lib import auth, Role, Permission
from zopsedu.bap.lib.auth import ProjeYurutucusu
from zopsedu.bap.proje.views.dashboard.common import get_proje_with_related_fields, get_next_states_info, \
    get_actions_info
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjeMesajView(FlaskView):
    """Proje mesajlari"""

    @staticmethod
    @login_required
    @auth.requires(Or(And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_mesajlari_goruntuleme"]),
                          ProjeYurutucusu()), Role("BAP Yetkilisi"), Role("BAP Admin")))
    @route('<int:proje_id>/dashboard/mesaj', methods=["GET"], endpoint='proje_mesajlari')
    def proje_mesajlari(proje_id):
        """Proje mesajlarini gosterir"""
        proje_yurutucusu_mu = ProjeYurutucusu().fulfill(user=current_user)
        proje = DB.session.query(Proje).options(
            joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
                OgretimElemani.personel).load_only("id").joinedload(
                Personel.person).load_only("ad", "soyad"),
            lazyload(Proje.proje_detayi),
            lazyload(Proje.kabul_edilen_proje_hakemleri),
            lazyload(Proje.proje_hakem_onerileri),
            lazyload(Proje.proje_destekleyen_kurulus),
            lazyload(Proje.proje_kalemleri),
        ).filter(Proje.id == proje_id, or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                                           Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)).first()

        next_states_info = get_next_states_info(proje_id=proje_id)
        actions_info = get_actions_info(proje_id=proje_id)

        proje_mesajlari = DB.session.query(Mesaj).join(ProjeMesaj, ProjeMesaj.mesaj_id == Mesaj.id).filter(
            ProjeMesaj.proje_id == proje_id).all()

        return render_template('dashboard/proje_mesajlari.html',
                               proje_id=proje_id,
                               next_states_info=next_states_info,
                               proje_mesajlari=proje_mesajlari,
                               proje_yurutucusu_mu=proje_yurutucusu_mu,
                               actions_info=actions_info,
                               proje=proje)

    @staticmethod
    @login_required
    @auth.requires(Or(And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_mesajlari_goruntuleme"]),
                          ProjeYurutucusu()), Role("BAP Yetkilisi"), Role("BAP Admin")))
    @route('<int:proje_id>/dashboard/mesaj/<int:mesaj_id>',methods=["GET"], endpoint='proje_mesaj_detay')
    def proje_mesaj_detay(proje_id, mesaj_id):
        """ Gelen kutusuna dusen mesajlarin, icerigini, kimden geldigini vs. gosterir."""
        mesaj = DB.session.query(
            Mesaj
        ).filter_by(id=mesaj_id).options(
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
                       'mesaj_ek':render_template_string("""
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
                        </ul>""", mesaj_ek=mesaj.mesajek,mesaj_id=mesaj_id)}

        return jsonify(status="success",
                       mesaj=mesaj_detay,
                       mesaj_id=int(mesaj_id))

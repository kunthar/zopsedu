"""Sablon text onizlemek ve sablon dosya indirmek icin  kullanılır"""
from importlib import import_module

from flask import render_template, jsonify, url_for, abort, render_template_string, request
from flask_login import login_required
from flask_classful import FlaskView, route
from sqlalchemy import func

from zopsedu.auth.lib import auth, Permission
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.firma import BapFirma
from zopsedu.bap.models.firma_teklif import FirmaTeklifKalemi, FirmaSatinalmaTeklif
from zopsedu.bap.models.proje_kalemleri import ProjeKalemi

from zopsedu.bap.models.proje_satinalma_talepleri import  TalepKalemleri
from zopsedu.bap.models.siparis_takip import SiparisTakip
from zopsedu.lib.db import DB
from zopsedu.models import Sablon


class SablonView(FlaskView):
    """
    Sablon view
    """
    route_base = "/sablon"

    @login_required
    @route('<int:sablon_id>/onizle-indir', methods=["GET"])
    @auth.requires(Permission(*permission_dict["common"]["app"]["sablon"]["sablon_onizleme"]))
    def sablon_onizle_indir(self, sablon_id):
        sablon = DB.session.query(Sablon).filter(Sablon.id == sablon_id).one()
        if not sablon.sablon_text:
            return jsonify(status="success",
                           file_url=url_for("FileView:file_download", file_id=sablon.file))
        return render_template("sablon_preview.html", sablon_text=sablon.sablon_text)

    # todo: izin ne olacak ??
    @login_required
    @route('<int:sablon_id>/render', methods=["GET"])
    @auth.requires(Permission(*permission_dict["common"]["app"]["sablon"]["sablon_onizleme"]))
    def render_sablon_with_values(self, sablon_id):
        sablon = DB.session.query(Sablon).filter(Sablon.id == sablon_id).one()
        if not sablon.sablon_text:
            return jsonify(status="success",
                           file_url=url_for("FileView:file_download", file_id=sablon.file))
        if not sablon.query_id:
            return render_template("sablon_preview.html", sablon_text=sablon.sablon_text)

        args_dict = request.args.to_dict()
        if not set(args_dict.keys()) == set(sablon.query.function_arg_list):
            return abort(404)

        # db den gelen pathten class import edilir
        query_class = getattr(import_module(sablon.query.import_path), sablon.query.class_name)
        # class methodu requestten gelen query parametreleri ile cagrilir
        query_result = getattr(query_class, sablon.query.function_name)(**args_dict)

        # sablon text icerisine query result "data" isimli parametre olarak geçilir

        return render_template_string(sablon.sablon_text, data=query_result)

    # todo: izin ne olacak ??
    @login_required
    @route('/<int:satinalma_id>/render/siparis-formu', methods=["POST"])
    @auth.requires(Permission(*permission_dict["common"]["app"]["sablon"]["sablon_onizleme"]))
    def render_siparis_formu_sablon_with_values(self, satinalma_id):
        firma_id = request.get_json()['firma_id']
        malzemeler = DB.session.query(SiparisTakip.id). \
            join(FirmaSatinalmaTeklif, FirmaSatinalmaTeklif.id == SiparisTakip.kazanan_firma_teklif_id).\
            join(TalepKalemleri, SiparisTakip.satinalma_talep_kalemleri_id == TalepKalemleri.id).\
            join(FirmaTeklifKalemi,FirmaTeklifKalemi.satinalma_talep_kalemi_id == TalepKalemleri.id).\
            join(ProjeKalemi, ProjeKalemi.id == TalepKalemleri.proje_kalemi_id).\
            join(BapFirma, BapFirma.id == FirmaSatinalmaTeklif.firma_id).\
            filter(FirmaSatinalmaTeklif.firma_id == firma_id, TalepKalemleri.satinalma_id == satinalma_id).\
            add_columns(
            BapFirma.adi.label("firma_adi"),
            BapFirma.adres.label("firma_adresi"),
            ProjeKalemi.ad.label("proje_kalemi_adi"),
            FirmaTeklifKalemi.marka_model.label("marka_model"),
            FirmaTeklifKalemi.teklif.label("teklif"),
            TalepKalemleri.talep_miktari.label("talep_miktari"),
            ProjeKalemi.birim.label("birim"),
            func.div(FirmaTeklifKalemi.teklif, TalepKalemleri.talep_miktari).label("birim_tutari")

        ).all()

        data = {
            'malzemeler': malzemeler
        }

        return jsonify(status="success", data=data)

"""Zopsedu main app module"""
from depot.manager import DepotManager
from flask_babel import Babel
from flask_jwt_extended import JWTManager


from zopsedu.auth.lib import ZopseduLoginManager



def register_signal_listeners(app):
    """Registers signals defined in project"""
    from zopsedu.lib.signals.signals import zopsedu_signals
    from zopsedu.lib.decorators import SIGNAL_LISTENERS

    for key, value in SIGNAL_LISTENERS.items():
        signal = zopsedu_signals.signal(key)
        for receiver in value:
            signal.connect(receiver, app)


# pylint: disable=too-many-locals
def register_blueprints(app):
    """
    Registers blueprints to application instance from `BLUEPRINTS`(list of
    tuples).

    The first argument of each tuple is the blueprint object, the second
    argument is options dict.

    Args:
        app (Flask): flask app instance

    Returns:
        flask.app

    """
    # samples
    from zopsedu.lib.sample_blueprint.date.views import date_blueprint
    from zopsedu.lib.sample_blueprint.template_generator.views import template_generator_blueprint
    from zopsedu.lib.sample_blueprint.form_samples.views import form_samples_blueprint
    from zopsedu.lib.sample_blueprint.table.views import table_blueprint
    from zopsedu.lib.sample_blueprint.summernote.views import summernote_blueprint
    from zopsedu.lib.sample_blueprint.file_updoad_samples.views import file_upload_samples_blueprint

    from zopsedu.farabi.blueprint import farabi_form_blueprint
    from zopsedu.erasmus.blueprint import erasmus_forms_blueprint
    from zopsedu.mevlana.blueprint import mevlana_blueprint

    # core
    from zopsedu.auth.blueprint import auth_bp
    from zopsedu.common.mesaj.blueprint import mesaj_blueprint
    from zopsedu.common.kullanici_profil.blueprint import kullanici_profil_bp

    # bap
    from zopsedu.bap.hakem.blueprint import hakem_bp
    from zopsedu.bap.proje.blueprint import proje_bp
    from zopsedu.bap.toplanti.blueprint import toplanti_blueprint
    from zopsedu.bap.anasayfa.blueprint import anasayfa_blueprint
    from zopsedu.bap.bap_yetkilisi_dashboard.blueprint import bap_yetkilisi_dashboard_blueprint
    from zopsedu.bap.firma_dashboard.blueprint import firma_blueprint
    from zopsedu.bap.hakem_dashboard.blueprint import hakem_dashboard_blueprint
    from zopsedu.bap.satinalma.blueprint import satinalma_blueprint
    from zopsedu.bap.yolluk.blueprint import yolluk_blueprint
    from zopsedu.bap.butce.blueprint import butce_blueprint
    from zopsedu.bap.demirbas.blueprint import demirbas_blueprint

    # ebys
    from zopsedu.ebys.blueprint import ebys_blueprint

    # yonetim
    from zopsedu.yonetim.bap_yonetimi.blueprint import bap_yonetimi_bp
    from zopsedu.yonetim.firma_yonetimi.blueprint import firma_yonetimi_blueprint
    from zopsedu.yonetim.personel_yonetimi.blueprint import personel_yonetimi_bp
    from zopsedu.yonetim.yetki_yonetimi.blueprint import yetki_yonetimi_bp
    from zopsedu.yonetim.ana_sayfa_yonetimi.blueprint import ana_sayfa_yonetimi_bp
    # ayarlar
    # icerik
    from zopsedu.icerik.blueprint import icerik_blueprint

    # akademik_performans
    from zopsedu.akademik_performans.blueprint import akademik_performans_bp

    # sistem takibi
    from zopsedu.sistem_takibi.blueprint import sistem_takibi_bp

    from zopsedu.lib.sample_blueprint.mail_sending.views import mail_sending_blueprint


    blueprints = {
        'core': [
            (auth_bp, {}),
            (mesaj_blueprint, {'url_prefix': '/mesaj'}),
            (kullanici_profil_bp, {'url_prefix': '/kullanici'}),
        ],

        'bap': [
            (bap_yetkilisi_dashboard_blueprint, {}),
            (hakem_bp, {'url_prefix': '/bap'}),
            (hakem_dashboard_blueprint, {'url_prefix': '/bap'}),
            (proje_bp, {'url_prefix': '/bap'}),
            (toplanti_blueprint, {'url_prefix': '/bap'}),
            (anasayfa_blueprint, {'url_prefix': '/bap'}),
            (firma_blueprint, {'url_prefix': '/bap'}),
            (butce_blueprint, {'url_prefix': '/bap'}),
            (satinalma_blueprint, {'url_prefix': '/bap'}),
            (butce_blueprint, {'url_prefix': '/bap'}),
            (yolluk_blueprint, {'url_prefix': '/bap'}),
            (demirbas_blueprint, {'url_prefix': '/bap'})
        ],

        'personel': [

        ],

        'erasmus': [
            (erasmus_forms_blueprint, {'url_prefix': '/erasmus_form'}),
        ],

        'farabi': [
            (farabi_form_blueprint, {'url_prefix': '/farabi_form'}),
        ],

        'mevlana': [
            (mevlana_blueprint, {'url_prefix': '/mevlana'}),
        ],

        # sample apps, will be removed
        'samples': [
            (date_blueprint, {'url_prefix': '/date'}),
            (template_generator_blueprint, {'url_prefix': '/templates'}),
            (form_samples_blueprint, {'url_prefix': '/form_samples'}),
            (table_blueprint, {'url_prefix': '/table_samples'}),
            (file_upload_samples_blueprint, {'url_prefix': '/file_upload'}),
            (summernote_blueprint, {'url_prefix': '/summernote'}),
            (mail_sending_blueprint, {'url_prefix': '/mail_example'})
        ],

        'yonetim': [
            (bap_yonetimi_bp, {}),
            (firma_yonetimi_blueprint, {}),
            (personel_yonetimi_bp, {}),
            (yetki_yonetimi_bp, {}),
            (ana_sayfa_yonetimi_bp, {})
        ],

        'icerik': [
            (icerik_blueprint, {})
        ],

        'sistem_takibi': [
            (sistem_takibi_bp, {})
        ],

        'akademik_performans': [
            (akademik_performans_bp, {})
        ],

        'ebys': [
            (ebys_blueprint, {"url_prefix": '/ebys'})
        ]

    }

    enabled_modules = app.config['ENABLED_MODULES']
    enabled_modules.insert(0, 'core')
    for module in enabled_modules:
        for bps in blueprints.get(module, []):
            app.register_blueprint(bps[0], **bps[1])

    if 'bap' in enabled_modules:
        from zopsedu.bap.lib.proje_durum import ProjectStateChecker
        from sqlalchemy.exc import ProgrammingError

        try:
            app.bap_proje_gecis = ProjectStateChecker(university_id=app.config['UNIVERSITE_ID'])
        except ProgrammingError as err:
            app.logger.warning("""Henüz veritabanı migration yapılmamış.
            Bu sebeple bazı modullerin çalışması için gerekli bileşenler yüklenemedi.
            Hata detayları: \n%s\n\n""", str(err))
            # pylint: enable=too-many-locals


def debug_toolbar(app):
    """Enables Debug Toolbar

    Args:
        app: flask app

    Returns:
        app
    """
    from flask_debugtoolbar import DebugToolbarExtension

    app.config['DEBUG_TB_PROFILER_ENABLED'] = True
    DebugToolbarExtension(app)
    return app


def zopsedu_app(new_app):
    """Zopsedu bağımlılıklarını aldığı app'e ekler"""

    from zopsedu.auth.models.auth import load_user
    from zopsedu.lib.anonymous import Anonymous
    from zopsedu.common.app.file.views import FileView
    from zopsedu.common.app.sablon.views import SablonView
    from zopsedu.common.app.model_filter.views import FilterView
    from zopsedu.common.export import ExportView
    from zopsedu.lib.mail import init_mail
    from zopsedu.app import scheduler, job_store
    from flask_menu import Menu
    from flask_babel import gettext as _

    # init session object login manager
    login_manager = ZopseduLoginManager()
    # login_manager.localize_callback = localize_callback
    login_manager.login_message = _("Sayfayı görüntülemek için, lütfen giriş yapınız!")
    login_manager.needs_refresh_message = _(
        "Sayfayı görüntülemek için, lütfen tekrar giriş yapınız!")
    login_manager.init_app(new_app)
    login_manager.login_view = 'auth.login'
    login_manager.user_callback = load_user
    login_manager.anonymous_user = Anonymous
    new_app.secret_key = new_app.config['SECRET_KEY']

    # depolama ayarlari
    DepotManager.configure('local',
                           {'depot.storage_path': new_app.config['DEPOT_STORAGE_PATH']})
    Babel(new_app)

    FileView.register(new_app)
    SablonView.register(new_app)
    FilterView.register(new_app)
    ExportView.register(new_app)

    # Depot Manager talep edilirse asagidaki gibi s3 uyumlu bir network
    # servisine baglanabilir.
    # DepotManager.configure('s3', {
    #     'depot.backend': 'depot.io.boto3.S3Storage',
    #     'depot.access_key_id': "123",
    #     'depot.secret_access_key': "1234",
    #     'depot.bucket': "bucket",
    #     'depot.endpoint_url': "http://localhost:8000"
    # })
    new_app.wsgi_app = DepotManager.make_middleware(new_app.wsgi_app)

    JWTManager(new_app)

    # extendd app with flask menu
    Menu(app=new_app)

    scheduler.init_app(new_app)
    scheduler.scheduler.add_jobstore(jobstore=job_store)
    scheduler.start()

    # @new_app.teardown_appcontext
    # def session_commit(exception):
    #     try:
    #         DB.session.commit()
    #     except IntegrityError as integrity_error:
    #         new_app.logger.error(integrity_error)
    #         DB.session.rollback()
    #     except Exception as exc:
    #         new_app.logger.error(exc)
    #         DB.session.rollback()

    # debug toolbar
    # enable only if you need while developing, do not in test and prod
    # new_app = debug_toolbar(new_app)
    register_blueprints(new_app)
    register_signal_listeners(new_app)
    if new_app.config['CRUD_LOG']:
        from zopsedu.lib.db_event_listeners import register_db_event_listeners
        register_db_event_listeners()

    # gereksiz 415 tane endpoint(model filtrelemek icin) olusturdugundan dolayı kaldirildi
    # build_api(new_app)

    init_mail(new_app)

    return new_app

from datetime import datetime
from importlib import import_module

from sqlalchemy.orm import lazyload
from zeep import Client
from zeep.helpers import serialize_object

from zopsedu.lib.db import DB
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.akademik_performans.lib.ozgecmis_service_parameters import \
    YOK_OZGECMIS_SERVICE_PARAMETERS
from zopsedu.server import app

MODEL_IMPORT_PATH = "zopsedu.akademik_performans.models"


class YoksisOzgecmisService(object):

    def __init__(self, kullanici_id, password, tc_no=None, ou_id=None):
        # todo: paralo ve kullanici id yi db den veya cache den okumak icin methodlar eklenecek astest icin bu sekilde
        self.service_url = "http://servisler.yok.gov.tr/ws/ozgecmisv1?wsdl"
        self.kullanici_id = kullanici_id
        self.password = password
        self.tc_no = tc_no
        self.ou_id = ou_id
        self.client = self.create_soap_client()

    def create_soap_client(self):
        client = Client(self.service_url)
        return client

    def set_tc_and_ou_id(self, tc_no, ou_id):
        """
        Bilgileri alinacak akademisyenin tc numarasi ve sistemde tanimli olan ogretim uyesi id si
        atanir
        :param tc_no: Bilgileri alinacak ogretim uyesinin tc numarasi
        :param ou_id: OgretimElemani model instance id
        :return:
        """
        self.tc_no = tc_no
        self.ou_id = ou_id

    def get_auth_info(self):
        """
        Servisi tüketmek icin gerekli olan parametreleri doner
        """
        return {
            "P_KULLANICI_ID": self.kullanici_id,
            "P_SIFRE": self.password,
            "P_TC_KIMLIK_NO": self.tc_no
        }

    def get_service_data(self, service_method_name, data_param_name):
        response = self.client.service[service_method_name](parametre=self.get_auth_info())
        # response zeep in serialize methoduy ile OrderedDict e cevrilir
        if response.sonuc:
            if response.sonuc.DurumKodu == "1":
                responseOD = serialize_object(response)
                return responseOD[data_param_name]
            elif response.sonuc.DurumKodu == "0":
                # kullanici tc si invalid demektir.
                # todo: custom error class eklenecek. invalid tc gibi
                return 0
        else:
            return 0

    def call_service_methods(self):
        for service_method_name, service_params in YOK_OZGECMIS_SERVICE_PARAMETERS.items():
            try:
                data = self.get_service_data(service_method_name,
                                             service_params.service_response_data_name)
            except Exception as exc:
                print(exc)
                break
            if type(data) is list:
                try:
                    self.save_data_to_db(data, service_params.model_name,
                                         service_params.data_id_name)
                except Exception as exc:
                    print("HATA OLUSTU: {}".format(exc))
                    DB.session.rollback()
                    break
        else:
            ogretim_elemani = DB.session.query(OgretimElemani).options(lazyload("*")).filter(
                OgretimElemani.id == self.ou_id).first()
            ogretim_elemani.yok_ozgecmis_bilgileri_var_mi = True
            ogretim_elemani.ozgemis_bilgileri_guncelleme_tarihi = datetime.now()
            DB.session.commit()
            print("ISLEM BASARIYLA SONUCLANDI")

    def save_data_to_db(self, data_list, model_name, data_id_name):
        with app.app_context():
            model_class = getattr(import_module(MODEL_IMPORT_PATH), model_name)
            kayitli_veriler = DB.session.query(model_class).filter(
                model_class.ogretim_elemani_id == self.ou_id).all()
            for data in data_list:
                # bazi verinin bütün alanalari None geliyo ve DB ye kaydediliyo bunun onune gecmek
                # icin kontrol yapiliyor.
                if data[data_id_name]:
                    for kayitli_veri in kayitli_veriler:
                        # gelen verinin daha once kayit edilip edilmedigi kontrol edilir
                        if getattr(kayitli_veri, data_id_name) == data[data_id_name]:
                            # daha once kayitli ise verinin guncel olup olmadigi kontrol edilir
                            guncelleme_tarihi = getattr(kayitli_veri, "GUNCELLEME_TARIHI", None)
                            # guncelleme tarihi fieldi 1 model(YoksisBirlikteCalistigiKisi) icin
                            # olmadigi icin bu kontrol eklendi
                            if guncelleme_tarihi and guncelleme_tarihi != data["GUNCELLEME_TARIHI"]:
                                # eger ilgili verinin guncel olmayan bir versiyonu kayitli ise
                                # var olan veri guncel versiyonuyla kaydedilir.
                                kayitli_veri.update_obj_data(data)
                            break
                    else:
                        # eger ustteki for dongusu basarili bir sekilde biterse(break olmadan)
                        # ilgili veri sistemimizde kayitli degil anlamina gelir ve veriyi kaydederiz
                        model_instance = model_class(ogretim_elemani_id=self.ou_id, **data)
                        DB.session.add(model_instance)

            DB.session.commit()

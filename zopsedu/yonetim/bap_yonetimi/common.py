from zopsedu.models import GenelAyarlar


def genel_ayarlar_guncelle(eski_genel_ayarlar, guncellenecek_field, yeni_data):
    """
    Bu method eski genel ayarlar verisini kullanarak yeni("yeni_data eklenerek) bir GenelAyarlar
    instance i olusturur.
    Eski instance aktif_mi degeri False yapilir.

    :param eski_genel_ayarlar: eski GenelAyarlar instancei
    :param guncellenecek_field: GenelAyarlar modelinde degisek fieldi temsil eder
    :param yeni_data: Guncellecek field datasi
    :return: GenelAyarlar instance
    """
    # GenelAyarlar instance datasindan dict olusturur
    ayarlar_data = eski_genel_ayarlar.to_dict()
    ayarlar_data["id"] = None
    ayarlar_data.pop("created_at")
    ayarlar_data.pop("updated_at")
    # eski kaydın "aktif_mi" fieldi False yapilir
    eski_genel_ayarlar.aktif_mi = False
    yeni_ayarlar = GenelAyarlar(**ayarlar_data)
    yeni_ayarlar.aktif_mi = True
    setattr(yeni_ayarlar, guncellenecek_field, yeni_data)
    return yeni_ayarlar

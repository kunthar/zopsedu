"""
Satinalma modulunde kullanilan ortak modellerin tutuldugu modul
"""
from decimal import Decimal


def kdv_dahil_fiyat_hesabi(teklif, kdv_orani):
    kdv_dahil_teklif = teklif + (teklif * kdv_orani / Decimal("100.00"))
    kdv_dahil_teklif = kdv_dahil_teklif.quantize(Decimal(".01"))
    return kdv_dahil_teklif


def proje_kalemi_kullanilabilir_butce_hesapla(proje_kalemi):
    """
    proje kaleminin kullanilabilir butcesini hesaplamak icin kullanilir
    :param proje_kalemi: ProjeKalemi instance
    :return: Decimal
    """
    kullanilabilir_butce = proje_kalemi.toplam_butce - proje_kalemi.rezerv_butce - proje_kalemi.kullanilan_butce
    kullanilabilir_butce = kullanilabilir_butce.quantize(Decimal(".01"))
    return kullanilabilir_butce

# {
#   "app_state": [
#     {
#       "id": "1",
#       "state_code": "P1",
#       "description": "Başvuru yapıldı, ıslak/dijital imzalı belgelerin BAP Koordinatörlüğüne teslim edilmesi bekleniyor",
#       "possible_states": [
#         "P2",
#         "P3",
#         "P4",
#         "P7",
#         "P25",
#         "P30"
#       ],
#       "current_app_state": "basvuru_kabul",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3"],
#       "universite_id": "0"
#     },
#     {
#       "id": "2",
#       "state_code": "P2",
#       "description": "Projenin ait olduğu birim amirinin başvuruyu onaylaması bekleniyor",
#       "possible_states": [
#         "P3",
#         "P4",
#         "P7",
#         "P25",
#         "P30"
#       ],
#       "current_app_state": "basvuru_kabul",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3"],
#       "universite_id": "0"
#     },
#     {
#       "id": "3",
#       "state_code": "P3",
#       "description": "Başvurunun BAP Koordinatörlüğü tarafından incelemeye alınması bekleniyor",
#       "possible_states": [
#         "P2",
#         "P4",
#         "P23",
#         "P25",
#         "P30"
#       ],
#       "current_app_state": "basvuru_kabul",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","PA6"],
#       "universite_id": "0"
#     },
#     {
#       "id": "4",
#       "state_code": "P4",
#       "description": "BAP Koordinatörlüğü başvuruyu değerlendirmek üzere belgeleri teslim aldı",
#       "possible_states": [
#         "P5",
#         "P6",
#         "P25",
#         "P30"
#       ],
#       "current_app_state": "basvuru_kabul",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","PA6"],
#       "universite_id": "0"
#     },
#     {
#       "id": "5",
#       "state_code": "P5",
#       "description": "Başvuru, Hakem ya da Bilim Kurulu değerlendirmesinde",
#       "possible_states": [
#         "P6",
#         "P25"
#       ],
#       "current_app_state": "basvuru_kabul",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","PA6","PA8"],
#       "universite_id": "0"
#     },
#     {
#       "id": "6",
#       "state_code": "P6",
#       "description": "BAP Koordinatörlüğü proje başvurusunu değerlendiriyor",
#       "possible_states": [
#         "P5",
#         "P7",
#         "P8",
#         "P9"
#       ],
#       "current_app_state": "basvuru_kabul",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","PA6","PA8","P10"],
#       "universite_id": "0"
#     },
#     {
#       "id": "7",
#       "state_code": "P7",
#       "description": "Proje başvurusu reddedildi",
#       "possible_states": [],
#       "current_app_state": "son",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1"],
#       "universite_id": "0"
#     },
#     {
#       "id": "8",
#       "state_code": "P8",
#       "description": "Başvuru kabul edildi, sözleşme bekleniyor",
#       "possible_states": [
#         "P11",
#         "P23",
#         "P25"
#       ],
#       "current_app_state": "basvuru_kabul",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "9",
#       "state_code": "P9",
#       "description": "Başvurunun onaylanması için yürütücü revizyonu bekleniyor",
#       "possible_states": [
#         "P10",
#         "P23",
#         "P25"
#       ],
#       "current_app_state": "basvuru_kabul",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","PA6","PA8","P10"],
#       "universite_id": "0"
#     },
#     {
#       "id": "10",
#       "state_code": "P10",
#       "description": "Yürütücü revizyonu tamamlandı, BAP Koordinatörlüğünün değerlendirmesi bekleniyor",
#       "possible_states": [
#         "P6",
#         "P23",
#         "P25"
#       ],
#       "current_app_state": "basvuru_kabul",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","PA6","PA8","P10"],
#       "universite_id": "0"
#     },
#     {
#       "id": "11",
#       "state_code": "P11",
#       "description": "Proje devam ediyor",
#       "possible_states": [
#         "P12",
#         "P16",
#         "P22",
#         "P23",
#         "P24",
#         "P26",
#         "P27",
#         "P29",
#         "P31",
#         "P32",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","PA6","PA7","PA8","PA9","PA10","PA11","PA12","PA13","P14","P15","P16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "12",
#       "state_code": "P12",
#       "description": "Ara rapor teslimi bekleniyor",
#       "possible_states": [
#         "P13",
#         "P14",
#         "P23",
#         "P24",
#         "P26",
#         "P27",
#         "P29",
#         "P31",
#         "P32",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA3","PA4","PA5","P7","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "13",
#       "state_code": "P13",
#       "description": "Ara rapor incelenmek üzere hakeme gonderildi",
#       "possible_states": [
#         "P14",
#         "P15",
#         "P20",
#         "P23",
#         "P24",
#         "P26",
#         "P27",
#         "P29",
#         "P31",
#         "P32",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","P7","P9","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "14",
#       "state_code": "P14",
#       "description": "Ara rapor BAP Koordinatörlüğü tarafından inceleniyor",
#       "possible_states": [
#         "P13",
#         "P15",
#         "P20",
#         "P23",
#         "P24",
#         "P26",
#         "P27",
#         "P29",
#         "P31",
#         "P32",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","P7","P9","P11","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "15",
#       "state_code": "P15",
#       "description": "Ara rapor incelemesi tamamlandı.",
#       "possible_states": [
#         "P11",
#         "P23",
#         "P24",
#         "P26",
#         "P27",
#         "P29",
#         "P31",
#         "P32",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","P7","P9","P11","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "16",
#       "state_code": "P16",
#       "description": "Sonuç raporu teslimi bekleniyor",
#       "possible_states": [
#         "P17",
#         "P18",
#         "P23",
#         "P24",
#         "P26",
#         "P27",
#         "P29",
#         "P31",
#         "P32",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","P7","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "17",
#       "state_code": "P17",
#       "description": "Sonuç raporu BAP Koordinatörlüğü tarafından inceleniyor",
#       "possible_states": [
#         "P18",
#         "P19",
#         "P20",
#         "P23",
#         "P24",
#         "P26",
#         "P27",
#         "P29",
#         "P31",
#         "P32",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","P7","P9","P11","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "18",
#       "state_code": "P18",
#       "description": "Sonuç raporu hakeme gonderildi",
#       "possible_states": [
#         "P17",
#         "P19",
#         "P20",
#         "P23",
#         "P24",
#         "P26",
#         "P27",
#         "P29",
#         "P31",
#         "P32",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","P7","P9","P11","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "19",
#       "state_code": "P19",
#       "description": "Sonuç raporu kabul edildi",
#       "possible_states": [
#         "P22",
#         "P28",
#         "P29",
#         "P32"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","P7","P9","P11","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "20",
#       "state_code": "P20",
#       "description": "Ara/sonuç raporu revizyonu bekleniyor",
#       "possible_states": [
#         "P21",
#         "P23",
#         "P24",
#         "P26",
#         "P27",
#         "P29",
#         "P31",
#         "P32",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","P7","P9","P11","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "21",
#       "state_code": "P21",
#       "description": "Ara/sonuç raporu revizyonu BAP Koordinatörlüğü tarafindan incelenmeyi bekliyor",
#       "possible_states": [
#         "P15",
#         "P19",
#         "P23",
#         "P24",
#         "P26",
#         "P27",
#         "P29",
#         "P31",
#         "P32",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","P7","P9","P11","P12","PA13","PA14","PA16"],
#       "universite_id": "0"
#     },
#     {
#       "id": "22",
#       "state_code": "P22",
#       "description": "Proje tamamlandı",
#       "possible_states": [],
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "current_app_state": "son",
#       "state_type": "proje",
#       "possible_actions":["P1","P2","P3"],
#       "universite_id": "0"
#     },
#     {
#       "id": "23",
#       "state_code": "P23",
#       "description": "Proje iptal edildi",
#       "possible_states": [],
#       "current_app_state": "son",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1"],
#       "universite_id": "0"
#     },
#     {
#       "id": "24",
#       "state_code": "P24",
#       "description": "Proje donduruldu",
#       "possible_states": [
#         "P11",
#         "P23",
#         "P27",
#         "P33",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1","P2","P3"],
#       "universite_id": "0"
#     },
#     {
#       "id": "25",
#       "state_code": "P25",
#       "description": "Proje başvurusu geri çekildi/yürürlükten kaldırıldı",
#       "possible_states": [],
#       "current_app_state": "son",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":[],
#       "universite_id": "0"
#     },
#     {
#       "id": "26",
#       "state_code": "P26",
#       "description": "Projeye ait bütçe ve satın alma işlemleri donduruldu",
#       "possible_states": [
#         "P11",
#         "P23",
#         "P27",
#         "P33",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1","P2","P3"],
#       "universite_id": "0"
#     },
#     {
#       "id": "27",
#       "state_code": "P27",
#       "description": "Proje yürütücüsü değiştirildi, sözleşme yapılması bekleniyor",
#       "possible_states": [
#         "P11",
#         "P23",
#         "P27",
#         "P33",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1","P2","P3"],
#       "universite_id": "0"
#     },
#     {
#       "id": "28",
#       "state_code": "P28",
#       "description": "Yayın bekleniyor",
#       "possible_states": ["P11"],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1","P2","P3"],
#       "universite_id": "0"
#     },
#     {
#       "id": "29",
#       "state_code": "P29",
#       "description": "BAP Koordinatörlüğü bütçe değerlendirmesi bekleniyor",
#       "possible_states": ["P11"],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1","P2","P3"],
#       "universite_id": "0"
#     },
#     {
#       "id": "30",
#       "state_code": "P30",
#       "description": "Proje işleme alınmadı, bekletiliyor",
#       "possible_states": ["P11"],
#       "current_app_state": "basvuru_kabul",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1","P2","P3"],
#       "universite_id": "0"
#     },
#     {
#       "id": "31",
#       "state_code": "P31",
#       "description": "Raportöre gönderildi",
#       "possible_states": [],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":[],
#       "universite_id": "0"
#     },
#     {
#       "id": "32",
#       "state_code": "P32",
#       "description": "Etik kurulu raporu bekleniyor",
#       "possible_states": ["P11"],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["PA1","PA2","PA3","PA4","PA5","PA6"],
#       "universite_id": "0"
#     },
#     {
#       "id": "33",
#       "state_code": "P33",
#       "description": "Projenin iptal edilmesi bekleniyor",
#       "possible_states": [],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1","P2","P3"],
#       "universite_id": "0"
#     },
#     {
#       "id": "34",
#       "state_code": "P34",
#       "description": "Yürütücünün yetkileri kısıtlandı",
#       "possible_states": [
#         "P11",
#         "P23",
#         "P27",
#         "P33",
#         "P34"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1"],
#       "universite_id": "0"
#     },
#     {
#       "id": "35",
#       "state_code": "P34",
#       "description": "Yürütücünün yetkileri kısıtlandı",
#       "possible_states": [
#         "P11"
#       ],
#       "current_app_state": "devam",
#       "module_name": "bap",
#       "sub_module_name": "bap_proje",
#       "state_type": "proje",
#       "possible_actions":["P1"],
#       "universite_id": "1"
#     }
#   ]
# }

#
# {
#   "app_action": [
#     {
#       "id": 1,
#       "action_code": "PA1",
#       "description": "Diğer işlem eklendi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 2,
#       "action_code": "PA2",
#       "description": "Projeye özel not eklendi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#      {
#       "id": 3,
#       "action_code": "PA3",
#       "description": "Proje yürütücüsüne özel not eklendi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#      {
#       "id": 4,
#       "action_code": "PA4",
#       "description": "Hakem eklendi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 5,
#       "action_code": "PA5",
#       "description": "Hakem değiştirildi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 6,
#       "action_code": "PA6",
#       "description": "Seçili Hakem / Hakemlere proje değerlendirilmesi gönderildi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 7,
#       "action_code": "PA7",
#       "description": "Seçili Hakem / Hakemlere ara/sonuç raporu gönderildi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 8,
#       "action_code": "PA8",
#       "description": "Proje proje değerlendirilmesi ile ilgili hakem kararı teslim alındı",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 9,
#       "action_code": "PA9",
#       "description": "Proje ara / sonuç raporu ile ilgili hakem kararı teslim alındı",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 10,
#       "action_code": "PA10",
#       "description": "Hakem proje değerlendirimesi BAP Yetkilisi tarafından incelendi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 11,
#       "action_code": "PA11",
#       "description": "Hakem ara / rapor değerlendirmesi BAP Yetkilisi tarafından incelendi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 12,
#       "action_code": "P12",
#       "description": "Yönetim kurulu kararı eklendi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#
#     {
#       "id": 13,
#       "action_code": "PA13",
#       "description": "Proje klasör sıra numarası eklendi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 14,
#       "action_code": "PA14",
#       "description": "Proje başlık / numarası değiştirildi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 15,
#       "action_code": "PA15",
#       "description": "Proje yürütücüsü proje için ek talep oluşturdu",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 16,
#       "action_code": "PA16",
#       "description": "Proje başlangıç tarihi ve kabul süresi değiştirildi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 17,
#       "action_code": "PA17",
#       "description": "Proje türü değiştirildi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     },
#     {
#       "id": 18,
#       "action_code": "PA18",
#       "description": "Proje imza yetkilisi değiştirildi",
#       "module_name": "bap",
#       "universite_id": 0,
#       "sub_module_name": "bap_proje"
#     }
#   ]
# }
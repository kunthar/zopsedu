## <a href="https://zetaops.io/zops-dev?active=2" target="_blank">ZOPS Development Platform</a>

Üniversitelerin bütünleşik üniversite yönetim sistemi ihtiyaçlarının karşılanması için, ortak verilerin tüm modüller tarafından kullanıldığı bir yapı tasarlanmıştır. Bu yapı öncelikle, üniversitelerdeki en karışık süreçleri içeren BAP Proje Süreçleri Yönetimi için uygulanmıştır. Sistemde yer alan öğrenci, öğretim görevlisi ve personel bilgisi ortak
olarak kullanılabilir ve yeni modüller geliştirilebilir. Öğrenci bilgi sistemi, personel yönetimi gibi yeni modüller kolaylıkla eklenebilir. Örnek modüller, projede bulunmaktadır.

#### ZOPS Development Platform bileşenleri;

* Authentication & Authorization Management LDAP, SOAP, Database
* Advanced Task Scheduler
* State Manager, (Non deterministic finite automaton)
* Error Handling and Logging
* Notification Management (Emails, SMS, Internal)
* Application Frontend Management
* In App Document Management
* Database Migration Management
* Expose REST API's
* Connect to any REST and SOAP resources
* Caching Management
* Internationalization, I18N Management
* Common Backend Libs
* Route Manager
* In app Event Streaming
* Integrated Data Science Libraries


# ZOPSEDU Tümleşik Proje Süreçleri Yönetimi ve Yönetim Bilgi Sistemi

![](https://www.zopsedu.com/static/files/zopsedu2.png)


<a href="https://demo.zopsedu.com/" target="_blank">Demo Uygulaması</a>

* Kullanıcı: bab_yetkilisi
* Parola: zetaops1992

Zopsedu hakkında detaylı bilgi için <a href="https://zopsedu.com/" target="_blank">sitesini ziyaret edebilirsiniz.</a>

Proje süresince farklı proje türü ihtiyaçlarını karşılayan ZOPSedu, akademik başarımın artmasına yardımcı olurken aynı zamanda karmaşık gündelik süreç takibini de başarıyla gerçekleştirir.
ZOPSedu Tümleşik Proje Süreçleri Yönetimi ile farklı türlerde projelerinizi istenen esneklikte oluşturabilir, yürütücülerin en az hata ve yüksek verimlilikle tüm proje süreçlerini takip etmesini sağlayabilirsiniz.

### ZOPSedu Tümleşik Proje Süreçleri Yönetimi uygulaması modülleri

* Proje Yönetimi
* Hakem Yönetimi
* Satınalma Yönetimi
* Yönetim Kurulu Toplantıları
* Bütçe Yönetimi
* Duyuru Yönetimi
* Firma Yönetimi
* Personel Yönetimi
* Şablon Yönetimi
* Kullanıcı Yönetimi
* BAP Anasayfa Yönetimi
* YÖK Proje Yönetimi
* Dış Veri Yönetimi
* Ek Talepler Yönetimi
* Demirbaş Yönetimi (Geliştiriliyor)
* Yolluk Yönetimi (Geliştiriliyor)

![](https://www.zopsedu.com/static/files/zopsedu1.png)

### ZOPSedu Yönetim Bilgi Sistemi

* Akademik personel YÖK modülü
* YÖK proje gönderimi modülü
* Yönetim Bilgi Sistemi Ana Sayfası
* Stratejik Veri Yönetimi
* Akademisyen Kişisel Sayfa Yönetimi (Geliştiriliyor)
* Scopus, WOS, ISI Dış Veri Yönetimi (Geliştiriliyor)
* ZOPSedu Rektör Kokpiti (Geliştiriliyor)

### Teknik Bilgi

* Geliştirmede, Python Flask, Postgresql veritabanı ve Redis kullaılmıştır.
* Sistem docker-compose ile geliştirme ve production şeklinde kurulabilir.
* Redis cache kullanıldığı için, web uygulaması istenen sayıda sunucuya ölçeklenebilir.
* Bilgi işlem birimlerinin adapte olması için geliştirme Türkçe temelli yapılmıştır.
* Linux veya Unix tabanlı bir sistemde geliştirme yapılması önerilir. Windows üzerinde test edilmemiştir ve gerek de yoktur.
* Kod elden geldiğince detaylı olarak belgelendirilmiştir. Lütfen zahmet edip kodu okuyunuz.

### Kurulum bilgisi

```zopsedu``` altında ana proje yer almaktadır.
```zops-dev``` altında kurulum ve deployment için gerekenler bulunmaktadır.

```zops-dev``` ```dev``` dizini altında geliştirme için bilgisayarınıza kurulum için gereken dosyalar bulunmaktadır.
```zops-dev``` ```prod``` dizini altında sistemi devreye alırken gerekecek dosyalar bulunmaktadır. Nginx veya Haproxy ile devreye alabilirsiniz.


### Lisans

Bu depo ikili lisansa sahiptir.

* Kendi bünyesinde uyarlama için kullanacak "Kamu Üniversiteleri" için geçerli olan lisans GPL3 lisansıdır. "Kamu Üniversiteleri", geliştirdikleri modülleri GPL3 uyarınca paylaştıkları sürece istedikleri geliştirmeyi yapabilirler. Lütfen depodaki GPL3 lisansını dikkatlice okuyunuz.
* Ticari olarak kullanmak üzere geliştirme yapacak olan özel eğitim kurumları da dahil olmak üzere tüm diğer kurumlar, Zetaops'un yazılı izni olmadan geliştirme yapamazlar. Tespiti halinde tüm haklarımız saklıdır.

* Lisanslama
* Kurulum yardımı
* Modül geliştirme hizmeti
* Teknik danışmanlık

konularında destek almak için Zetaops info[youknow]zetaops.io eposta adresine ya da @zetaops twitter hesabina ulaşabilirsiniz.


![Made in URLA with Love and Enginar](https://zetaops.io/static/assets/images/enginar-small.png)
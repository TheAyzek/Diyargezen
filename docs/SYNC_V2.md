# Sync v2 — Sunucu sözleşmesi

Durum: Sunucu, web sync motoru ve Python/SQLite sync worker v2 kullanıyor.
Web kataloğunda çakışma çözüm paneli var. Native SQLite çözüm fonksiyonları
eklendi, fakat gömülü web ile SQLite deposunun oturum/veri köprüsü ve native
çözüm ekranı tamamlanmadı. Bütün yazma yollarının geçişi tamamlanmış değildir.

## İstek

`POST /api/sync/v2`, mevcut JWT Bearer oturumu ile çağrılır.

```json
{
  "operations": [{
    "operation_id": "her-yeni-karar-icin-benzersiz-kimlik",
    "server_id": "karakterin-sabit-uuid-kimligi",
    "base_revision": 0,
    "system": "pf1e",
    "name": "Valeros",
    "data": {"level": 1},
    "is_deleted": false
  }]
}
```

- Yeni kayıtta `base_revision=0`; düzenleme/silmede en son alınan sunucu revizyonu.
- Paket başına en fazla 100 işlem. Aynı pakette işlem kimlikleri benzersiz olmalı.
- Ağ hatasında aynı işlem kimliği **aynı içerikle** tekrar gönderilir.
- Yeni düzenleme veya kullanıcı tarafından çözülen çakışma yeni işlem kimliği alır.
- İstemci saatleri karar vermez; güncelleme zamanını sunucu üretir.

## Yanıt ve istemci yükümlülükleri

`results` her işlem için `accepted` veya `conflict` içerir. Kabulde `revision`,
çakışmada `expected_revision`, `actual_revision` ve `server_character` döner.
Kabul ve çakışma sonuçları hesap bazlı işlem tablosunda kalıcıdır. Karakter
mutasyonu ile işlem onayı aynı transaction içinde commit edilir.

- `accepted`: yalnızca gönderilen yerel revision hâlâ aynıysa dirty bayrağını temizle.
- `conflict`: yerel düzenlemeyi **koru**; sunucu kopyasını ayrı sakla ve kullanıcıya
  karşılaştırma/çözüm sun. Kendiliğinden sunucu kopyasıyla değiştirme.
- Aynı kimlik farklı içerikle kullanılırsa HTTP 409; paket geri alınır.
- Eşzamanlı yazma yarışında HTTP 409; paket geri alınır, aynı kimliklerle tekrar denenir.
- Tekrar edilen işlem, özgün onayı döndürür. Güncel karakter daha ileri revizyonda olabilir.

`characters`, sadece oturum sahibinin bütün kayıtlarını ve silme işaretlerini içerir;
`snapshot_mode="full"`. Saat damgasına göre filtreleme yoktur. Büyük hesaplarda
sayfalı değişiklik günlüğü/cursor henüz uygulanmadı.

## Geçiş ve sınırlar

- `characters.revision` SQLAlchemy optimistic locking alanıdır; ORM üzerinden yapılan
  güncellemeler sürümü artırır, eski ORM nesnesiyle eşzamanlı yazma reddedilir.
- Başlangıç geçişi mevcut DB'nin SQLite yedeğini alır; eski satırlara revizyon 1,
  kimliği olmayanlara sabit UUID verir. Geçiş veri silmez ve tekrar çalıştırılabilir.
- `/api/sync` sadece eski PULL isteklerini kabul eder; yazma paketi HTTP 426 döner.
  Yeni istemci/server birlikte dağıtılmalıdır; eski istemciler artık yazamaz.
- Sayısal ID ile PUT, DELETE, level-up, level-undo, portrait, GM modifier/override
  ve level-up-session yolları `If-Match: <revision>` ister. Eksik başlık 428,
  geçersiz başlık 400, eski revizyon 409 döner. GET/list/create yanıtlarında
  `revision` ve `server_id` bulunur. Sonraki işlemde yeni revizyon kullanılmalıdır.
- DELETE soft-delete uygular; karakter satırı ve ilerleme geçmişi korunur.
  Silinmiş karakter normal GET/list işlemlerinde görünmez, v2 snapshot'ta görünür.
- İstemcilerin kalıcı işlem kuyruğu ve ayrı conflict saklaması eklendi. Webde
  yerel/sunucu seçimi öncesinde iki kopya da arşivlenir. Yerel seçim yeni işlem
  kimliğiyle tekrar gönderilir. Mahzendeki arşivden ayrı bir karakter kopyası
  kurtarılabilir; mevcut sunucu kaydı üzerine sessizce yazılmaz.
- Sayısal-ID komutları v2 işlem onayı tablosunu kullanmaz. Yanıt kaybında otomatik
  tekrarlama yapılmamalı; yeniden senkronize edilip sonuç kontrol edilmelidir.
  Eski revizyonla tekrar istek ilerlemeyi ikinci kez uygulamaz. Yeni karakter
  oluşturmak için eski POST yerine kalıcı operation_id kullanan v2 tercih edilir.
- İşlem onayları şimdilik süresiz tutulur; temizleme/retention politikası henüz yok.
- Ham SQL ile güncelleme ORM revizyon denetimini aşabilir; bütün yazıcılar denetlenmeli.
# Güvenli masaüstü başlangıcı ve eski misafir uyumluluğu

Sentetik misafir token'ları ve eski ortak `Yerel Gezgin` hesabına giriş kapalıdır.
Bu hesaba ait veriler silinmez, otomatik kişisel hesaba atanmaz. Web misafir
karakterleri yerel IndexedDB'de kalır; bulut senkronizasyonu gerçek üyelik ister.

Masaüstü yalnızca kendi ayırdığı 127.0.0.1:8000 soketinde çalışan backend'i açar.
Önceden bu portta çalışan geliştirme sunucusunu otomatik kullanmaz; önce onu
kapatıp masaüstünü yeniden başlatın. Port değiştirme/file:// fallback yapılmaz;
eski IndexedDB origin'i korunur.

## Native SQLite adaptörü (25 Eylül 2026)

Qt WebChannel yalnızca sahipli localhost ana çerçevesine açılır; köprü sırrı
closure içinde tutulur. Komut kümesi sabittir, SQL veya dosya yolu kabul etmez.
Hesap `account:<username>` ve misafir `guest` bölümleri ayrı tutulur. JWT ilk
kullanımda yerel API otoritesiyle doğrulanır; DB'de token'ın kendisi değil özeti
saklanır. Daha önce doğrulanan oturumun çevrimdışı yerel erişimi, sunucu JWT'sinin
süresi dolsa da korunur; bu sunucuda yazma yetkisi sağlamaz.

`web_local_records`, `web_local_archives`, `web_level_drafts` kayıtları sahibine
göre ayrılır. Köprü hatası sessizce IndexedDB'ye yönlendirmez. Gönderim sırasında
değişen kaydın dirty durumu korunur; eski oturumun yanıtı yeni hesaba uygulanmaz.
Level-up taslağı commit edilmiş karakterden ayrıdır. Eski tarayıcı deposu ancak
açık JSON yedekleme/içe aktarma ile taşınır; otomatik hesap sahipliği atanmaz.

Sınır: mevcut native doğrulayıcı yerel backend JWT'sini doğrular. Uzak bulut
otoritesi, güvenilir endpoint yapılandırması ve issuer bazlı hesap ayrımı henüz
uçtan uca bağlanmadı. Yerel API testleri gerçek çok cihazlı bulut testi değildir.

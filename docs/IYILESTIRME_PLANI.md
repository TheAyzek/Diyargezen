# Diyargezen iyileştirme takibi

## Güncel durum — 25 Eylül 2026, son doğrulama

Alttaki aşama notları kronolojik geçmiş kaydıdır; eski “henüz yok” ve test
sayıları güncel durum değildir. Güncel yayın sınırları ve tekrar çalıştırma
adımları: [Yayın ve doğrulama raporu](YAYIN_VE_DOGRULAMA.md).

- WebView–SQLite köprüsü, hesap ayrımı, kalıcı v2 işlem kuyruğu, conflict
  arşivi ve kopya olarak kurtarma eklendi. Eski IndexedDB deposu otomatik taşınmaz.
- Foundry öncelikli alan bazlı scraper fallback, kaynak izi, çelişki göstergesi
  ve güvenli katalog upsert uygulandı. Parser'ın gizli DB yazımı kaldırıldı;
  `pf1e` alias'ının aynı kataloğu ikinci kez işlemesi engellendi.
- Gerekçeli seçim override'ları, tek level-up sihirbazı ve hesap/karakter bazlı
  kalıcı taslak eklendi. Tam PF1e kural kapsamı bitmiş sayılmıyor.
- Kayıt/hesaplama/PDF sözleşmesi ortaklaştırıldı. Canlı ve indirilen PDF aynı
  AcroForm eşlemesini kullanır; şablon önbelleği, debounce ve eski yanıt koruması var.
- Özel API yanıtlarının service worker önbelleğine girmesi engellendi;
  üretim varlıkları çevrimdışı kullanım için derleme manifestine alındı.
- Son tasarım aşaması uygulandı: özgün fantastik illüstrasyon, lacivert–zümrüt–altın
  tema, mobil yerleşim, görünür odak ve azaltılmış hareket desteği.
- Son Python koşusu: **562 geçti, 4 atlandı, 5 uyarı, 1 subtest geçti** (48,64 sn).
  Frontend: **41 geçti**; üretim derlemesi başarılı. Ana JS 603,20 → 108,16 kB.
- Yerel geliştirme tamamlamaları, canlı bulut/temiz EXE/Docker kabulü demek değildir.
  Uzak JWT otoritesine masaüstü bağlantısı, tam çevrimdışı yeniden başlatma,
  ileri PF1e kombinasyonları ve dağıtım doğrulaması açık yayın kapılarıdır.

Önemli veri olayı: ilk güvenli önizleme sırasında eski SpellParser yan etkisi
gerçek DB'nin `spells` kataloğunu değiştirdi. Hata düzeltildi; önceki yedekle
salt-okunur karşılaştırmada karakterler, kullanıcılar, ilerleme ve diğer tablolar
aynı; yalnızca büyü kataloğu farklı. Otomatik geri yükleme yapılmadı. Ayrıntı raporda.

## 25 Eylül 2026 başlangıç doğrulaması

Hedef: PF1e karakterlerinin web ve masaüstünde güvenilir biçimde yönetilmesi;
açıklanabilir hesaplar, izlenebilir GM istisnaları ve tutarlı PDF çıktısı.

Bu kayıt tüm ürünün tamamlandığı anlamına gelmez. Aşama 1 başlangıç denetimi
tamamlandı; aşağıdaki ürün hataları ve doğrulanmamış akışlar açık kalıyor.

### Uygulanan başlangıç düzeltmeleri

- Masaüstü `save_character` içinde tanımsız `dirty_characters` kullanımını kaldırdık.
  Toplu sistem doğrulaması, verinin gerçekten mevcut olduğu `sync_characters`
  metoduna taşındı. PF1e dışı karma paket ağ isteğinden önce reddediliyor.
- Kayıt/güncelleme, JWT başlığı, PF1e paketleri ve boş PULL isteği için 5
  ağdan bağımsız regresyon testi eklendi.
- Backend senkronizasyon testleri her testte yeni bellek veritabanı kullanıyor;
  test sonunda önceki FastAPI dependency override geri yükleniyor.
- Auth ve progression testlerindeki modül seviyesinde kalan dependency override
  kaldırıldı. Her test temiz bellek veritabanı kullanıyor ve override geri yükleniyor.
  Auth testleri gerekli kullanıcıyı kendileri hazırlıyor; test sırasına bağımlılık kaldırıldı.

### Ölçülen durum

- `tests/test_desktop_api_client.py`, `web/backend/tests/test_gm_engine.py`,
  `web/backend/tests/test_sync_api.py`: toplam 10 test geçti.
- `web/frontend` altında `npm run build`: başarılı.
- Derleme çıktısı: ana JS 603.20 kB (gzip 153.16), vendor 211.32 kB
  (gzip 67.41), PDF 428.95 kB (gzip 177.67). Ana paket için boyut uyarısı var.
- İzole çalışma kopyasında `python -m pytest tests web/backend/tests -q
  -p no:cacheprovider --import-mode=importlib`: **463 geçti, 4 atlandı,
  3 uyarı, 1 subtest geçti** (26.57 saniye). Atlanan testler başarı sayılmadı.
  İlk kopyada eksik frontend dosyalarının neden olduğu 13 hata, kaynak/dist
  dosyaları kopyalandıktan sonra tekrar çalıştırmada ortadan kalktı.
- Testler asıl kullanıcı DB'sinde çalıştırılmadı. SQLite backup ile alınmış
  geçici kopya kullanıldı; tarayıcı test hesabı da yalnızca bu kopyada oluşturuldu.
- Browser becerisiyle yerel sunucuda üyelik oluşturma, karakter kaydetme ve
  tam sayfa yenilemesinden sonra karakterin listelenmesi doğrulandı.
- PDF yükleme göstergesi kalktı ve iframe oluştu. PDF içindeki alan değerleri,
  indirilen PDF, ayrı giriş/çıkış ve gerçek çevrimdışı çakışma akışı doğrulanmadı.
- Tarayıcı denetimi: Valeros hazır şablonunda ırk/sınıf alanları boş kaldı;
  isim değişikliği sonrasında görünen BAB +1'den +0'a değişti. Testlerin geçmesi
  bu akışın doğru olduğu anlamına gelmiyor. Ortak karakter sözleşmesi aşamasında
  şablon yükleme ve editör başlatma eşlemesi için regresyon testi gerekli.

## Sıralı iş planı ve kabul ölçütleri

1. Başlangıç doğrulamasını tamamla: test yalıtımını denetle, tam test paketini
   izole ortamda çalıştır, kayıt/giriş/karakter/PDF akışını tarayıcıda doğrula.
   Kabul: başarısızlıklar ve test edilmeyen akışlar ayrı ayrı belgeli.
2. Veri güvenliği: paketlenmiş veritabanının kullanıcı verisi üzerine
   kopyalanmasını kaldır; içerik aktarımını ayır. Yedek ve şema geçişi ekle.
   Sync için işlem kimliği, revizyon, onay ve hesap bazlı yerel ayrım kur.
   Kabul: istek sırasında düzenlenen kayıt dirty kalır; tekrar gönderim,
   hesap değişimi, eşzamanlı düzenleme ve silme kullanıcı verisini kaybettirmez.
3. Birleşik katalog: Foundry + scraper alan bazlı çözümleme, kaynak sürümü,
   eksik/çelişkili veri işaretleri. Kabul: fallback testleri ve API kaynak dökümü.
4. GM motoru: seçim bazlı gerekçeli override ve denetim geçmişi; level-up
   geçiş kuralları, commit ve geri alma. Kabul: bağımsız referans karakter
   testleri, yeniden açınca korunan kararlar ve hesap katkı dökümü.
5. İstemci/PDF bütünlüğü: ortak karakter sözleşmesi, envanter miktarı/ağırlığı,
   kalıcı kayıt ve tek PDF alan eşlemesi. Kabul: web, desktop ve PDF aynı sonuçta.
6. Performans: ölçüm sonrası istek birleştirme, eski yanıt koruması,
   PDF önbelleği, dar store abonelikleri, indeks ve sayfalama; bağımlılık
   denetimi sonrası atıl kod temizliği. Kabul: tekrarlanabilir önce/sonra ölçümü.
7. Yayın: zorunlu üretim anahtarı, kullanıcı yetkileri, güvenli oturum saklama,
   CI, paketleme ve geri yükleme rehberi. Kabul: temiz ortam kurulumu ve
   kullanıcı verisini koruyan sürüm yükseltme testi.
8. **En son — modern, canlı ve tematik site tasarımı:** teknik işler tamamlandıktan
   sonra mevcut arayüzü baştan gözden geçir. Diyargezen/PF1e fantastik temasına
   uygun renk, tipografi, katmanlar, bileşenler ve tutarlı görsel dil oluştur.
   Gerekirse özgün üretilmiş illüstrasyonlar, arka planlar ve dekoratif görseller
   kullan; veri yoğun karakter editöründe okunabilirliği koru. Responsive düzen,
   klavye erişimi, kontrast, azaltılmış hareket tercihi ve ölçülü animasyonlar
   dahil olsun. Önce tasarım yönünü göster, ardından uygula. Kabul: masaüstü ve
   mobil görsel inceleme; auth, kayıt/sync/çakışma ve canlı PDF regresyonları;
   optimize görsellerle önceki performans hedeflerinin korunması. Bu aşama
   kullanıcının isteğiyle tüm teknik aşamaların sonrasına eklendi; henüz başlamadı.

## Öncelikli açık bulgular

- SQLite ve web IndexedDB hesap ayrımı eklendi; gömülü web/SQLite oturum
  bağlantısı henüz uçtan uca doğrulanmadı. Sunucu v2 revizyon/işlem onayı temeli
  eklendi; istemci geçişi ve açık çakışma çözümü henüz yok. Aktif LWW protokolü cihaz saatlerine dayanıyor; çok cihazlı
  kullanım için tam veri kaybı koruması sağlandığı iddia edilmemeli.
- `parsers/pf1e_parser.py`: açıklamaya göre tekilleştirme alan bazlı fallback değil.
- Yeni içerik modelleri ile çalışan ETL/sorgu yolunun entegrasyonu eksik.
- Level-up oturumu saklama, tam geçiş denetimli state machine değil.
- Hazır şablon → editör geçişinde karakter alanları korunmuyor (yukarıdaki
  tarayıcı bulgusu). `loadPresetCharacter` ve `initCharacter` veri şekilleri incelenmeli.
- Arayüzdeki "şifrelenmiş üye alanı" ve koşulsuz senkronizasyon ifadeleri,
  uygulamanın gerçek güvenlik/senkronizasyon garantilerine göre düzeltilmeli.

Kaynak içerikler, lisanslar ve kullanıcı kayıtları temizlik kapsamında silinmez.

## Aşama 2 — İlk veri güvenliği düzeltme paketi (25 Eylül 2026)

- Masaüstü sync artık tüm dirty bayraklarını topluca temizlemiyor. Gönderilen
  anlık kopya, yereldeki zaman damgası/isim/sistem/veri/silme durumu ile karşılaştırılıyor;
  yalnızca yanıtta kimliği bulunan, arada değişmemiş kayıtlar onaylanıyor.
  Sonradan eklenen, düzenlenen veya silinen kayıtlar kuyrukta kalıyor.
- PULL güncellemesi/silmesi bekleyen yerel değişikliklerin üzerine yazmıyor.
  Yanıt ve checkpoint tek SQLite işlemiyle uygulanıyor; hata durumunda geri alınıyor.
- API, gönderilen kayıt checkpoint'ten eski olsa da sonucunu yanıtına ekliyor.
  Böylece eski tarihli çevrimdışı kayıtlar da açıkça onaylanabiliyor.
- Frozen başlangıçtaki tüm DB'yi kopyalama kaldırıldı. Yeni `db/bundled_catalog.py`
  sadece eksik PF1e entities satırlarını ekliyor. Kullanıcı tabloları kaynak paketten
  aktarılmıyor, mevcut katalog satırları ve kimlikleri değiştirilmiyor.
- Mevcut DB'ye katalog eklenmeden önce SQLite backup ile `data/backups` altında
  tarihli yedek alınıyor. Yedek alınamazsa aktarım duruyor; dosya üzerine yazma
  fallback'i yok. Eksik içerik yoksa yeniden yedek/aktarım yapılmıyor.
- Doğrulama: offline CRUD, yarış senaryoları, sync worker, katalog aktarımı,
  API sync, auth, progression ve desktop API testlerinden **34 geçti, 3 uyarı**.
  Test DB'leri geçici/bellek veritabanlarıdır. Bu değişikliklerden sonra tam
  test paketi ve paketlenmiş EXE çalıştırılmadı; önceki 463 sonucu yeni doğrulama değildir.
- Kalan işler: hesap bazlı ayrım ve geçiş politikası; sunucu revizyon/işlem
  protokolü; tüm cihazlara eski tarihli değişikliklerin güvenilir dağıtımı;
  sürümlü içerik/şema geçişleri ve geri yükleme akışı. Aşama 2 tamamlanmış değildir.

## Aşama 2 — SQLite hesap ayrımı (25 Eylül 2026)

- `local_characters.owner` alanı ve hesap/dirty indeksi eklendi. Listeleme,
  ID ile okuma, güncelleme, silme ve gönderim kuyruğu aktif kullanıcıya göre
  sınırlandırılıyor. Checkpoint artık hesap bazlı; eski ortak checkpoint yeniden kullanılmıyor.
- Her girişe benzersiz `session_id` veriliyor. Sync worker kalıcı oturumdan
  kendi API istemcisini oluşturuyor; UI'nin değişken JWT nesnesini paylaşmıyor.
  Aynı hesaba yeniden giriş dahil oturum değişince eski yanıt atomik olarak reddediliyor.
  Çıkış yapılmışken bellekte kalan token ile gönderim yapılmıyor.
- Eski şemadan geçmeden önce `data/backups` altında SQLite yedeği alınıyor.
  Sahibi belirsiz eski kayıtlar ve misafir kayıtları `owner=''` ile yerel tutuluyor;
  ilk giriş yapan hesaba otomatik atanıp yüklenmiyor. Çıkış yapılmış yerel DB
  erişiminde korunuyorlar. Kullanıcı onaylı sahiplenme/aktarım arayüzü henüz yok.
- Başka yerel hesaba/yerel arşive ait server_id ile gelen kayıt işlemi durduruyor;
  mevcut kaydın sahibini değiştirmiyor. Böyle bir çakışmanın aktarım/uzlaştırma akışı
  sonraki revizyon protokolünde ele alınmalı.
- Eski Python karakter ekranındaki, hesap filtresini eski kayıt tablosuyla
  aşabilecek okuma fallback'i kaldırıldı.
- Doğrulama: **44 test geçti, 3 deprecation uyarısı**. Hesap değiştirme,
  çıkış, yeniden giriş, gecikmiş yanıt, sabit istek kimliği, hesaba özel checkpoint,
  eski şema yedeği ve tekrarlı geçiş dahil. Tam test paketi/EXE/UI bu turda çalıştırılmadı.
- Kapsam sınırı: bu uygulama katmanı ayrımıdır, SQLite şifrelemesi veya OS erişim
  kontrolü değildir. Kullanıcı adı mevcut sabit sunucu için hesap anahtarıdır;
  çok sunuculu kullanım için sunucu kimliği + değişmez kullanıcı ID'si gerekir.
- Bir sonraki adım: gömülü web istemcisinin IndexedDB ve oturum akışını aynı
  güvenlik ilkeleriyle düzenlemek; ardından sunucu revizyon/çakışma protokolü.

## Aşama 2 — Web IndexedDB ve oturum ayrımı

- Her kullanıcı için ayrı `DiyargezenScopedDB:account...` deposu, misafir için
  ayrı depo kullanılıyor (aynı origin/sunucu varsayımı). Eski ortak `DiyargezenDB`
  açılmıyor, silinmiyor veya otomatik sahiplenilmiyor. Yeni listede eski yerel
  kayıtlar görünmez; bu davranış arayüzde açıklanıyor. Eski depodan kurtarma/
  kullanıcı onaylı aktarım arayüzü henüz yok. Mevcut JSON yedekleri içe aktarılabilir.
- İstek oturumun token ve giriş neslini sabitliyor. Geç dönen yanıt eski oturuma
  aitse uygulanmıyor; başka sekmedeki oturum değişikliği arayüzü yeniden yüklüyor.
  Uzun süren içe aktarımlar da başlangıç oturumuna bağlı.
- Kayıt/silme/listeleme artık tek UUID tabanlı sync yolunu kullanıyor; ayrı
  POST/PUT ile çift kayıt oluşturma yolu kaldırıldı. Sayısal API kimliği
  `remote_id` alanında ayrıca tutuluyor. Klon ve yedekten aktarımlar yeni UUID alıyor.
- Dirty boolean indeks sorgusu kaldırıldı (IndexedDB boolean indeks anahtarı
  desteklemez). Gönderilmemiş kayıtlar gerçekten kuyruğa giriyor. Silmeler sunucu
  onayı gelene kadar tombstone olarak saklanıyor; doğrudan yerelden silinmiyor.
- Yerel revision ile istek sırasında yapılan düzenleme/silme korunuyor. Yalnızca
  yanıtta bulunan, gönderilen revision ile aynı kayıtlar onaylanıyor. Yanıt ve
  checkpoint aynı IndexedDB transaction içinde yazılıyor; commit bekleniyor.
- Bekleyen işler 15 saniyede bir tekrar deneniyor. Şifreleme iddiası kaldırıldı;
  yalnızca internet bağlantısına dayanarak 'senkronize' gösterilmesi düzeltildi.
- Doğrulama: `npm test` ile **11 davranış testi geçti** (Node + fake-indexeddb,
  ağ istekleri mock). `test_multi_character_vault.py`: **4 test geçti**.
  `npm run build` başarılı: ana JS 601.64 kB / gzip 152.93 kB; paket boyutu
  uyarısı sürüyor. Tam Python paketi, gerçek tarayıcı çok-sekme testi ve EXE
  bu turda çalıştırılmadı. Bu sonuçlar uçtan uca ürün onayı değildir.
- Sıradaki iş: sunucu revizyonları ve idempotent işlem onayları; saat farkından
  bağımsız değişiklik dağıtımı ve çakışmaların kullanıcıya açıkça sunulması.

## Aşama 2 — Sunucu v2 temeli

- `/api/sync/v2`: base_revision denetimi, accepted/conflict sonuçları ve hesap
  bazlı kalıcı işlem onayları. Aynı işlem tekrar uygulanmıyor; farklı içerikle
  aynı kimliğin kullanılması 409 ile reddediliyor. Paket ve onayları atomik.
- ORM karakter revizyonu eklendi; eşzamanlı eski nesneyle güncelleme engelleniyor.
  Yedekli şema geçişi eski karakterlere başlangıç revizyonu ve eksik UUID veriyor.
- V2 PULL şimdilik tüm hesap kayıtlarını ve tombstone'ları döndürüyor; istemci
  saatlerinden bağımsız. Artımlı cursor/sayfalama ileride gerekli.
- Ek güvenlik bulgusu düzeltildi: cloud seed açma yolu artık mevcut küçük/az
  içerikli DB'nin üzerine yazmıyor; yalnızca dosya yoksa exclusive create kullanıyor.
- Doğrulama: **55 test geçti, 3 deprecation uyarısı**. Yeni v2 testleri; eski cihaz
  çakışması, tekrar gönderim, tombstone, hesap yetkisi, ORM yarış koruması,
  yedekli şema geçişi, sabit UUID ve seed korumasını kapsıyor. Asıl kullanıcı DB'sine
  geçiş uygulanmadı; tam test paketi/EXE/tarayıcı bu turda çalıştırılmadı.
- Web/masaüstü hâlâ v1 kullanıyor; eski endpoint deprecated ama aktif. V2'nin
  korumaları henüz ürünün bütün yazma yollarında etkin değil.
- Sıradaki parça: istemcilerde kalıcı operation_id/base_revision kuyruğu, ayrı
  conflict kopyaları, kullanıcı çözüm akışı ve v2 bağlantısı; eski CRUD/seviye
  atlama/silme yollarını da yeni sözleşmeye geçirmek.
- Protokol ayrıntıları ve sınırlar: `docs/SYNC_V2.md`.

## Aşama 2 — V2 istemci kuyrukları ve çakışma çözümü

- Web sync motoru ve Python `SyncWorker` artık `/api/sync/v2` çağırıyor. V2
  bulunamazsa v1'e geri dönülmüyor; yerel kuyruk korunuyor. Sunucu önce güncellenmeli.
- IndexedDB kaydında immutable pending_operation; SQLite'ta hesap bazlı
  `sync_v2_records` tablosu kullanılıyor. Gönderilecek işlem, ağ isteğinden önce
  kaydediliyor. Yanıt kaybında/restart'ta aynı kimlik ve aynı içerikle tekrar deneniyor.
- İstek sürerken yapılan edit/delete önceki işlemden ayrılıyor. Onay, arada
  yapılan düzenlemeyi temizlemiyor; sonraki işlem yeni kimlikle ve onaylanan
  revizyonla hazırlanıyor. Eksik onay kuyruktan kayıt çıkarmıyor.
- Çakışmada yerel kayıt ve sunucu kopyası ayrı korunuyor, otomatik tekrar gönderim
  duruyor. Web kataloğundaki panel iki sürümü gösteriyor; yereli yeni işlem olarak
  gönderme veya sunucuyu kullanma seçeneği sunuyor. Seçim öncesi iki kopya arşivleniyor.
  Eski açık panel, sonradan değişmiş kaydı ezemiyor.
- SQLite için listeleme/çözüm fonksiyonları da eklendi; native Qt çözüm ekranı ve
  gömülü web/SQLite oturum-veri köprüsü hâlâ eksik. Web paneli IndexedDB çakışmalarını
  yönetir, SQLite kuyruğunu doğrudan yönetmez. Arşivden kurtarma UI'si de henüz yok.
- Klon/yedek içe aktarma yeni UUID ve base revision 0 ile başlıyor. Paket başına
  en fazla 100 kayıt gönderiliyor; kalanlar sonraki döngüde ele alınıyor.
- Doğrulama: **63 Python testi + 17 frontend testi geçti**. İki ayrı SQLite
  istemcisinin TestClient API ile eşzamanlı edit, conflict çözümü ve yakınsaması;
  kayıp yanıt sonrası restart/tekrar gönderimi doğrulandı. Frontend testleri
  fake-indexeddb ve mock HTTP kullanıyor; gerçek tarayıcı etkileşimi değil.
- Vite üretim derlemesi başarılı, ana paket yaklaşık 606 kB; boyut uyarısı sürüyor.
  Tam test paketi, gerçek tarayıcı çakışma ekranı ve EXE bu turda doğrulanmadı.
- Kalan öncelik: eski CRUD/seviye atlama/hard-delete yollarını revizyon protokolüne
  geçirmek; native köprüyü tamamlamak; gerçek tarayıcı/EXE senaryolarını doğrulamak.
  Aşama 2 tüm ürün genelinde henüz tamamlanmış değildir.

## Aşama 2 — Eski API yazıcılarının revizyon koruması

- Sayısal karakter ID'siyle güncelleme, silme, seviye atlama/geri alma, portre,
  GM modifier/override ve level-up-session işlemlerine ortak If-Match denetimi
  eklendi. Yetki önce denetleniyor; eksik revizyon 428, eski revizyon 409.
  ORM commit yarışları rollback edilip 409'a çevriliyor.
- Eski `/api/sync` PUSH kapatıldı (426); salt okunur PULL uyumluluğu korunuyor.
  Bu kasıtlı bir istemci uyumluluğu değişikliğidir: eski istemcilerin yazabilmesi
  için güncellenmesi gerekir. V2 kuyrukları hata durumunda yerelde kalır.
- HTTP DELETE artık tombstone oluşturuyor; karakter ve ilerleme geçmişi korunuyor.
  Normal GET/list silinmiş ve başka hesaba/sahipsiz kayıtları göstermiyor.
- Web seviye işlemleri JWT ve revizyonu sabitliyor. Kaydedilmemiş/değişmiş editör
  veya bekleyen kuyruk varsa önce kaydet/senkronize et/yeniden aç yönlendirmesi var.
  Sunucu işleminden sonra revision ve yerel snapshot güncelleniyor. İstek sırasında
  yapılan düzenleme korunuyor; eski base revision ile kaydedilerek sonraki sync'te
  çakışmanın görünür olması sağlanıyor.
- Başarısız sunucu level-up isteğinin yerelde seviye artırmaya devam etmesi kaldırıldı.
  Gerçekten yerel/yeni karakterin offline level-up yolu korunuyor. Gecikmiş stat
  hesaplama yanıtları değişmiş editörü güncellemiyor.
- Doğrulama: **77 Python + 21 frontend testi geçti**, Vite build başarılı.
  Testler missing/stale If-Match, PUT yarış rollback'i, soft-delete geçmişi,
  auxiliary revision, eski PUSH reddi ve progression workflow'u kapsıyor.
  Bu sonuç tam test paketi, gerçek tarayıcı veya EXE doğrulaması değildir.
- Sonraki parça: gömülü web/SQLite oturum-veri köprüsü. Native çakışma ekranı,
  arşivden geri yükleme ve paketlenmiş uygulamada uçtan uca testler hâlâ açık.

## Aşama 2 — Köprü öncesi HTTP oturum sınırı

- Köprü incelemesinde ortak Axios interceptor'ünün sabitlenmiş JWT'yi tekrar
  localStorage'dan okuyup değiştirdiği, herhangi bir 401 yanıtının da mevcut
  oturumu sildiği görüldü. Merkezi HTTP oturum koruması eklendi.
- İstek oturumu çağrı anında yakalanıyor. Açıkça verilen başka JWT veya eski
  oturum nesli gönderimden önce reddediliyor; geç yanıtlar yeni hesaba ulaşmıyor.
  Sync ve revision işlemleri yakaladıkları oturumu HTTP katmanına da iletiyor.
- 401 yerel hesap kimliğini/kuyruğu silmiyor; arayüz yeniden giriş uyarısı
  gösteriyor. Misafir isteğine sentetik JWT eklenmiyor. Yeniden giriş öncesi
  açık editörü kaydetme uyarısı var; otomatik token yenileme eklenmedi.
- Doğrulama: 9 yeni gerçek Axios interceptor/adapter testi ile toplam **30
  frontend testi geçti**; üretim derlemesi başarılı. Ana paket yaklaşık 608 kB;
  boyut uyarısı sürüyor. Gerçek tarayıcı/EXE ve Python paketi bu turda çalıştırılmadı.
- Köprü henüz uygulanmadı. WebView mevcut localhost:8000 sağlık yanıtını güven
  kanıtı sayıyor; native yetkiler açılmadan önce uygulamanın kendi başlattığı
  sunucu doğrulanmalı ve dış sayfalara köprü erişimi engellenmeli.
- Ek güvenlik bulgusu: backend `get_current_user` hâlâ sentetik guest token'ı
  ortak `Yerel Gezgin` hesabına eşliyor. Frontend artık bunu göndermese de sunucu
  kabulü sürüyor; güvenli köprüden önce bu eski uyumluluk yolu kapatılmalı ve
  mevcut ortak misafir kayıtları otomatik bir hesaba taşınmadan korunmalı.
- Sonraki işler: sunucu misafir yetki sınırı, güvenilir WebView başlangıcı,
  hesap/oturum kontrollü SQLite adaptörü ve tek senkronizasyon sahibi. IndexedDB
  ile SQLite arasında çift yazma/otomatik kayıt sahipliği ataması yapılmayacak.

## Aşama 2 — Ortak misafir hesabını kapatma ve sahipli yerel sunucu

- Backend artık sentetik misafir token'larını kabul etmiyor. Eski ortak
  `Yerel Gezgin` hesabına parola ile giriş, o hesaba ait eski imzalı JWT ve bu
  adla yeni kayıt da reddediliyor. Hiçbir kullanıcı/karakter silinmedi veya başka
  hesaba atanmadı. Bu hesaptaki eski kayıtlar, sahipliği ayrıca doğrulanacak bir
  kurtarma işlemi gerektirir; otomatik taşınmayacak. Misafir web kullanımı kendi
  IndexedDB bölümünde kalır; kişisel bulut işlemleri gerçek üyelik gerektirir.
- Masaüstü başlangıcı portu önce kendisi ayırıp Uvicorn'a soketi devrediyor.
  Sağlık yanıtıyla sunucu keşfi/güvenme kaldırıldı. 8000 doluysa açıklayıcı hata
  gösteriliyor; başka servise, rastgele porta veya file:// sayfasına geri dönüş
  yok. Sabit origin, mevcut IndexedDB kayıtlarının adresini değiştirmiyor.
- Worker dursa da pencere açıkken port sahipliği korunuyor. WebView yalnızca
  çalışan sahipli sunucunun origin'ine gezinmeye izin veriyor; farklı origin,
  dosya/JS/data adresleri ve yeni pencere açılışları engelleniyor. Aynı origin'li
  blob PDF alt çerçevesine izin var. Yerel dosyanın uzak/dosya erişimi kapatıldı.
  Bu gezinme sınırı tek başına XSS veya tüm ağ alt-kaynaklarını filtreleyen bir
  sandbox değildir; native köprü açılmadan ayrıca yetki/oturum denetimi gereklidir.
- Yanıltıcı "SQLite Sync Aktif" durum metni düzeltildi. Eski native giriş
  formundaki önceden doldurulmuş kullanıcı adı/parola kaldırıldı.
- Doğrulama: **100 Python testi geçti, 5 deprecation uyarısı**. Bellek/geçici
  SQLite testleri; gerçek loopback soketiyle sahiplik, dolu port, worker durması,
  başarısız startup ve URL izin politikası kapsandı. WebView modülü import kontrolü
  geçti. Gerçek Qt pencere/PDF etkileşimi, EXE ve tam paket bu turda doğrulanmadı;
  gerçek kullanıcı DB'sinde uygulama başlatılmadı.
- Sonraki teknik parça: hesap/oturum kontrollü web–SQLite adaptörü ve tek sync
  sahibi; ardından native çakışma/arşiv kurtarma ve uçtan uca doğrulama.
- Kullanıcının yeni isteği, sıralı planın **en sonuna 8. tasarım aşaması** olarak
  eklendi: modern, canlı, PF1e temalı arayüz ve gerektiğinde özgün üretilmiş görseller.

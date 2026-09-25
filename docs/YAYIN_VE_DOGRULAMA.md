# Diyargezen — uygulama ve yayın doğrulaması

25 Eylül 2026. Bu rapor kaynak çalışma ağacını anlatır; yayımlanmış sürüm veya
tam PF1e uyumluluk sertifikası değildir. Değişiklikler commit edilmedi.

## Uygulanan mimari

FastAPI + React/Vite korunmuştur; Next.js'e gereksiz yeniden yazım yapılmamıştır.
Aktif ürün sistemi PF1e'dir. Eski modüllerde erişilmeyen diğer sistem dalları
tamamen ayıklanmış değildir; veri dosyaları körlemesine silinmemiştir.

- **Veri:** Foundry > scraper > paketlenmiş zenginleştirme önceliği, alan bazlı
  fallback. Sıfır ve false eksik sayılmaz, listeler atomik seçilir. `_provenance`
  kaynakları, alan kaynaklarını, fallback alanlarını ve çelişkileri taşır.
  Katalog yazımı eski özel satırları silmez. API ve kural arayüzü kaynak izini sunar.
- **GM:** bilinen prerequisite koşulları denetlenir, yorumlanamayan koşullar manuel
  inceleme uyarısıdır. Override seçim ve gerekçeyle kaydedilir; sessiz genel bypass
  değildir. Custom modifier alanları korunur. HP/skill/feat/trait/spell/ability
  adımları tek sihirbazda, taslak ayrı depoda tutulur. Gerekçeli GM commit desteklenir.
- **Kimlik/sync:** sunucu revizyonları, UUID, tekrar gönderilebilir operation_id,
  dirty kayıt, kalıcı kuyruk, hesap ayrımı ve çakışma arşivi. Sayısal kayıt mutasyonları
  If-Match ister. Qt istemci WebChannel üzerinden SQLite kullanır; web IndexedDB
  kullanır. Başarısız native kayıt sessizce başka depoya yazılmaz.
- **PDF:** orijinal AcroForm + pdf-lib + blob iframe. Canlı/indirilen dosya tek
  alan eşlemesine dayanır. Debounce, şablon önbelleği ve eski üretimi atma vardır.
  Ekipman miktarı/ağırlığı ve temel alanlar aynı karakter sözleşmesinden gelir.
- **Performans:** editör/kural kütüphanesi/PDF tembel yüklenir. Dosya taraması
  scandir metadatasını yeniden kullanır. Katalog ilk HTTP açılışını bloke etmeyen
  arka plan işi olarak çalışır; durum kullanıcıya gösterilir. Sistem alias'ı aynı
  kataloğu iki kez işleyemez. Service worker özel API verilerini önbelleğe almaz.
- **Tasarım:** özgün üretilmiş 187 kB WebP illüstrasyon; lacivert, zümrüt, altın;
  giriş ve mahzen hero alanları, mevcut Diyargezen logosu, mobil tek kolon,
  klavye odağı ve azaltılmış hareket tercihi. Harici font CDN bağımlılığı kaldırıldı.

## Ölçülen sonuçlar

| Kontrol | Sonuç |
| --- | --- |
| İzole Python tam paket | 562 geçti, 4 atlandı, 5 deprecation uyarısı, 1 subtest; 48,64 sn |
| Frontend testleri | 41 geçti |
| Üretim derlemesi | Başarılı |
| Ana JS | 603,20 → 108,16 kB; gzip 32,35 kB |
| Ayrı editör/PDF parçaları | 374,18 / 428,92 kB; toplam indirme azalmasıyla karıştırılmamalı |
| Kaynak fingerprint | Bu makinede yaklaşık 0,95 sn; eski süre için kontrollü benchmark yok |
| Tam veri aktarımı | 27.927 birleşik kayıt; tamamlanan denemede alias yüzünden iki tur vardı, son regresyon bu tekrarı kaldırır |
| Geçici katalog incelemesi | 38.115 toplam satır; 27.927 provenance, 20.763 fallback, 1.109 çelişki taşıyan kayıt |

Katalog toplamı birleşen satır sayısı değildir: daha önceki/özel satırlar güvenlik
için tutulur. Silinmiş/yeniden adlandırılmış kaynak kayıtlarını emekliye ayırma
politikası ileride açıkça tasarlanmalıdır. Fallback sayısı tüm bu kayıtların sayısal
kurallarının eksiksiz makine yorumuna çevrildiği anlamına gelmez.

Tarayıcıda doğrulananlar: Valeros şablonunun Human/Fighter/BAB +1 korunması,
yeniden adlandırma-kayıt-yenileme-yeniden açma, gerçek blob PDF iframe,
level-up HP'den becerilere geçiş ve taslağı kapatıp yeniden açma. 390 px mobil
mahzen ve editör incelendi; document genişliği ve scroll genişliği 386 px.
Portre düğmesi dar ekranda alt satıra geçer. İlk açılışta yakalanan `currentScreen`
ReferenceError düzeltildi; açık sihirbaz render regresyonu eklendi.

PDF fixture tekrar açıldı; alan değerleri ve appearance stream'leri kontrol edildi,
iki sayfa PNG render ile görsel incelendi. Kara hızı `Base`/`Squares1` alanlarına
bağlandı; olmayan `SPEED` alanı kaldırıldı. Sıfır hız/HP/AC korunması test edildi.
Türkçe metinler mevcut Helvetica/WinAnsi sınırı nedeniyle translitere edilir;
tam Unicode font gömme tamamlanmış değildir. Fixture tüm karmaşık karakterlerin
alan eşitliğini veya her ekipman satırının taşmamasını kanıtlamaz.

Gerçek Qt WebChannel smoke ve iki ayrı SQLite istemcisinin v2 API testleri geçti.
Bir önceki koşuda Qt alt işlemi Windows erişim ihlaliyle kapandı; tekil tekrar ve
sonraki iki tam koşu geçti. Temiz EXE/uzun süreli Qt kararlılığı ayrıca sınanmalıdır.

## Test ve önizleme

Proje kökünde (PowerShell):

```powershell
.\.venv\Scripts\python.exe scripts/verify_isolated.py -q --tb=short
```

Bu komut geçici çalışma kopyası ve SQLite backup oluşturur; tam testleri orada
çalıştırır. Yazdırılan yolu saklayın. Testleri doğrudan gerçek kullanıcı DB'sinde
çalıştırmayın. Geçici kopyalar teşhis için tutulur, gerçek kullanıcı bilgileri
içerebilir; paylaşmayın. Silmeden önce tam yolu ve artık gerekmediğini doğrulayın.

`web/frontend` dizininde:

```powershell
npm test
npm run build
```

Güvenli yerel önizleme için kökte:

```powershell
.\.venv\Scripts\python.exe scripts/preview_safe.py
```

Önizleme 127.0.0.1:8011 üzerinde geçici DB kullanır. Kod/varlık değişiklikleri için
frontend'i yeniden derleyin; backend değişiklikleri süreç yeniden başlatılınca alınır.
Gerçek kullanıcı DB'sinin üzerine preview kopyası yazmayın.

## Veri olayı ve korunan yedek

İlk önizleme sırasında eski `parsers/base.py` her büyü için `SpellParser()`
oluşturuyordu. Varsayılan yol nedeniyle hedef geçici DB yerine gerçek
`data/characters.db` içindeki `spells` tablosuna yazdı. Önizleme durduruldu; parser
salt dönüşüm haline getirildi. Büyü projeksiyonu artık açık DB yolu ve toplu katalog
transaction'ı kullanır. İki regresyon testi gizli SQLite yazımını ve hedef DB'yi denetler.

Olay öncesi yedek:
`C:\Users\dnssh\AppData\Local\Temp\diyargezen-verification-shmlvgu5\data\characters.db`

`scripts/compare_databases.py` ile salt-okunur, kolon sırasından bağımsız içerik
karşılaştırmasında: characters 9, users 14, progression 1, entities 35.527 satır
ve diğer tablolar değişmemiştir. `spells` 4.204 → 4.204 satır; içerik farklıdır.
Bu nedenle “gerçek DB'ye hiç dokunulmadı” denemez. Otomatik geri yükleme yapılmadı;
tüm DB'yi geri almak sonradan eklenen kullanıcı düzenlemelerini kaybettirebilir.
Yedeği inceleme bitene kadar koruyun; gerekirse yalnız katalog için kontrollü
geri yükleme yapın, kullanıcı tablolarını değiştirmeyin.

Kod temizliğinde eski `LevelUpWizardModal.jsx` kaldırıldı; tek sihirbaz kaldı.
Git geçmişinden geri alınabilir. Kullanıcıya ait CV/portfolio HTML dosyalarına
dokunulmadı. Kullanıcı karakteri veya hesabı silinmedi.

## Yayın kapıları — açık kalan işler

1. **Gerçek uzak otorite:** native köprü şu anda yerel backend JWT'sini doğrular.
   Güvenilir HTTPS sunucu adresi, issuer bazlı hesap bölümü, uzak login/doğrulama ve
   iki fiziksel cihazda kopma/yeniden bağlanma testi tamamlanmalı. Mevcut yerel API
   senkronizasyonu çok cihazlı bulut tamamlandı diye sunulmamalı.
2. **Offline kabul:** service worker manifesti ve özel veri izolasyonu testli;
   browser/Qt tamamen kapalıyken ağsız yeniden açma, ilk kurulum önbelleği,
   disk dolması ve uzun süreli eşzamanlı düzenleme testleri tamamlanmadı.
3. **Kural kapsamı:** tüm sınıf/arketip/multiclass/feat/büyü kombinasyonları,
   stat katkı açıklamaları, yerel-sunucu-PDF referans karakter eşitliği ve yerel
   level-undo eksiksiz değil. Mevcut sihirbaz ana sınıf ilerlemesine odaklanır;
   tam multiclass ve 20 üstü GM akışı ayrıca gerekir. Bilinmeyen prerequisites
   uyarı/GM incelemesi olarak kalır; otomatik uygunluk iddiası yapılmaz.
4. **Dağıtım:** Docker bu ortamda yok; compose/Dockerfile düzenlemeleri gerçek
   imajda çalıştırılmadı. Temiz Windows EXE kurulum/yükseltme/geri alma testleri yok.
   TLS/domain/hosting ve üretim hesabı seçilmedi; dış sunucuya yayın yapılmadı.
5. **Güvenlik/işletim:** JWT şu anda tarayıcı yerel deposunda; HttpOnly refresh
   modeli veya OS güvenli kasa, rate limiting, retention, çok büyük hesaplarda
   cursor sync, log redaksiyonu ve kaynak lisans/atıf denetimi yayın öncesi gerekir.
   Katalog dosyalarının tamamı makinece yorumlanabilir kurallara dönüşmüş değildir.
6. **Görsel kabul:** ana masaüstü/mobil ekranlar incelendi; tüm modal ve uzun içerik
   kombinasyonlarında klavye/ekran okuyucu/kontrast denetimi tamamlanmadı.

Üretimde `DIYARGEZEN_ENV=production`, benzersiz en az 32 karakter
`DIYARGEZEN_JWT_SECRET`, açık `DIYARGEZEN_CORS_ORIGINS` ve kalıcı
`DIYARGEZEN_DB_PATH` gerekir. Secret repoya veya rapora yazılmamalıdır.
Compose kullanıcı çalışma DB'sini değil ayrı named volume'u kullanır.
Prod'a geçmeden mevcut DB'yi SQLite backup API ile tutarlı yedekleyin, yedeği
ayrı dizinde salt-okunur doğrulayın. Şema geçişi öncesi yazıcıları durdurun.
Geri dönüşte önce yeni verinin ayrı yedeğini alın; eski kopyayı kullanıcı verisi
üzerine sessizce kopyalamayın. Restore tatbikatı yalnızca geçici hedefte yapılmalı.

PF1e HP/CON ve favored class kararları için birincil referanslar:
[Character Advancement](https://www.aonprd.com/Rules.aspx?Category=Basics&Name=Character+Advancement),
[Archives of Nethys kuralları](https://aonprd.com/Rules.aspx?ID=349).

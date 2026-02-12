# Diyargezer - Ultimate Character Builder

Modern, kullanıcı dostu TTRPG karakter oluşturma uygulaması.

## Özellikler

- 🎲 **4 TTRPG Sistemi**: D&D 5e, Pathfinder 1e, Vampire 5e, Mutants & Masterminds
- 🎨 **Modern Arayüz**: CustomTkinter ile koyu tema tasarımı
- 📄 **PDF Export**: Karakter sayfalarınızı PDF olarak kaydedin
- 💾 **Otomatik Kaydetme**: Karakterler JSON formatında kaydedilir
- 📊 **Gerçek Zamanlı Log**: Tüm işlemler loglanır

## Kurulum

1. Gerekli bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:
```bash
python gui/modern_gui.py
```

## Kullanım

### D&D 5e Karakter Oluşturma
1. "D&D 5e" sekmesine tıklayın
2. Karakter adını girin
3. Irk ve sınıfı seçin
4. "Karakteri Oluştur" butonuna tıklayın

### Pathfinder 1e Karakter Oluşturma
1. "Pathfinder 1e" sekmesine tıklayın
2. Karakter adını girin
3. STR, DEX, CON, INT, WIS, CHA skorlarını girin (1-20 arası)
4. "Karakteri Oluştur" butonuna tıklayın

### PDF Export
- Karakter oluşturduktan sonra "PDF Export" butonuna tıklayın
- Kaydetmek istediğiniz konumu seçin
- PDF otomatik olarak oluşturulur

## Sistem Gereksinimleri

- Python 3.8+
- CustomTkinter 5.2+
- ReportLab (PDF için)

## Dosya Yapısı

```
gui/
├── modern_gui.py      # Ana GUI uygulaması
└── app.py            # Eski PySide6 GUI (referans için)

creators/
├── base_creator.py   # Temel creator sınıfı
├── dnd5e_creator.py  # D&D 5e creator
├── pathfinder1e_creator.py  # Pathfinder 1e creator
├── vtm5e_creator.py  # Vampire 5e creator
└── mm3e_creator.py   # M&M 3e creator

data/
├── dnd_data.json     # D&D 5e verileri
├── pathfinder_1e_data.json  # Pathfinder 1e verileri
├── vtm_data.json     # Vampire 5e verileri
└── mm_data.json      # M&M 3e verileri

characters/           # Kaydedilen karakterler
```

## Geliştirme

Bu GUI, mevcut CLI tabanlı sistemi tamamlayıcı olarak geliştirilmiştir. Daha gelişmiş özellikler için `gui/app.py` dosyasındaki PySide6 tabanlı GUI'yi inceleyebilirsiniz.

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
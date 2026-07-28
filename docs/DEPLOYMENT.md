# Diyargezen — Production Deployment & Sunucu Kurulum Kılavuzu

Bu doküman, Diyargezen TTRPG web platformunun (FastAPI Backend + React Frontend) gerçek bir Linux (Ubuntu 22.04 / 24.04 LTS) sunucuda production standartlarına uygun şekilde kurulmasını, SSL sertifikalandırılmasını ve güvenli şekilde yönetilmesini açıklar.

---

## 🛠️ 1. Sunucu Gereksinimleri & Ön Hazırlık

### Minimum Sunucu Özellikleri
- **İşletim Sistemi:** Ubuntu 22.04 LTS veya Ubuntu 24.04 LTS
- **RAM:** Minimum 2 GB (4 GB önerilir)
- **Disk:** Minimum 20 GB SSD
- **Ağ:** Statik IPv4 adresi, Port 80 (HTTP) ve Port 443 (HTTPS) açık

### Ortam Değişkenleri (`.env`)
Sunucuda güvenli JWT secret key üretmek için aşağıdaki komutu çalıştırın:

```bash
openssl rand -hex 32
```

Kök dizinde bir `.env` dosyası oluşturun:

```env
SECRET_KEY=b8f7d92e10a4c567890123456789abcdef0123456789abcdef0123456789abcd
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:////app/data/diyargezen.db
```

---

## 🐳 2. Yöntem A: Docker Compose ile Dağıtım (Önerilen Hızlı Yöntem)

Tüm platformu (Backend + Frontend + Nginx Proxy) tek komutla canlıya almak için Docker Compose kullanabilirsiniz.

### 1. Docker & Docker Compose Kurulumu:
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
```

### 2. Repositoriyi Klonlama ve Başlatma:
```bash
git clone https://github.com/KullaniciAdi/Diyargezenweb.git
cd Diyargezenweb

# Docker konteynerlerini arka planda derle ve başlat
docker compose up --build -d
```

### Status ve Log Kontrolü:
```bash
docker compose ps
docker compose logs -f backend
```

---

## 💻 3. Yöntem B: Bare-Metal Linux (Systemd & Nginx Dağıtımı)

Docker kullanmadan doğrudan Linux üzerine kurulum yapmak için:

### 1. Sistem Paketlerinin Yüklenmesi:
```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx
```

### 2. Backend Systemd Servisi (`/etc/systemd/system/diyargezen-backend.service`):
```ini
[Unit]
Description=Diyargezen FastAPI Backend Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/diyargezen/web/backend
Environment="PYTHONPATH=/var/www/diyargezen"
ExecStart=/var/www/diyargezen/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Servisi etkinleştirin ve başlatın:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now diyargezen-backend
```

### 3. Nginx Konfigürasyonu (`/etc/nginx/sites-available/diyargezen`):
```nginx
server {
    listen 80;
    server_name diyargezen.com www.diyargezen.com;

    root /var/www/diyargezen/web/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Nginx servisini aktifleştirin:
```bash
sudo ln -s /etc/nginx/sites-available/diyargezen /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 4. SSL / TLS Sertifika Kurulumu (HTTPS)

Let's Encrypt / Certbot kullanarak alan adınıza ücretsiz SSL yükleyin:

```bash
sudo certbot --nginx -d diyargezen.com -d www.diyargezen.com
```

Certbot Nginx ayarlarınızı otomatik güncelleyecek ve HTTP isteklerini HTTPS'e yönlendirecektir.

---

## 💾 5. Otomatik Veritabanı Yedeği (Backup Strategy)

SQLite veritabanının her gün otomatik olarak yedeklenmesi için bir cron job oluşturun:

### Yedekleme Betiği (`/usr/local/bin/backup_diyargezen.sh`):
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/diyargezen"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y-%m-%d_%H%M%S)

# SQLite canlı snapshot yedeği
sqlite3 /var/www/diyargezen/data/diyargezen.db ".backup '$BACKUP_DIR/diyargezen_$DATE.db'"

# 30 günden eski yedekleri sil
find $BACKUP_DIR -type f -name "*.db" -mtime +30 -delete
```

Çalıştırma izni verin ve Crontab'a ekleyin:
```bash
sudo chmod +x /usr/local/bin/backup_diyargezen.sh
sudo crontab -e
```

Crontab satırı (Her gece saat 03:00'te çalışır):
```cron
0 3 * * * /usr/local/bin/backup_diyargezen.sh
```

---

## 🛡️ 6. Güvenlik Sertleştirme (Production Hardening)

### UFW Güvenlik Duvarı:
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

*Diyargezen Projesi — Pathfinder 1st Edition Web Platformu*

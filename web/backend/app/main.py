import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importing config first registers the workspace root for shared PF1e modules
# when the backend is started from web/backend.
from app.core.config import DB_PATH
from app.routers import systems, rules, characters, auth, sync
from app.core.database import check_db_exists

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

tags_metadata = [
    {
        "name": "Auth",
        "description": "🔑 **Kimlik Doğrulama & Oturum Yönetimi**: Kullanıcı kaydı (`register`), JWT login (`token`) ve yetkilendirme kontrolü.",
    },
    {
        "name": "Characters",
        "description": "🧙‍♂️ **Karakter Yönetimi & Canlı Hesaplama**: Pathfinder 1e karakter kağıdı CRUD işlemleri, soft-block kural denetimi ve GM override mekanizması.",
    },
    {
        "name": "Rules",
        "description": "📜 **PF1e Kural Motoru & Veri Arama**: Trait, Feat, Spellbook, Irk ve Sınıf kural arama ve filtreleme API'leri.",
    },
    {
        "name": "Systems",
        "description": "⚙️ **TTRPG Sistem Kataloğu**: Desteklenen masaüstü ve web TTRPG kural sistemleri kataloğu.",
    },
    {
        "name": "Sync",
        "description": "☁️ **Offline-First Masaüstü Senkronizasyonu**: Masaüstü PySide6 istemcisi ile bulut veritabanı arasında otomatik arka plan senkronizasyonu.",
    },
]

API_DESCRIPTION = """
# 🛡️ Diyargezen TTRPG Rules & Character Management API

**Diyargezen**, Pathfinder 1st Edition (PF1e) kuralları odaklı, offline-first masaüstü istemcisine ve ayrık mimarili web platformuna sahip bir TTRPG karakter yönetim servisidir.

### 🌟 Öne Çıkan Özellikler:
- **Fast & Stateless Stat Calculation:** Karakter istatistikleri, BAB, AC, saves ve beceri modifikatörleri anlık ve dinamik hesaplanır.
- **Game Master Rule Override (`is_overridden`):** Sert engeller ("hard-block") yerine akıllı soft-validation uyarıları ve GM izin bayrağı sunar.
- **Combined Rules Database (Unified DB):** Foundry VTT veri setleri ile Scraper (Aonprd/d20pfsrd) verilerini birleştirerek eksiksiz kural fallback'i sağlar.
- **Offline-First Synchronization:** Masaüstü istemcisinde internetsiz yerel SQLite'a kaydeder, internet bağlantısı sağlandığında JWT ile buluta aktarır.

---
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info("Initializing TTRPG database at path: %s", DB_PATH)
    if not check_db_exists():
        logger.error("Database connection failed or expected schemas are missing at: %s", DB_PATH)
    else:
        logger.info("Database loaded and schemas verified successfully.")

    from app.core.database import initialize_orm_schemas
    initialize_orm_schemas()
    logger.info("ORM schemas initialized and checked.")
    yield


# Initialize FastAPI App
app = FastAPI(
    title="Diyargezen TTRPG Web API",
    description=API_DESCRIPTION,
    version="2.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Diyargezen Core Architecture Team",
        "url": "https://github.com/KullaniciAdi/Diyargezenweb",
    },
    license_info={
        "name": "Open Gaming License (OGL) & MIT",
    },
    lifespan=lifespan,
)

# Set up CORS middleware to allow React frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow React frontend dev servers on any local/network port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Tüm yakalanmamış iç sunucu hatalarını (500 Internal Server Error) yakalar.
    Üretim ortamında hassas sunucu dosya yolları veya kod izlerinin (stack trace)
    sızmasını engeller ve hatayı güvenle log kaydı olarak saklar.
    """
    logger.error("Dahili Sunucu Hatası (%s): %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Sunucu tarafında beklenmeyen bir hata oluştu. Lütfen tekrar deneyiniz."
        }
    )



import sys
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Root probe endpoint
@app.get("/api/health", tags=["Systems"], summary="Sistem Sağlık Durumu & Probe", description="API sunucusunun sağlık durumunu ve aktif desteklenen TTRPG sistemlerini döndürür.")
def read_root():
    return {
        "status": "healthy",
        "app": "Diyargezen TTRPG Web Backend",
        "supported_systems": ["pathfinder1e"]
    }

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(systems.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(characters.router, prefix="/api")
app.include_router(sync.router, prefix="/api")

frontend_dist = None
if getattr(sys, 'frozen', False):
    candidate = Path(getattr(sys, '_MEIPASS', '')) / "web" / "frontend" / "dist"
    if candidate.exists() and (candidate / "index.html").exists():
        frontend_dist = candidate

if not frontend_dist:
    candidate = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if candidate.exists() and (candidate / "index.html").exists():
        frontend_dist = candidate

if frontend_dist:
    logger.info("Mounting built frontend static files from: %s", frontend_dist)

    @app.get("/")
    def serve_spa():
        return FileResponse(frontend_dist / "index.html")

    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")




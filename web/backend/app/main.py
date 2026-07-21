import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import systems, rules, characters, auth, sync
from app.core.database import check_db_exists
from app.core.config import DB_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

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
    description="Stateless rules calculation and persistent character sheet management for D&D 5e, PF1e, and M&M 3e.",
    version="2.0.0",
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


# Root probe endpoint
@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "app": "Diyargezen TTRPG Web Backend",
        "supported_systems": ["dnd5e", "pf1e", "mnm3e"]
    }

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(systems.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(characters.router, prefix="/api")
app.include_router(sync.router, prefix="/api")

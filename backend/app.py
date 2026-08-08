from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database.session import engine
from backend.database.models import Base
from backend.api.deps import require_api_key
from backend.dashboard import router as dashboard_router


# Routers
from backend.deception.routes import (
    router as deception_router,
    public_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting MIRAGE Platform...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database initialized.")

    yield

    print("🛑 Shutting down MIRAGE Platform...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)



# -------------------------------------------------
# CORS
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Register Routers
# -------------------------------------------------

# Protected APIs
app.include_router(
    deception_router,
    prefix="/api/v1",
    tags=["Deception"],
)

# Public APIs
app.include_router(public_router)
app.include_router(dashboard_router)

# -------------------------------------------------
# Root
# -------------------------------------------------

@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "status": "online",
        "version": settings.VERSION,
    }


# -------------------------------------------------
# Health Check
# -------------------------------------------------

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
    }


# -------------------------------------------------
# Protected Admin Endpoint
# -------------------------------------------------

@app.get(
    "/admin/deception-logs",
    dependencies=[Depends(require_api_key)],
    tags=["Admin"],
)
async def deception_logs():
    return {
        "message": "Access granted!",
        "logs": [],
    }


# -------------------------------------------------
# Startup
# -------------------------------------------------

@app.on_event("startup")
async def startup_event():
    print("✅ MIRAGE FastAPI Server Started")


# -------------------------------------------------
# Shutdown
# -------------------------------------------------

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 MIRAGE FastAPI Server Stopped")
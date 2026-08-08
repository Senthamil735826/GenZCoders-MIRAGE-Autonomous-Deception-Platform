from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database.session import engine
from backend.database.models import Base
from backend.api.deps import require_api_key

from backend.dashboard import router as dashboard_router

from backend.deception.routes import (
    router as deception_router,
    public_router,
)


# ============================================================
# Application Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    print("🚀 Starting MIRAGE Platform...")

    # --------------------------------------------------------
    # Initialize database
    # --------------------------------------------------------

    try:
        async with engine.begin() as conn:
            await conn.run_sync(
                Base.metadata.create_all
            )

        print("✅ Database initialized.")

    except Exception as exc:
        print(
            f"❌ Database initialization failed: {exc}"
        )

    # --------------------------------------------------------
    # Application running
    # --------------------------------------------------------

    yield

    # --------------------------------------------------------
    # Shutdown
    # --------------------------------------------------------

    print("🛑 Shutting down MIRAGE Platform...")

    try:
        await engine.dispose()
        print("✅ Database connection closed.")

    except Exception as exc:
        print(
            f"⚠️ Database shutdown error: {exc}"
        )


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "MIRAGE Autonomous Deception Intelligence Platform"
    ),
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=settings.CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# Deception API
# ============================================================

app.include_router(
    deception_router,
    prefix="/api/v1",
    tags=["Deception"],
)


# ============================================================
# Public API
# ============================================================

app.include_router(
    public_router
)


# ============================================================
# Dashboard API
# ============================================================

app.include_router(
    dashboard_router
)


# ============================================================
# Root Endpoint
# ============================================================

@app.get(
    "/",
    tags=["System"],
)
async def root():

    return {
        "platform": settings.APP_NAME,
        "status": "online",
        "version": settings.VERSION,
        "message": "MIRAGE Deception Platform is running",
    }


# ============================================================
# Health Check
# ============================================================

@app.get(
    "/health",
    tags=["System"],
)
async def health():

    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
    }


# ============================================================
# API Information
# ============================================================

@app.get(
    "/api",
    tags=["System"],
)
async def api_info():

    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================
# Protected Admin Endpoint
# ============================================================

@app.get(
    "/admin/deception-logs",
    dependencies=[
        Depends(require_api_key)
    ],
    tags=["Admin"],
)
async def deception_logs():

    return {
        "message": "Access granted!",
        "logs": [],
    }

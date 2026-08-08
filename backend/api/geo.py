"""
geo.py — IP -> lat/lon geolocation for the MIRAGE threat-origin map.

FastAPI router.

Endpoints:
    GET /api/geo
    GET /api/threat-locations

Lookup order:
    1. GeoIP2 / MaxMind GeoLite2
    2. ip-api.com fallback
"""

import time
import sqlite3
from pathlib import Path

import requests
from fastapi import APIRouter


# =========================================================
# Router
# =========================================================

geo_router = APIRouter(
    prefix="/api",
    tags=["Geo"],
)


# =========================================================
# GeoIP2 / MaxMind
# =========================================================

_geoip_reader = None

def _get_geoip_reader():
    global _geoip_reader
    if _geoip_reader is not None:
        return _geoip_reader
    try:
        import geoip2.database
        from pathlib import Path
        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        GEOIP_DB = PROJECT_ROOT / "backend" / "data" / "GeoLite2-City.mmdb"
        if GEOIP_DB.exists():
            _geoip_reader = geoip2.database.Reader(str(GEOIP_DB))
            print(f"✅ GeoIP database loaded: {GEOIP_DB}")
            return _geoip_reader
        else:
            print(f"⚠️ GeoIP database not found: {GEOIP_DB}")
            return None
    except Exception as exc:
        print(f"⚠️ GeoIP database could not be loaded: {exc}")
        return None


def _lookup_geoip2(ip: str):
    """
    Lookup an IP using the local MaxMind database.
    """
    reader = _get_geoip_reader()
    if reader is None:
        return None

    try:
        response = reader.city(ip)
        return {
            "lat": response.location.latitude,
            "lon": response.location.longitude,
            "city": response.city.name,
            "country": response.country.iso_code,
        }
    except Exception:
        return None


# =========================================================
# ip-api.com Fallback
# =========================================================

def _lookup_ip_api(ip: str):
    """
    Fallback geolocation lookup using ip-api.com.
    """

    try:
        url = f"http://ip-api.com/json/{ip}"

        response = requests.get(
            url,
            timeout=2,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            return None

        return {
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "city": data.get("city"),
            "country": data.get("countryCode"),
        }

    except Exception:
        return None


# =========================================================
# Resolve IP
# =========================================================

def resolve_ip(ip: str):
    """
    Try GeoIP2 first.

    If GeoIP2 is unavailable or cannot resolve the IP,
    use ip-api.com as a fallback.
    """

    geo = _lookup_geoip2(ip)

    if geo:
        return geo

    return _lookup_ip_api(ip)


# =========================================================
# Test Endpoint
# =========================================================

@geo_router.get("/geo")
async def get_geo():
    """
    Test whether the Geo API is working.
    """

    return {
        "status": "success",
        "message": "Geo API is working",
    }


# =========================================================
# Threat Locations
# =========================================================

@geo_router.get("/threat-locations")
async def threat_locations():
    """
    Return recent detection events with resolved
    GPS coordinates.

    Expected database table:

        detections

    Expected columns:

        id
        source_ip
        severity
        created_at
    """

    # -----------------------------------------------------
    # Database path
    # -----------------------------------------------------

    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    db_path = PROJECT_ROOT / "mirage.db"

    # If your database is actually located here:
    #
    # db_path = (
    #     PROJECT_ROOT
    #     / "backend"
    #     / "data"
    #     / "mirage.db"
    # )

    if not db_path.exists():
        print(
            f"⚠️ Database not found: {db_path}"
        )

        return []


    # -----------------------------------------------------
    # SQLite connection
    # -----------------------------------------------------

    conn = None

    try:
        conn = sqlite3.connect(
            str(db_path)
        )

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        # Last 15 minutes
        cutoff = time.time() - 900

        cursor.execute(
            """
            SELECT
                id,
                source_ip,
                severity,
                created_at
            FROM detections
            WHERE created_at >= ?
            ORDER BY created_at DESC
            LIMIT 200
            """,
            (cutoff,),
        )

        rows = cursor.fetchall()

    except sqlite3.Error as exc:
        print(
            f"❌ Geo database error: {exc}"
        )

        return []

    finally:
        if conn is not None:
            conn.close()


    # -----------------------------------------------------
    # Resolve locations
    # -----------------------------------------------------

    results = []

    for row in rows:

        source_ip = row["source_ip"]

        if not source_ip:
            continue

        geo = resolve_ip(source_ip)

        if not geo:
            continue

        latitude = geo.get("lat")
        longitude = geo.get("lon")

        if latitude is None or longitude is None:
            continue

        results.append(
            {
                "id": row["id"],
                "lat": latitude,
                "lon": longitude,
                "ip": source_ip,
                "city": geo.get("city"),
                "country": geo.get("country"),
                "severity": row["severity"],
                "ts": row["created_at"],
            }
        )

    return results
"""
honeypot.py
-----------
MIRAGE Honeypot Deployment API.

Provides endpoints to:
    POST /deploy
    GET  /active

This module uses FastAPI and the MIRAGE backend package structure.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/honeypots",
    tags=["Honeypots"],
)


# ============================================================
# Request Models
# ============================================================

class HoneypotCreate(BaseModel):
    """
    Request body for creating a honeypot.
    """

    type: str = Field(
        ...,
        description="Honeypot type: SSH, HTTP, Database, IoT",
    )

    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Honeypot configuration",
    )

    isolated: bool = Field(
        default=True,
        description="Whether the honeypot should run in an isolated environment",
    )

    adaptive_deception: bool = Field(
        default=True,
        description="Enable adaptive deception",
    )


# ============================================================
# Response Model
# ============================================================

class HoneypotResponse(BaseModel):
    """
    Response returned after honeypot deployment.
    """

    id: str
    type: str
    status: str
    isolated: bool
    adaptive_deception: bool
    config: Dict[str, Any] = Field(
        default_factory=dict
    )


# ============================================================
# In-memory registry
# ============================================================

# Temporary registry for the prototype/demo.
#
# Later we can connect this directly to your SQLAlchemy
# Honeypot model and database.

_active_honeypots: Dict[str, HoneypotResponse] = {}


# ============================================================
# Utility
# ============================================================

def generate_honeypot_id() -> str:
    """
    Generate a unique honeypot identifier.
    """

    import uuid

    return f"MIRAGE-{uuid.uuid4().hex[:12].upper()}"


# ============================================================
# Deploy Honeypot
# ============================================================

@router.post(
    "/deploy",
    response_model=HoneypotResponse,
)
async def deploy_honeypot(
    honeypot: HoneypotCreate,
):
    """
    Deploy a new deception asset.

    Supported types:
        SSH
        HTTP
        DATABASE
        IOT
    """

    supported_types = {
        "SSH",
        "HTTP",
        "DATABASE",
        "IOT",
    }

    honeypot_type = honeypot.type.upper()

    if honeypot_type not in supported_types:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported honeypot type: "
                f"{honeypot.type}. "
                f"Supported types: "
                f"{', '.join(sorted(supported_types))}"
            ),
        )

    # --------------------------------------------------------
    # Generate ID
    # --------------------------------------------------------

    honeypot_id = generate_honeypot_id()

    # --------------------------------------------------------
    # Create deployment
    # --------------------------------------------------------

    deployment = HoneypotResponse(
        id=honeypot_id,
        type=honeypot_type,
        status="active",
        isolated=honeypot.isolated,
        adaptive_deception=honeypot.adaptive_deception,
        config=honeypot.config,
    )

    # --------------------------------------------------------
    # Store deployment
    # --------------------------------------------------------

    _active_honeypots[honeypot_id] = deployment

    print(
        f"🪤 Honeypot deployed: "
        f"{honeypot_id} "
        f"[{honeypot_type}]"
    )

    # --------------------------------------------------------
    # Adaptive deception
    # --------------------------------------------------------

    if honeypot.adaptive_deception:

        print(
            f"🧠 Adaptive deception enabled: "
            f"{honeypot_id}"
        )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return deployment


# ============================================================
# List Active Honeypots
# ============================================================

@router.get(
    "/active",
    response_model=List[HoneypotResponse],
)
async def list_active_honeypots():
    """
    Return all active honeypots.
    """

    return [
        honeypot
        for honeypot in _active_honeypots.values()
        if honeypot.status == "active"
    ]


# ============================================================
# Get Honeypot
# ============================================================

@router.get(
    "/{honeypot_id}",
    response_model=HoneypotResponse,
)
async def get_honeypot(
    honeypot_id: str,
):
    """
    Get details of a specific honeypot.
    """

    honeypot = _active_honeypots.get(
        honeypot_id
    )

    if honeypot is None:
        raise HTTPException(
            status_code=404,
            detail="Honeypot not found",
        )

    return honeypot


# ============================================================
# Stop Honeypot
# ============================================================

@router.delete(
    "/{honeypot_id}",
)
async def stop_honeypot(
    honeypot_id: str,
):
    """
    Stop an active honeypot.
    """

    honeypot = _active_honeypots.get(
        honeypot_id
    )

    if honeypot is None:
        raise HTTPException(
            status_code=404,
            detail="Honeypot not found",
        )

    updated = honeypot.model_copy(
        update={
            "status": "stopped"
        }
    )

    _active_honeypots[honeypot_id] = updated

    return {
        "status": "success",
        "message": "Honeypot stopped",
        "honeypot_id": honeypot_id,
    }
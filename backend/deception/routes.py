import io
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
import io
from backend.api.deps import require_api_key
from backend.database.models import (
    AttackLog,
    ContainmentAction,
    Honeytoken,
    Severity,
    TokenType,
    TriggerEvent,
    utcnow,
)
from backend.database.schemas import TokenCreate, TokenOut, TriggerEventOut
from backend.database.session import get_db
from backend.deception import tokens as tk
from backend.deception import generators as g
from backend.response.engine import evaluate_and_contain

# ── management API (protected) ────────────────────────────────────────────
router = APIRouter(dependencies=[Depends(require_api_key)])

# ── public callback + decoys (must stay unauthenticated) ──────────────────
public_router = APIRouter()

@router.get("/containment/actions", response_model=list[dict])
async def list_containment_actions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContainmentAction).order_by(desc(ContainmentAction.created_at)))
    actions = result.scalars().all()
    return [{
        "id": a.id,
        "attacker_ip": a.attacker_ip,
        "action_type": a.action_type,
        "status": a.status,
        "details": a.details,
        "created_at": a.created_at
    } for a in actions]



@router.post("/tokens", response_model=TokenOut, status_code=201)
async def create_token(body: TokenCreate, db: AsyncSession = Depends(get_db)):
    trigger_id = tk.g.new_trigger_id()
    token = Honeytoken(
        trigger_id=trigger_id,
        name=body.name,
        token_type=body.token_type.value,
        plant_location=body.plant_location,
        description=body.description,
        sensitivity=body.sensitivity or tk.default_sensitivity(body.token_type.value),
        artifact=tk.build_artifact(body.token_type.value, trigger_id),
        callback_url=tk.callback_url(trigger_id),
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token


@router.get("/tokens", response_model=list[TokenOut])
async def list_tokens(
    db: AsyncSession = Depends(get_db),
    triggered_only: bool = False,
    limit: int = Query(100, le=500),
    offset: int = 0,
):
    stmt = select(Honeytoken).order_by(desc(Honeytoken.created_at))
    if triggered_only:
        stmt = stmt.where(Honeytoken.trigger_count > 0)
    result = await db.execute(stmt.limit(limit).offset(offset))
    return result.scalars().all()


@router.get("/tokens/{token_id}", response_model=TokenOut)
async def get_token(token_id: int, db: AsyncSession = Depends(get_db)):
    token = await db.get(Honeytoken, token_id)
    if token is None:
        raise HTTPException(404, "Token not found")
    return token


@router.get("/tokens/{token_id}/events", response_model=list[TriggerEventOut])
async def token_events(token_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TriggerEvent)
        .where(TriggerEvent.token_id == token_id)
        .order_by(desc(TriggerEvent.occurred_at))
    )
    return result.scalars().all()


@router.delete("/tokens/{token_id}", status_code=204)
async def deactivate_token(token_id: int, db: AsyncSession = Depends(get_db)):
    token = await db.get(Honeytoken, token_id)
    if token is None:
        raise HTTPException(404, "Token not found")
    token.is_active = False
    await db.commit()
    return Response(status_code=204)


@router.get("/events", response_model=list[TriggerEventOut])
async def all_events(
    db: AsyncSession = Depends(get_db), limit: int = Query(100, le=500)
):
    result = await db.execute(
        select(TriggerEvent).order_by(desc(TriggerEvent.occurred_at)).limit(limit)
    )
    return result.scalars().all()


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count(Honeytoken.id)))
    active = await db.scalar(
        select(func.count(Honeytoken.id)).where(Honeytoken.is_active.is_(True))
    )
    burned = await db.scalar(
        select(func.count(Honeytoken.id)).where(Honeytoken.trigger_count > 0)
    )
    events = await db.scalar(select(func.count(TriggerEvent.id)))
    unique_ips = await db.scalar(
        select(func.count(func.distinct(TriggerEvent.source_ip)))
    )
    by_type = (
        await db.execute(
            select(Honeytoken.token_type, func.count(Honeytoken.id)).group_by(
                Honeytoken.token_type
            )
        )
    ).all()
    return {
        "tokens_total": total or 0,
        "tokens_active": active or 0,
        "tokens_triggered": burned or 0,
        "trigger_events": events or 0,
        "unique_attacker_ips": unique_ips or 0,
        "tokens_by_type": {t: c for t, c in by_type},
    }


# --- NEW: Document Download Endpoint ---
@router.get("/tokens/{token_id}/download")
async def download_token_artifact(token_id: int, db: AsyncSession = Depends(get_db)):
    token = await db.get(Honeytoken, token_id)
    if not token:
        raise HTTPException(404, "Token not found")
        
    if token.token_type != TokenType.DOCUMENT.value:
        raise HTTPException(400, "Only document tokens can be downloaded this way.")
        
    cb = token.artifact.get("_callback") or tk.callback_url(token.trigger_id)
    file_data = g.generate_document_bytes(token.trigger_id, cb)
    
    if not file_data:
        raise HTTPException(500, "Failed to generate document artifact.")
        
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={token.artifact.get('filename', 'document.docx')}"}
    )


# ── the callback: this is what attackers hit ──────────────────────────────

_PIXEL = bytes.fromhex(
    "47494638396101000100800000ffffff00000021f90401000000002c"
    "00000000010001000002024401003b"
)


@public_router.api_route(
    "/t/{trigger_id}",
    methods=["GET", "POST", "PUT", "HEAD"],
    include_in_schema=False,
)
async def honeytoken_callback(
    trigger_id: str, request: Request, db: AsyncSession = Depends(get_db)
):
    clean = trigger_id.split(".")[0] 

    token = (
        await db.execute(select(Honeytoken).where(Honeytoken.trigger_id == clean))
    ).scalar_one_or_none()

    if token is not None:
        body = (await request.body())[:2000].decode("utf-8", errors="replace")
        now = utcnow()

        event = TriggerEvent(
            token_id=token.id,
            source_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent"),
            method=request.method,
            path=str(request.url.path),
            referer=request.headers.get("referer"),
            channel="http",
            headers=dict(request.headers),
            query=dict(request.query_params),
            body_snippet=body or None,
            severity=(
                Severity.CRITICAL.value
                if token.sensitivity >= 8
                else Severity.HIGH.value
            ),
            threat_score=min(100, token.sensitivity * 10),
        )
        db.add(event)
        
        token.trigger_count += 1
        token.last_triggered_at = now
        if token.first_triggered_at is None:
            token.first_triggered_at = now
            
        await db.commit()
        await db.refresh(event) # Ensure event has an ID for containment

        # --- AUTONOMOUS CONTAINMENT TRIGGER ---
        try:
            await evaluate_and_contain(event, token, db)
        except Exception as exc:
            import logging
            logging.getLogger("mirage").exception("containment failed: %s", exc)
            await db.rollback()
        # --------------------------------------

    return Response(content=_PIXEL, media_type="image/gif")


# ── legacy honeypot endpoint, kept ────────────────────────────────────────

@public_router.post("/api/v1/admin/login", include_in_schema=False)
async def fake_admin_login(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        payload = await request.json()
    except Exception:
        payload = {"raw_body": (await request.body()).decode("utf-8", "replace")[:2000]}

    db.add(
        AttackLog(
            source_ip=request.client.host if request.client else "unknown",
            target_port=request.url.port or 8000,
            protocol="http",
            method=request.method,
            path=str(request.url.path),
            user_agent=request.headers.get("user-agent"),
            payload=str(payload)[:4000],
            deception_triggered="fake_admin_login",
            severity=Severity.MEDIUM.value,
            threat_score=40,
            meta={"headers": dict(request.headers)},
        )
    )
    await db.commit()
    raise HTTPException(401, "Invalid credentials. Account locked for 5 minutes.")
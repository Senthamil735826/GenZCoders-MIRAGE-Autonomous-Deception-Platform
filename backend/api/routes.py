from fastapi import APIRouter, Depends
from backend.api.deps import require_api_key

router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_api_key)])


@router.get("/decoys")
async def list_decoys():
    return []
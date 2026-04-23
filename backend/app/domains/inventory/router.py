from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
def inventory_health() -> dict[str, str]:
    return {"status": "ok", "domain": "inventory"}


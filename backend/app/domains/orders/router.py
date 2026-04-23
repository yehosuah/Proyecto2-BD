from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
def orders_health() -> dict[str, str]:
    return {"status": "ok", "domain": "orders"}


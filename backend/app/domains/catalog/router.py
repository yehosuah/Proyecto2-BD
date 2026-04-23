from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
def catalog_health() -> dict[str, str]:
    return {"status": "ok", "domain": "catalog"}


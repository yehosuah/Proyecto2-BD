from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
def reporting_health() -> dict[str, str]:
    return {"status": "ok", "domain": "reporting"}


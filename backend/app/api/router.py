from fastapi import APIRouter

from app.domains.admin.router import router as admin_router
from app.domains.auth.router import router as auth_router
from app.domains.catalog.router import router as catalog_router
from app.domains.inventory.router import router as inventory_router
from app.domains.orders.router import router as orders_router
from app.domains.reporting.router import router as reporting_router


api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(catalog_router, prefix="/catalog", tags=["catalog"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])
api_router.include_router(reporting_router, prefix="/reporting", tags=["reporting"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])


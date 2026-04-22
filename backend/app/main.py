from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="API Proyecto 2",
        version="0.1.0",
        description="API para la tienda, inventario, ventas y reportes del Proyecto 2.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok", "domain": "ok"}

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()

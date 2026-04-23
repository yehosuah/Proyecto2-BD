from fastapi import FastAPI

from app.api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Proyecto 2 Store API",
        version="0.1.0",
        description="Skeleton API for the Proyecto 2 storefront/admin platform.",
    )

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok", "domain": "ok"}

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()


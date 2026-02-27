from __future__ import annotations

import os
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from .api.v1.router import router as v1_router
from .core.config import get_settings
from .core.errors import AppError, DependencyMissingError, InvalidInputError
from .core.logging import configure_logging, new_correlation_id, set_correlation_id
from .repositories.history import HistoryRepository
from .repositories.user import UserRepository
from .repositories.saved_outfits import SavedOutfitRepository
from .services.stylist import StylistService

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.app_name)

    # ✅ CORS MIDDLEWARE (placed correctly here)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost", "http://127.0.0.1"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # health check
    @app.get("/healthz")
    async def _root_healthz():
        return {"ok": True}

    # startup
    @app.on_event("startup")
    async def _startup() -> None:
        history_repo = HistoryRepository(settings.database_path)
        user_repo = UserRepository(settings.database_path)
        saved_repo = SavedOutfitRepository(settings.database_path)

        await history_repo.init()
        await user_repo.init()
        await saved_repo.init()

        app.state.history_repo = history_repo
        app.state.user_repo = user_repo
        app.state.saved_outfits = saved_repo
        app.state.stylist = StylistService(settings, history_repo, saved_repo=saved_repo)
        logger.info("startup_complete")

    # logging middleware
    @app.middleware("http")
    async def correlation_and_access_logs(request: Request, call_next):
        cid = request.headers.get("x-request-id") or new_correlation_id()
        set_correlation_id(cid)

        start = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            import traceback
            print("🔥 ERROR:")
            traceback.print_exc()
            return JSONResponse(status_code=500, content={"detail": str(e)})
        finally:
            latency_ms = int((time.perf_counter() - start) * 1000)
            access_log = logging.getLogger("access")
            access_log.info(
                "request",
                extra={
                    "route": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                },
            )

        response.headers["x-request-id"] = cid
        return response

    # error handlers
    @app.exception_handler(DependencyMissingError)
    async def dep_missing_handler(request: Request, exc: DependencyMissingError):
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(InvalidInputError)
    async def invalid_input_handler(request: Request, exc: InvalidInputError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(status_code=500, content={"detail": "Internal error"})

    # include routes
    app.include_router(v1_router)

    return app


# create app instance
app = create_app()
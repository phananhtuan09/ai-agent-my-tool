"""FastAPI entry point for the AI agent tool foundation shell."""

from __future__ import annotations

from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.agents._registry import AgentRegistry
from backend.api.config import router as config_router
from backend.api.crypto_airdrop import router as crypto_airdrop_router
from backend.api.daily_scheduler import router as daily_scheduler_router
from backend.api.job_finder import router as job_finder_router
from backend.api.pages import router as pages_router
from backend.api.stream import router as stream_router
from backend.shared.events import EventBroker
from backend.shared.settings import ROOT_DIR, load_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    templates_dir = ROOT_DIR / "frontend" / "templates"
    static_dir = ROOT_DIR / "frontend" / "static"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings = load_settings()
        broker = EventBroker()
        registry = AgentRegistry(settings=settings, broker=broker)
        registry.discover()
        registry.initialize()

        scheduler = AsyncIOScheduler()
        scheduler.start()
        for agent in registry.list_agents():
            agent.register_jobs(scheduler)

        app.state.registry = registry
        app.state.scheduler = scheduler
        app.state.templates = Jinja2Templates(directory=str(templates_dir))
        try:
            yield
        finally:
            scheduler.shutdown(wait=False)

    app = FastAPI(
        title="AI Agent Tool",
        summary="Unified web shell for personal automation agents.",
        lifespan=lifespan,
    )

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    app.include_router(pages_router)
    app.include_router(config_router)
    app.include_router(crypto_airdrop_router)
    app.include_router(daily_scheduler_router)
    app.include_router(job_finder_router)
    app.include_router(stream_router)
    return app


app = create_app()

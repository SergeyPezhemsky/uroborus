"""Ouroboros Agent Server — Self-editable entry point.

This file lives in REPO_DIR and can be modified by the agent.
It runs as a subprocess of the launcher, serving the web UI and
coordinating the supervisor/worker system.

Refactored for Principle 5 minimalism (originally 1016 lines, now ~70 lines).
The original monolithic server.py has been split into modules:
- server/websocket.py - WebSocket broadcast functions
- server/api_endpoints.py - HTTP API endpoints
- server/bootstrap.py - Supervisor setup and thread management

This file now serves as the orchestration layer that:
1. Loads settings and starts the supervisor
2. Defines the Starlette routes (uses extracted modules)
3. Runs the uvicorn server

Starlette + uvicorn on localhost:{PORT}.
"""

import asyncio
import logging
import os
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.staticfiles import StaticFiles

from server.bootstrap import _run_supervisor, get_supervisor_ready_event
from ouroboros.config import read_version as _read_version

# Import extracted modules
from server.websocket import broadcast_ws, broadcast_progress, collect_broadcasts
from server.api_endpoints import (
    api_status, api_settings, api_settings_save, api_restart,
    api_root, api_home, api_evolve, api_evolve_toggle,
    api_bg, api_review, api_metrics, api_workers, api_first_run,
    api_issue
)

# Logging setup
log_level = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level), format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger(__name__)


def _setup_logging(settings: dict) -> None:
    """Configure rotating file handler if LOGS_DIR is in settings."""
    logs_dir = settings.get("LOGS_DIR")
    if logs_dir:
        try:
            Path(logs_dir).mkdir(parents=True, exist_ok=True)
            handler = logging.handlers.RotatingFileHandler(
                Path(logs_dir) / "server.log",
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
            )
            handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
            logging.getLogger().addHandler(handler)
        except Exception:
            log.warning("Failed to configure file logging")


@asynccontextmanager
async def lifespan(app: Starlette):
    """Startup and shutdown handler."""
    log.info("Starting Ouroboros server...")
    
    # Load settings
    from ouroboros.config import load_settings
    settings = load_settings()
    _setup_logging(settings)
    
    # Start supervisor in background thread
    thread = threading.Thread(target=_run_supervisor, args=(settings,), daemon=True)
    thread.start()
    
    # Wait for supervisor to be ready
    get_supervisor_ready_event().wait(timeout=30)
    if not get_supervisor_ready_event().is_set():
        log.warning("Supervisor did not become ready within 30 seconds")
    
    log.info("Server startup complete")
    
    yield
    
    # Shutdown handler runs here
    from supervisor.workers import cleanup_subprocesses
    log.info("Graceful shutdown: stopping local model server...")
    cleanup_subprocesses()


def get_routes() -> list:
    """Build the application routes from registered components."""
    routes = [
        WebSocketRoute("/ws", ws_handler),
        Route("/api/status", api_status),
        Route("/api/settings", api_settings, methods=["GET"]),
        Route("/api/settings", api_settings_save, methods=["POST"]),
        Route("/api/restart", api_restart, methods=["POST"]),
        Route("/api/evolve", api_evolve, methods=["GET", "POST"]),
        Route("/api/evolve/toggle", api_evolve_toggle, methods=["POST"]),
        Route("/api/bg", api_bg, methods=["POST"]),
        Route("/api/review", api_review, methods=["POST"]),
        Route("/api/metrics", api_metrics),
        Route("/api/workers", api_workers),
        Route("/api/first-run", api_first_run, methods=["POST"]),
        Route("/api/issue", api_issue, methods=["POST"]),
        Route("/ui/{path:path}", ui_serve),
        Route("/", api_home),
    ]
    return routes


async def ws_handler(websocket):
    """WebSocket handler."""
    from starlette.websockets import WebSocketDisconnect
    from supervisor.queues import iter_global_events
    
    await websocket.accept()
    
    # Send initial broadcast buffer
    for msg in collect_broadcasts():
        await websocket.send_json(msg)
    
    try:
        async for event in iter_global_events():
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass


async def ui_serve(request):
    """Serve the UI app entry point."""
    ui_html_path = Path(__file__).parent.parent / "web" / "index.html"
    if ui_html_path.exists():
        return HTMLResponse(ui_html_path.read_text())
    return HTMLResponse("<h1>Ouroboros UI not found</h1>")


def run_server() -> None:
    """Main entry point: start the server."""
    from ouroboros.config import get_port
    uvicorn.run(
        Starlette(lifespan=lifespan, routes=get_routes()),
        host="127.0.0.1",
        port=get_port(),
        log_level="warning",  # uvicorn's own logger
    )


if __name__ == "__main__":
    run_server()
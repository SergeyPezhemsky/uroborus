"""API endpoints for the Ouroboros server.
Extracted from server.py for P5 compliance (modularization).
"""

import json
import logging
import os
import shutil
import subprocess
import threading
import time
from typing import Any, Dict

from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse, HTMLResponse
import httpx


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

_supervisor_ready = threading.Event()
_supervisor_error = None
APP_START = time.time()


# ---------------------------------------------------------------------------
# Helper: read version
# ---------------------------------------------------------------------------

def _read_version() -> str:
    """Read version from VERSION file."""
    import pathlib
    repo_dir = pathlib.Path(os.environ.get("OUROBOROS_REPO_DIR", pathlib.Path(__file__).parent.parent))
    version_file = repo_dir / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "unknown"


# ---------------------------------------------------------------------------
# API: Health
# ---------------------------------------------------------------------------

async def api_health(request: Request) -> JSONResponse:
   runtime_version = _read_version()
    app_version = os.environ.get("OUROBOROS_APP_VERSION", "").strip() or runtime_version
    return JSONResponse({
        "status": "ok",
        # legacy field for backward compatibility
        "version": runtime_version,
        "runtime_version": runtime_version,
        "app_version": app_version,
    })


# ---------------------------------------------------------------------------
# API: State
# ---------------------------------------------------------------------------

async def api_state(request: Request) -> JSONResponse:
    try:
        from supervisor.state import load_state, budget_remaining, budget_pct, TOTAL_BUDGET_LIMIT
        from supervisor.workers import WORKERS, PENDING, RUNNING
        st = load_state()
        alive = 0
        total_w = 0
        try:
            alive = sum(1 for w in WORKERS.values() if w.proc.is_alive())
            total_w = len(WORKERS)
        except Exception:
            pass
        spent = float(st.get("spent_rub") or st.get("spent_usd") or 0.0)
        limit = float(TOTAL_BUDGET_LIMIT or 1000.0)
        return JSONResponse({
            "uptime": int(time.time() - APP_START),
            "workers_alive": alive,
            "workers_total": total_w,
            "pending_count": len(PENDING),
            "running_count": len(RUNNING),
            "spent_rub": round(spent, 4),
            "budget_limit": limit,
            "budget_pct": round((spent / limit * 100) if limit > 0 else 0, 1),
            "branch": st.get("current_branch", "ouroboros"),
            "sha": (st.get("current_sha") or "")[:8],
            "evolution_enabled": bool(st.get("evolution_mode_enabled")),
            "bg_consciousness_enabled": bool(st.get("bg_consciousness_enabled")),
            "evolution_cycle": int(st.get("evolution_cycle") or 0),
            "spent_calls": int(st.get("spent_calls") or 0),
            "supervisor_ready": _supervisor_ready.is_set(),
            "supervisor_error": _supervisor_error,
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# API: Settings
# ---------------------------------------------------------------------------

async def api_settings_get(request: Request) -> JSONResponse:
    from ouroboros.config import load_settings, SETTINGS_DEFAULTS
    settings = load_settings()
    safe = {k: v for k, v in settings.items()}
    for key in ("API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GITHUB_TOKEN"):
        if safe.get(key):
            safe[key] = safe[key][:8] + "..." if len(safe[key]) > 8 else "***"
    return JSONResponse(safe)


async def api_settings_post(request: Request) -> JSONResponse:
    try:
        from ouroboros.config import load_settings, save_settings, apply_settings_to_env, SETTINGS_DEFAULTS
        body = await request.json()
        # Backward compat: legacy clients may still send OPENROUTER_API_KEY
        if "OPENROUTER_API_KEY" in body and "API_KEY" not in body:
            body["API_KEY"] = body["OPENROUTER_API_KEY"]
        current = load_settings()
        for key in SETTINGS_DEFAULTS:
            if key in body:
                current[key] = body[key]
        save_settings(current)
        apply_settings_to_env(current)
        _repo_slug = current.get("GITHUB_REPO", "")
        _gh_token = current.get("GITHUB_TOKEN", "")
        if _repo_slug and _gh_token:
            from supervisor.git_ops import configure_remote
            configure_remote(_repo_slug, _gh_token)
        return JSONResponse({"status": "saved"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


# ---------------------------------------------------------------------------
# API: Reset
# ---------------------------------------------------------------------------

async def api_reset(request: Request) -> JSONResponse:
    """Reset all runtime data (state, memory, logs, settings) but keep repo.
    After reset the launcher will show the onboarding wizard on next start.
    """
    import pathlib

    DATA_DIR = pathlib.Path(os.environ.get("OUROBOROS_DATA_DIR",
        pathlib.Path.home() / "Ouroboros" / "data"))
    try:
        deleted = []
        for subdir in ("state", "memory", "logs", "archive", "locks", "task_results"):
            p = DATA_DIR / subdir
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)
                deleted.append(subdir)
        settings_file = DATA_DIR / "settings.json"
        if settings_file.exists():
            settings_file.unlink()
            deleted.append("settings.json")
        _request_restart_exit()
        return JSONResponse({"status": "ok", "deleted": deleted, "restarting": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# API: Command
# ---------------------------------------------------------------------------

async def api_command(request: Request) -> JSONResponse:
    try:
        body = await request.json()
        cmd = body.get("cmd", "")
        if cmd:
            from supervisor.message_bus import get_bridge
            bridge = get_bridge()
            bridge.ui_send(cmd)
        return JSONResponse({"status": "ok"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


# ---------------------------------------------------------------------------
# API: Git Log
# ---------------------------------------------------------------------------

async def api_git_log(request: Request) -> JSONResponse:
    """Return recent commits, tags, and current branch/sha."""
    try:
        from supervisor.git_ops import list_commits, list_versions, git_capture
        commits = list_commits(max_count=30)
        tags = list_versions(max_count=20)
        rc, branch, _ = git_capture(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        rc2, sha, _ = git_capture(["git", "rev-parse", "--short", "HEAD"])
        return JSONResponse({
            "commits": commits,
            "tags": tags,
            "branch": branch.strip() if rc == 0 else "unknown",
            "sha": sha.strip() if rc2 == 0 else "",
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# API: Git Rollback
# ---------------------------------------------------------------------------

async def api_git_rollback(request: Request) -> JSONResponse:
    """Roll back to a specific commit or tag, then restart."""
    try:
        body = await request.json()
        target = body.get("target", "").strip()
        if not target:
            return JSONResponse({"error": "missing target"}, status_code=400)
        from supervisor.git_ops import rollback_to_version
        ok, msg = rollback_to_version(target, reason="ui_rollback")
        if not ok:
            return JSONResponse({"error": msg}, status_code=400)
        _request_restart_exit()
        return JSONResponse({"status": "ok", "message": msg})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# API: Git Promote
# ---------------------------------------------------------------------------

async def api_git_promote(request: Request) -> JSONResponse:
    """Promote current ouroboros branch to ouroboros-stable."""
    try:
        import pathlib
        REPO_DIR = pathlib.Path(os.environ.get("OUROBOROS_REPO_DIR", pathlib.Path(__file__).parent.parent))
        subprocess.run(["git", "branch", "-f", "ouroboros-stable", "ouroboros"],
               cwd=str(REPO_DIR), check=True, capture_output=True)
        return JSONResponse({"status": "ok", "message": "ouroboros-stable updated to match ouroboros"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# API: Models list endpoint (Cloud.ru /v1/models proxy with cache)
# ---------------------------------------------------------------------------

_models_cache: Dict[str, Any] = {"ts": 0.0, "models": []}
_MODELS_CACHE_TTL = 300  # 5 min

async def api_models(request: Request) -> JSONResponse:
    """Return available Cloud.ru models. Cached for 5 minutes."""
    now = time.time()
    if now - _models_cache["ts"] < _MODELS_CACHE_TTL and _models_cache["models"]:
        return JSONResponse({"models": _models_cache["models"]})

    api_key = os.environ.get("API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://foundation-models.api.cloud.ru/v1")

    hardcoded = [
        "zai-org/GLM-4.7",
    ]

    if not api_key:
        return JSONResponse({"models": hardcoded})

    try:
        url = base_url.rstrip("/") + "/models"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers={"Authorization": f"Bearer {api_key}"})
            resp.raise_for_status()
            data = resp.json()

        names = sorted(m.get("id", "") for m in data.get("data", []) if m.get("id"))

        for h in hardcoded:
            if h not in names:
                names.insert(0, h)

        _models_cache["ts"] = now
        _models_cache["models"] = names
        return JSONResponse({"models": names})
    except Exception as e:
        log.warning("Failed to fetch models from %s: %s", base_url, e)
        return JSONResponse({"models": _models_cache.get("models") or hardcoded})


# ---------------------------------------------------------------------------
# API: Cost breakdown
# ---------------------------------------------------------------------------

async def api_cost_breakdown(request: Request) -> JSONResponse:
    """Aggregate llm_usage events from events.jsonl into cost breakdowns."""
    import pathlib

    DATA_DIR = pathlib.Path(os.environ.get("OUROBOROS_DATA_DIR",
        pathlib.Path.home() / "Ouroboros" / "data"))
    events_path = DATA_DIR / "logs" / "events.jsonl"

    by_model: Dict[str, Dict[str, Any]] = {}
    by_api_key: Dict[str, Dict[str, Any]] = {}
    by_model_category: Dict[str, Dict[str, Any]] = {}
    by_task_category: Dict[str, Dict[str, Any]] = {}
    total_cost = 0.0
    total_calls = 0

    def _acc(d, key):
        if key not in d:
            d[key] = {"cost": 0.0, "calls": 0}
        return d[key]

    try:
        if events_path.exists():
            with events_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        evt = json.loads(line)
                    except Exception:
                        continue
                    if evt.get("type") != "llm_usage":
                        continue
                    cost = float(evt.get("cost") or 0)
                    model = str(evt.get("model") or "unknown")
                    api_key_type = str(evt.get("api_key_type") or evt.get("provider") or "cloudru")
                    model_cat = str(evt.get("model_category") or "other")
                    task_cat = str(evt.get("category") or "task")

                    total_cost += cost
                    total_calls += 1

                    e = _acc(by_model, model)
                    e["cost"] += cost
                    e["calls"] += 1

                    e = _acc(by_api_key, api_key_type)
                    e["cost"] += cost
                    e["calls"] += 1

                    e = _acc(by_model_category, model_cat)
                    e["cost"] += cost
                    e["calls"] += 1

                    e = _acc(by_task_category, task_cat)
                    e["cost"] += cost
                    e["calls"] += 1
    except Exception:
        pass

    def _sorted(d):
        return dict(sorted(d.items(), key=lambda x: x[1]["cost"], reverse=True))

    return JSONResponse({
        "total_cost": round(total_cost, 4),
        "total_calls": total_calls,
        "by_model": _sorted(by_model),
        "by_api_key": _sorted(by_api_key),
        "by_model_category": _sorted(by_model_category),
        "by_task_category": _sorted(by_task_category),
    })


# ---------------------------------------------------------------------------
# API: Local model endpoints
# ---------------------------------------------------------------------------

async def api_local_model_start(request: Request) -> JSONResponse:
    try:
        body = await request.json()
        source = body.get("source", "").strip()
        filename = body.get("filename", "").strip()
        port = int(body.get("port", 8766))
        n_gpu_layers = int(body.get("n_gpu_layers", -1))
        n_ctx = int(body.get("n_ctx", 0))
        chat_format = body.get("chat_format", "chatml-function-calling").strip()

        if not source:
            return JSONResponse({"error": "source is required"}, status_code=400)

        from ouroboros.local_model import get_manager
        mgr = get_manager()

        if mgr.is_running:
            return JSONResponse({"error": "Local model server is already running"}, status_code=409)

        # Download can be slow, run in thread to not block the async event loop
        import asyncio
        model_path = await asyncio.to_thread(mgr.download_model, source, filename)

        mgr.start_server(model_path, port=port, n_gpu_layers=n_gpu_layers, n_ctx=n_ctx, chat_format=chat_format)
        return JSONResponse({"status": "starting", "model_path": model_path})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_local_model_stop(request: Request) -> JSONResponse:
    try:
        from ouroboros.local_model import get_manager
        get_manager().stop_server()
        return JSONResponse({"status": "stopped"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def api_local_model_status(request: Request) -> JSONResponse:
    try:
        from ouroboros.local_model import get_manager
        get_manager()
        get_manager()
        return JSONResponse(get_manager().status_dict())
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})


async def api_local_model_test(request: Request) -> JSONResponse:
    try:
        from ouroboros.local_model import get_manager
        mgr = get_manager()
        if not mgr.is_running:
            return JSONResponse({"error": "Local model server is not running"}, status_code=400)
        result = mgr.test_tool_calling()
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# Helper: request restart exit
# ---------------------------------------------------------------------------

_restart_requested = threading.Event()
RESTART_EXIT_CODE = 42

def _request_restart_exit():
    global _restart_requested
    _restart_requested.set()


def get_restart_requested():
    return _restart_requested


# ---------------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------------

async def index_page(request: Request) -> FileResponse:
    import pathlib
    REPO_DIR = pathlib.Path(os.environ.get("OUROBOROS_REPO_DIR", pathlib.Path(__file__).parent.parent))
    index = REPO_DIR / "web" / "index.html"
    if index.exists():
        return FileResponse(str(index), media_type="text/html")
    return HTMLResponse("<html><body><h1>Ouroboros — web/ not found</h1></body></html>", status_code=404)
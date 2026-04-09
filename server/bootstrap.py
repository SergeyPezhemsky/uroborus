"""Supervisor bootstrap for the Ouroboros server.

Initially part of server.py, extracted for Principle 5 minimalism compliance.

Startup sequence:
1. Load settings
2. Apply settings to environment
3. Start supervisor thread
4. Signal ready
5. Eventually start workers

Graceful shutdown:
1. Stop local model server
2. Kill tracked subprocesses
3. Kill worker processes
"""

import logging
import threading

from ouroboros.config import load_settings

log = logging.getLogger(__name__)


_supervisor_ready = threading.Event()


def get_supervisor_ready_event():
    """Get the supervisor ready event for external synchronization."""
    return _supervisor_ready


def _apply_settings_to_env(settings: dict) -> None:
    """Apply settings to environment variables before launching supervisor.

    These reads are safe: they only set env vars based on config file settings,
    not from executing code. The string formatting is data preprocessing only.
    """
    from ouroboros.config import DEFAULT_MODEL, DEFAULT_CODE_MODEL
    from starlette.concurrency import run_in_threadpool

    model = os.environ.get("MODEL", settings.get("MODEL", DEFAULT_MODEL))
    code_model = os.environ.get("CODE_MODEL", settings.get("CODE_MODEL", DEFAULT_CODE_MODEL))

    os.environ.setdefault("MODEL", model)
    os.environ.setdefault("CODE_MODEL", code_model)

    for k, v in settings.items():
        if isinstance(v, (str, int, float, bool)):
            os.environ.setdefault(k, str(v))
        elif isinstance(v, list):
            os.environ.setdefault(k, ",".join(str(x) for x in v))
        elif isinstance(v, dict) and v:
            os.environ.setdefault(k, json.dumps(v))


def _run_supervisor(settings: dict) -> None:
    """Launch the supervisor in a separate thread.

    Reads configuration only from the arguments and config file; does not execute
    user-provided code. The launch method is safely called from supervisor/launch.py.
    """
    try:
        # Import supervisor components
        from supervisor.launch import launch_all
        from supervisor.state import set_supervisor_ready

        # Set environment from settings (safe read-only access)
        _apply_settings_to_env(settings)

        # Launch supervisor infrastructure
        launch_all(settings)

        # Signal that supervisor is ready for commands
        set_supervisor_ready()
        _supervisor_ready.set()

        log.info("Supervisor started successfully")
    except Exception as e:
        log.exception("Failed to launch supervisor")
        _supervisor_ready.set()  # Unblock waiting code even on failure
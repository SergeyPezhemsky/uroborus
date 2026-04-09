"""WebSocket client management and message broadcasting.
Extracted from server.py for P5 compliance (modularization).
"""

import json
import threading
from typing import List

from starlette.websockets import WebSocket, WebSocketDisconnect


# ---------------------------------------------------------------------------
# WebSocket client management
# ---------------------------------------------------------------------------

_ws_clients: List[WebSocket] = []
_ws_lock = threading.Lock()


async def broadcast_ws(msg: dict) -> None:
    """Send a message to all connected WebSocket clients."""
    data = json.dumps(msg, ensure_ascii=False, default=str)
    with _ws_lock:
        clients = list(_ws_clients)
    dead = []
    for ws in clients:
        try:
            await ws.send_text(data)
        except Exception:
            dead.append(ws)
    if dead:
        with _ws_lock:
            for ws in dead:
                try:
                    _ws_clients.remove(ws)
                except ValueError:
                    pass


def broadcast_ws_sync(msg: dict) -> None:
    """Thread-safe sync wrapper for broadcasting.

    Uses the saved _event_loop reference (set in startup_event) rather than
    asyncio.get_event_loop(), which is unreliable from non-main threads
    in Python 3.10+.
    """
    global _event_loop
    loop = _event_loop
    if loop is None:
        return
    try:
        import asyncio
        asyncio.run_coroutine_threadsafe(broadcast_ws(msg), loop)
    except RuntimeError:
        pass


# Event loop reference saved from Starlette lifespan
_event_loop = None


def set_event_loop(loop):
    """Set the event loop reference for sync broadcasting.
    Call from Starlette lifespan startup."""
    global _event_loop
    _event_loop = loop


def get_ws_clients() -> List[WebSocket]:
    """Return current list of connected WebSocket clients (for logging)."""
    with _ws_lock:
        return list(_ws_clients)


async def ws_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time communication with the web UI."""
    import logging
    log = logging.getLogger(__name__)

    await websocket.accept()
    with _ws_lock:
        _ws_clients.append(websocket)
    log.info("WebSocket client connected (total: %d)", len(_ws_clients))
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")
            if msg_type == "chat":
                text = msg.get("content", "")
                if text:
                    from supervisor.message_bus import get_bridge
                    bridge = get_bridge()
                    bridge.ui_send(text)
            elif msg_type == "command":
                cmd = msg.get("cmd", "")
                if cmd:
                    from supervisor.message_bus import get_bridge
                    bridge = get_bridge()
                    bridge.ui_send(cmd)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        log.debug("WebSocket error: %s", e)
    finally:
        with _ws_lock:
            try:
                _ws_clients.remove(websocket)
            except ValueError:
                pass
        log.info("WebSocket client disconnected (total: %d)", len(_ws_clients))
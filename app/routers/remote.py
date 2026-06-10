from collections import defaultdict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


class ConnectionManager:
    def __init__(self):
        self.sessions: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        self.sessions[session_id].append(ws)

    def disconnect(self, session_id: str, ws: WebSocket):
        try:
            self.sessions[session_id].remove(ws)
        except ValueError:
            pass

    async def broadcast(self, session_id: str, message: str, sender: WebSocket):
        for ws in list(self.sessions[session_id]):
            if ws is not sender:
                try:
                    await ws.send_text(message)
                except Exception:
                    pass


manager = ConnectionManager()


@router.get("/remote/{session_id}", response_class=HTMLResponse)
def remote_page(session_id: str, request: Request):
    return templates.TemplateResponse(
        "remote.html", {"request": request, "session_id": session_id}
    )


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(ws: WebSocket, session_id: str):
    await manager.connect(session_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast(session_id, data, sender=ws)
    except WebSocketDisconnect:
        manager.disconnect(session_id, ws)
    except Exception:
        manager.disconnect(session_id, ws)

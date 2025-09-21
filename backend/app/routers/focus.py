from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

router = APIRouter()


rooms_clients: Dict[str, Set[WebSocket]] = {}


@router.post("/rooms")
def create_room(payload: dict):
    # Stub: create and return room
    room_id = payload.get("id") or "public-room"
    return {"id": room_id, "name": payload.get("name", "Public Room"), "type": payload.get("type", "public"), "status": "active"}


@router.get("/rooms")
def list_rooms():
    return {"items": [{"id": "public-room", "name": "Public Room", "type": "public", "status": "active"}]}


@router.get("/rooms/{room_id}")
def get_room(room_id: str):
    return {"id": room_id, "name": "Public Room", "type": "public", "status": "active"}


@router.post("/rooms/{room_id}/sessions/start")
def start_session(room_id: str):
    return {"ok": True, "room_id": room_id, "started": True}


@router.post("/rooms/{room_id}/sessions/stop")
def stop_session(room_id: str):
    return {"ok": True, "room_id": room_id, "stopped": True}


@router.websocket("/v1/rooms/{room_id}/socket")
async def room_socket(websocket: WebSocket, room_id: str):
    await websocket.accept()
    clients = rooms_clients.setdefault(room_id, set())
    clients.add(websocket)
    try:
        await websocket.send_json({"event": "joined", "room_id": room_id, "peers": len(clients)})
        while True:
            msg = await websocket.receive_json()
            # Broadcast timer ticks / presence
            data = {"event": "broadcast", "payload": msg}
            for client in list(clients):
                if client is not websocket:
                    await client.send_json(data)
    except WebSocketDisconnect:
        clients.remove(websocket)
    except Exception:
        clients.discard(websocket)


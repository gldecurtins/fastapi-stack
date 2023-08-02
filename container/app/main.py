from connection import ConnectionManager
from message import MessageManager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles


app = FastAPI()


connections = ConnectionManager()


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await connections.connect(websocket)
    try:
        while True:
            received_text = await websocket.receive_text()
            await MessageManager().validate_received_text(
                received_text, websocket, connections
            )
    except WebSocketDisconnect:
        await connections.disconnect(websocket)


app.mount("/", StaticFiles(directory="static", html=True), name="static")

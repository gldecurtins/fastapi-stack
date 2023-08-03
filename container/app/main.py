from server import ServerManager
from message import MessageManager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    server = ServerManager()

    await server.connect(websocket)
    try:
        while True:
            received_text = await websocket.receive_text()
            await MessageManager().validate_received_text(received_text, websocket, server.connections)
    except WebSocketDisconnect:
        await server.disconnect(websocket)


app.mount("/", StaticFiles(directory="static", html=True), name="static")

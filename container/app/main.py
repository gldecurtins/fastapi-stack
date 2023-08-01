from connection import ConnectionManager
from command import CommandManager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles


app = FastAPI()


connections = ConnectionManager()


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await connections.connect(websocket, connections)
    try:
        while True:
            received_text = await websocket.receive_text()
            await CommandManager().search_for_command(
                received_text, websocket, connections
            )
    except WebSocketDisconnect:
        await connections.disconnect(websocket, connections)


app.mount("/", StaticFiles(directory="static", html=True), name="static")

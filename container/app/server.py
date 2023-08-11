from message import MessageManager
from fastapi import WebSocket
from faker import Faker


def get_random_name(websocket: WebSocket):
    accept_language = str(websocket.headers.get("accept-language")).split(";")[0]
    locales = accept_language.split(",")
    faker = Faker(locales)
    faker = Faker()
    return faker.unique.first_name()


class ServerManager:
    connections = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections[websocket] = {}
        self.connections[websocket]["user_name"] = get_random_name(websocket)
        self.connections[websocket]["channel_name"] = "1"
        await MessageManager().connected(websocket, self.connections)

    async def disconnect(self, websocket: WebSocket):
        await MessageManager().disconnected(websocket, self.connections)
        del self.connections[websocket]

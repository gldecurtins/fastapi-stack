from typing import TypedDict, NotRequired
from fastapi import WebSocket
from faker import Faker


def get_random_name():
    faker = Faker()
    return faker.unique.first_name()


class Connection(TypedDict):
    user_name: str
    channel_name: str
    channel_password: NotRequired[str]


class ConnectionManager:
    def __init__(self):
        self.connections: Connection = {}

    async def connect(self, websocket: WebSocket, connections: dict):
        await websocket.accept()
        self.connections[websocket] = {}
        self.connections[websocket]["user_name"] = get_random_name()
        self.connections[websocket]["channel_name"] = "1"
        text = f">> {self.connections[websocket]['user_name']} connected"
        await self.send_to_user(text, websocket)
        await self.send_to_channel(text, websocket, connections)

    async def disconnect(self, websocket: WebSocket, connections: dict):
        text = f">> {self.connections[websocket]['user_name']} disconnected"
        await self.send_to_channel(text, websocket, connections)
        del self.connections[websocket]

    async def send_to_user(self, text: str, websocket: WebSocket):
        await websocket.send_text(text)

    async def send_to_channel(self, text: str, websocket: WebSocket, connections: dict):
        from_channel_name = connections.connections[websocket]["channel_name"]
        for connection in connections.connections:
            to_channel_name = connections.connections[connection]["channel_name"]
            if from_channel_name is to_channel_name and connection is not websocket:
                await connection.send_text(text)

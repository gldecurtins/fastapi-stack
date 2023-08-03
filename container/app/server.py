from message import MessageManager
from fastapi import WebSocket
from faker import Faker


def get_random_name():
    faker = Faker()
    return faker.unique.first_name()


class ServerManager:
    connections = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections[websocket] = {}
        self.connections[websocket]["user_name"] = get_random_name()
        self.connections[websocket]["channel_name"] = "1"
        text_to_send = f">> {self.connections[websocket]['user_name']} connected"
        await MessageManager().send_text_to_user(text_to_send, websocket)
        await MessageManager().send_text_to_channel(text_to_send, websocket, self.connections)

    async def disconnect(self, websocket: WebSocket):
        text_to_send = f">> {self.connections[websocket]['user_name']} disconnected"
        await MessageManager().send_text_to_channel(text_to_send, websocket, self.connections)
        del self.connections[websocket]

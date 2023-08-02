from typing import TypedDict, NotRequired
from message import MessageManager
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

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections[websocket] = {}
        self.connections[websocket]["user_name"] = get_random_name()
        self.connections[websocket]["channel_name"] = "1"
        text_to_send = f">> {self.connections[websocket]['user_name']} connected"
        await MessageManager.send_text_to_user(self, text_to_send, websocket)
        await MessageManager.send_text_to_channel(
            self,
            text_to_send=text_to_send,
            websocket=websocket,
            connections=self,
        )

    async def disconnect(self, websocket: WebSocket):
        text_to_send = f">> {self.connections[websocket]['user_name']} disconnected"
        await MessageManager.send_text_to_channel(
            self,
            text_to_send=text_to_send,
            websocket=websocket,
            connections=self,
        )
        del self.connections[websocket]

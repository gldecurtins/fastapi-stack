from fastapi import WebSocket
import logging


class MessageManager:
    async def validate_received_text(self, received_text: str, websocket: WebSocket, connections: dict):
        lower_received_text = received_text.lower()
        if lower_received_text.startswith("a."):
            await self.send_text_as_action(received_text, websocket, connections)

        elif lower_received_text.startswith("s."):
            await self.show_connections(websocket, connections)

        elif lower_received_text.startswith("c."):
            await self.change_channel(received_text, websocket, connections)

        elif lower_received_text.startswith("h."):
            await self.help_cmd(websocket)

        elif lower_received_text.startswith("w."):
            await self.whisper_text_to_user(received_text, websocket, connections)

        else:
            await self.send_text_to_channel(
                f"<{connections[websocket]['user_name']}> {received_text}",
                websocket,
                connections,
            )

    async def connected(self, websocket: WebSocket, connections: dict):
        text_to_send = f">> {connections[websocket]['user_name']} connected"
        await self.send_text_to_user(text_to_send, websocket)

    async def disconnected(self, websocket: WebSocket, connections: dict):
        text_to_send = f">> {connections[websocket]['user_name']} disconnected"
        await self.send_text_to_channel(text_to_send, websocket, connections)

    async def send_text_to_user(self, text_to_send: str, websocket: WebSocket):
        await websocket.send_text(text_to_send)

    async def send_text_to_channel(self, text_to_send: str, websocket: WebSocket, connections: dict):
        user_in_channel = connections[websocket]["channel_name"]
        for connection in connections:
            channel_name = connections[connection]["channel_name"]
            if user_in_channel is channel_name and connection is not websocket:
                await connection.send_text(text_to_send)

    async def send_text_as_action(self, received_text: str, websocket: WebSocket, connections: dict):
        action_text = f"-> {connections[websocket]['user_name']} {str(received_text.split(' ', 1)[1])}"
        await self.send_text_to_user(action_text, websocket)
        await self.send_text_to_channel(action_text, websocket, connections)

    async def whisper_text_to_user(self, received_text: str, websocket: WebSocket, connections: dict):
        try:
            to_user = received_text.split()[1].capitalize()
            text = f"<*{connections[websocket]['user_name']}*> {received_text.split(' ', 2)[2]}"

            for connection, detail in connections.items():
                if detail["user_name"] == to_user:
                    await self.send_text_to_user(text, connection)
        except IndexError:
            await self.send_text_to_user(">> w. <user name> <text> to whisper", websocket)

    async def change_channel(self, received_text: str, websocket: WebSocket, connections: dict):
        try:
            channel_name = received_text.split()[1]
            await self.send_text_to_channel(
                f">> {connections[websocket]['user_name']} leaves this channel",
                websocket,
                connections,
            )
            connections[websocket]["channel_name"] = channel_name
            await self.send_text_to_user(f">> Channel changed to {channel_name}", websocket)
            await self.send_text_to_channel(
                f">> {connections[websocket]['user_name']} joined this channel",
                websocket,
                connections,
            )
        except IndexError:
            await self.send_text_to_user(">> c. <channel name> to change the channel", websocket)

    async def show_connections(self, websocket: WebSocket, connections: dict):
        await self.send_text_to_user(
            f"+---------------------------------------+",
            websocket,
        )
        for connection in connections:
            await self.send_text_to_user(
                f"| {(connections[connection]['user_name'] + ' ').ljust(20, '.')} {connections[connection]['channel_name'].ljust(16)} |",
                websocket,
            )
        await self.send_text_to_user(
            f"+---------------------------------------+",
            websocket,
        )
        await self.send_text_to_user(
            f"| Name:                Channel:         |",
            websocket,
        )
        await self.send_text_to_user(
            f"+---------------------------------------+",
            websocket,
        )

    async def help_cmd(self, websocket: WebSocket):
        help_text = [
            ">> a. <text> action something",
            ">> c. <channel name> to change the channel",
            ">> w. <user name> <text> to whisper",
            ">> s. to show who's online",
            ">> h. to show this help",
            ">> e. to disconnect",
        ]
        for text in reversed(help_text):
            await self.send_text_to_user(text, websocket)

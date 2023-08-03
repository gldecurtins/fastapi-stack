from fastapi import WebSocket


class MessageManager:
    async def validate_received_text(
        self, received_text: str, websocket: WebSocket, connections: dict
    ):
        lower_received_text = received_text.lower()
        if lower_received_text.startswith("a.") or lower_received_text.startswith(
            "action"
        ):
            await self.send_text_as_action(received_text, websocket, connections)

        elif lower_received_text.startswith("s.") or lower_received_text.startswith(
            "show"
        ):
            await self.show_connections(websocket, connections)

        elif lower_received_text.startswith("c.") or lower_received_text.startswith(
            "channel"
        ):
            await self.change_channel(received_text, websocket, connections)
        elif lower_received_text.startswith("h.") or lower_received_text.startswith(
            "help"
        ):
            await self.help_cmd(websocket)
        else:
            await self.send_text_to_user(received_text, websocket)
            await self.send_text_to_channel(
                f"<{connections[websocket]['user_name']}> {received_text}",
                websocket,
                connections,
            )

    async def send_text_to_user(self, text_to_send: str, websocket: WebSocket):
        await websocket.send_text(text_to_send)

    async def send_text_to_channel(
        self, text_to_send: str, websocket: WebSocket, connections: dict
    ):
        user_in_channel = connections[websocket]["channel_name"]
        for connection in connections:
            channel_name = connections[connection]["channel_name"]
            if user_in_channel is channel_name and connection is not websocket:
                await connection.send_text(text_to_send)

    async def send_text_as_action(
        self, received_text: str, websocket: WebSocket, connections: dict
    ):
        action_text = (
            f"-> {connections[websocket]['user_name']} {received_text.split(' ', 1)[1]}"
        )
        await self.send_text_to_user(action_text, websocket)
        await self.send_text_to_channel(action_text, websocket, connections)

    async def change_channel(
        self, received_text: str, websocket: WebSocket, connections: dict
    ):
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

    async def show_connections(self, websocket: WebSocket, connections: dict):
        for connection in connections:
            await self.send_text_to_user(
                f"{connections[connection]['user_name']} @{connections[connection]['channel_name']}",
                websocket,
            )

    async def help_cmd(self, websocket: WebSocket):
        help_text = [
            "a. or action <text> action something",
            "c. or channel <channel name> to change the channel",
            "s. or show to show who's online",
            "h. or help to show this help",
        ]
        for text in reversed(help_text):
            await self.send_text_to_user(text, websocket)

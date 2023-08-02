from fastapi import WebSocket


class MessageManager:
    async def validate_received_text(
        self, received_text: str, websocket: WebSocket, connections: dict
    ):
        lower_received_text = received_text.lower()
        if lower_received_text.startswith("a.") or lower_received_text.startswith(
            "action"
        ):
            await self.send_action(received_text, websocket, connections)

        elif lower_received_text.startswith("s.") or lower_received_text.startswith(
            "show"
        ):
            await self.show_connections(websocket=websocket, connections=connections)
        elif lower_received_text.startswith("c.") or lower_received_text.startswith(
            "channel"
        ):
            await self.change_channel(received_text, websocket, connections)
        elif lower_received_text.startswith("h.") or lower_received_text.startswith(
            "help"
        ):
            await self.help_cmd(websocket=websocket)
        else:
            await self.send_message(received_text, websocket, connections)

    async def send_text_to_user(self, text_to_send: str, websocket: WebSocket):
        await websocket.send_text(text_to_send)

    async def send_text_to_channel(
        self, text_to_send: str, websocket: WebSocket, connections: dict
    ):
        from_channel_name = connections.connections[websocket]["channel_name"]
        for connection in connections.connections:
            to_channel_name = connections.connections[connection]["channel_name"]
            if from_channel_name is to_channel_name and connection is not websocket:
                await connection.send_text(text_to_send)

    async def send_message(
        self, received_text: str, websocket: WebSocket, connections: dict
    ):
        await self.send_text_to_user(text_to_send=received_text, websocket=websocket)
        await self.send_text_to_channel(
            text_to_send=f"<{connections.connections[websocket]['user_name']}> {received_text}",
            websocket=websocket,
            connections=connections,
        )

    async def send_action(
        self, received_text: str, websocket: WebSocket, connections: dict
    ):
        text = f"-> {connections.connections[websocket]['user_name']} {received_text.split(' ', 1)[1]}"
        await self.send_text_to_user(text_to_send=text, websocket=websocket)
        await self.send_text_to_channel(
            text_to_send=text, websocket=websocket, connections=connections
        )

    async def change_channel(
        self, received_text: str, websocket: WebSocket, connections: dict
    ):
        channel_name = received_text.split()[1]
        await self.send_text_to_channel(
            text_to_send=f">> {connections.connections[websocket]['user_name']} leaves this channel",
            websocket=websocket,
            connections=connections,
        )
        connections.connections[websocket]["channel_name"] = channel_name
        await self.send_text_to_user(
            text_to_send=f">> Channel changed to {channel_name}", websockets=websocket
        )
        await self.send_text_to_channel(
            text_to_send=f">> {connections.connections[websocket]['user_name']} joined this channel",
            websocket=websocket,
            connections=connections,
        )

    async def show_connections(self, websocket: WebSocket, connections: dict):
        for connection in connections.connections:
            await self.send_text_to_user(
                text_to_send=f"{connections.connections[connection]['user_name']} @{connections.connections[connection]['channel_name']}",
                websocket=websocket,
            )

    async def help_cmd(self, websocket: WebSocket):
        help_text = [
            "a. or action <text> action something",
            "c. or channel <channel name> to change the channel",
            "s. or show to show who's online",
            "h. or help to show this help",
        ]
        for text in help_text:
            await self.send_text_to_user(text_to_send=text, websocket=websocket)

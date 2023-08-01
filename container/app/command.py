from fastapi import WebSocket
from connection import ConnectionManager


class CommandManager:
    async def search_for_command(
        self, received_text: str, websocket: WebSocket, connections: dict
    ):
        lower_received_text = received_text.lower()
        if lower_received_text.startswith("a.") or lower_received_text.startswith(
            "action"
        ):
            await self.action_cmd(received_text, websocket, connections)

        elif lower_received_text.startswith("s.") or lower_received_text.startswith(
            "show"
        ):
            await self.show_cmd(websocket, connections)
        elif lower_received_text.startswith("c.") or lower_received_text.startswith(
            "channel"
        ):
            await self.channel_cmd(received_text, websocket, connections)
        elif lower_received_text.startswith("h.") or lower_received_text.startswith(
            "help"
        ):
            await self.help_cmd(websocket, connections)
        else:
            await connections.send_to_user(received_text, websocket)
            await connections.send_to_channel(
                f"<{connections.connections[websocket]['user_name']}> {received_text}",
                websocket,
                connections,
            )

    async def action_cmd(
        self, received_text: str, websocket: WebSocket, connections: dict
    ):
        text = f"-> {connections.connections[websocket]['user_name']} {received_text.split(' ', 1)[1]}"
        await connections.send_to_user(text, websocket)
        await connections.send_to_channel(text, websocket, connections)

    async def channel_cmd(
        self, received_text: str, websocket: WebSocket, connections: dict
    ):
        channel_name = received_text.split()[1]
        await connections.send_to_channel(
            f">> {connections.connections[websocket]['user_name']} leaves this channel",
            websocket,
            connections,
        )
        connections.connections[websocket]["channel_name"] = channel_name
        await connections.send_to_user(
            f">> Channel changed to {channel_name}", websocket
        )
        await connections.send_to_channel(
            f">> {connections.connections[websocket]['user_name']} joined this channel",
            websocket,
            connections,
        )

    async def show_cmd(self, websocket: WebSocket, connections: dict):
        for connection in connections.connections:
            await connections.send_to_user(
                f"{connections.connections[connection]['user_name']} @{connections.connections[connection]['channel_name']}",
                websocket,
            )

    async def help_cmd(self, websocket: WebSocket, connections: dict):
        help_text = [
            "a. or action <text> action something",
            "c. or channel <channel name> to change the channel",
            "s. or show to show who's online",
            "h. or help to show this help",
        ]
        for text in help_text:
            await connections.send_to_user(text, websocket)

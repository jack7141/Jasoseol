import asyncio

from channels.generic.websocket import AsyncConsumer

class PingConsumer(AsyncConsumer):
    async def websocket_connect(self, message):
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, message):
        await self.send({
            "type": "websocket.send",
            "text": "pong",
        })
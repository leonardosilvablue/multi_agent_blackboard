import asyncio


class Blackboard:
    def __init__(self):
        self.messages = []
        self.lock = asyncio.Lock()

    async def post(self, sender, content, type_="discussion"):
        async with self.lock:
            self.messages.append({"sender": sender, "content": content, "type": type_})

    async def get_discussions(self):
        async with self.lock:
            return [msg for msg in self.messages if msg["type"] == "discussion"]

    async def get_actions(self):
        async with self.lock:
            return [msg for msg in self.messages if msg["type"] == "action"]

    async def get_all(self):
        async with self.lock:
            return list(self.messages)

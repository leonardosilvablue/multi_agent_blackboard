import asyncio
import logging
import uuid
import threading
from datetime import datetime

# Create a logger for the blackboard
blackboard_logger = logging.getLogger("blackboard.core")


class Blackboard:
    def __init__(self):
        self.messages = []
        self.lock = asyncio.Lock()
        self._thread_lock = threading.Lock()  # For synchronous access
        blackboard_logger.info("[BLACKBOARD_INIT] Blackboard initialized")

    async def post(self, sender, content, type_="discussion"):
        """Post a message to the blackboard asynchronously."""
        message_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()

        message = {
            "id": message_id,
            "sender": sender,
            "content": content,
            "type": type_,
            "timestamp": timestamp,
        }

        async with self.lock:
            self.messages.append(message)
            blackboard_logger.info(
                f"[BLACKBOARD_POST] [MessageID: {message_id}] New message posted from {sender}, type: {type_}"
            )
            blackboard_logger.debug(
                f"[BLACKBOARD_POST_CONTENT] [MessageID: {message_id}] Content: {content}"
            )

        return message_id

    def post_sync(self, sender, content, type_="discussion"):
        """Post a message to the blackboard synchronously (for use in function tools)."""
        message_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()

        message = {
            "id": message_id,
            "sender": sender,
            "content": content,
            "type": type_,
            "timestamp": timestamp,
        }

        with self._thread_lock:
            self.messages.append(message)
            blackboard_logger.info(
                f"[BLACKBOARD_POST_SYNC] [MessageID: {message_id}] New message posted from {sender}, type: {type_}"
            )
            blackboard_logger.debug(
                f"[BLACKBOARD_POST_SYNC_CONTENT] [MessageID: {message_id}] Content: {content[:100]}..."
            )

        return message_id

    async def get_discussions(self):
        """Get all discussion-type messages."""
        async with self.lock:
            discussions = [msg for msg in self.messages if msg["type"] == "discussion"]
            blackboard_logger.info(
                f"[BLACKBOARD_GET] Retrieved {len(discussions)} discussion messages"
            )
            return discussions

    async def get_actions(self):
        """Get all action-type messages."""
        async with self.lock:
            actions = [msg for msg in self.messages if msg["type"] == "action"]
            blackboard_logger.info(
                f"[BLACKBOARD_GET] Retrieved {len(actions)} action messages"
            )
            return actions

    async def get_all(self):
        """Get all messages from the blackboard."""
        async with self.lock:
            blackboard_logger.info(
                f"[BLACKBOARD_GET_ALL] Retrieved {len(self.messages)} total messages"
            )
            return list(self.messages)

    async def get_by_type(self, type_):
        """Get messages of a specific type."""
        async with self.lock:
            results = [msg for msg in self.messages if msg["type"] == type_]
            blackboard_logger.info(
                f"[BLACKBOARD_GET_TYPE] Retrieved {len(results)} messages of type '{type_}'"
            )
            return results

    async def get_by_sender(self, sender):
        """Get messages from a specific sender."""
        async with self.lock:
            results = [msg for msg in self.messages if msg["sender"] == sender]
            blackboard_logger.info(
                f"[BLACKBOARD_GET_SENDER] Retrieved {len(results)} messages from sender '{sender}'"
            )
            return results

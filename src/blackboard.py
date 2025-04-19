import asyncio
import logging
import uuid
import threading
import json
from datetime import datetime
from pathlib import Path

# Define the path for the blackboard data file
BLACKBOARD_DATA_FILE = Path("blackboard_data.json")


class Blackboard:
    def __init__(self):
        self.messages = []
        self.lock = asyncio.Lock()
        self._thread_lock = threading.Lock()  # For synchronous access
        self._load_messages()
        logging.info("[BLACKBOARD_INIT] Blackboard initialized")

    def _load_messages(self):
        """Load messages from the JSON file."""
        if BLACKBOARD_DATA_FILE.exists():
            try:
                with open(BLACKBOARD_DATA_FILE, "r") as f:
                    self.messages = json.load(f)
                logging.info(
                    f"[BLACKBOARD_LOAD] Loaded {len(self.messages)} messages from file"
                )
            except Exception as e:
                logging.error(f"[BLACKBOARD_LOAD_ERROR] Error loading messages: {e}")
                self.messages = []

    def _save_messages(self):
        """Save messages to the JSON file."""
        try:
            with open(BLACKBOARD_DATA_FILE, "w") as f:
                json.dump(self.messages, f)
            logging.info(
                f"[BLACKBOARD_SAVE] Saved {len(self.messages)} messages to file"
            )
        except Exception as e:
            logging.error(f"[BLACKBOARD_SAVE_ERROR] Error saving messages: {e}")

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
            self._save_messages()
            logging.info(
                f"[BLACKBOARD_POST] [MessageID: {message_id}] New message posted from {sender}, type: {type_}"
            )
            logging.debug(
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
            self._save_messages()
            logging.info(
                f"[BLACKBOARD_POST_SYNC] [MessageID: {message_id}] New message posted from {sender}, type: {type_}"
            )
            logging.debug(
                f"[BLACKBOARD_POST_SYNC_CONTENT] [MessageID: {message_id}] Content: {content}..."
            )

        return message_id

    async def get_discussions(self):
        """Get all discussion-type messages."""
        async with self.lock:
            discussions = [msg for msg in self.messages if msg["type"] == "discussion"]
            logging.info(
                f"[BLACKBOARD_GET] Retrieved {len(discussions)} discussion messages"
            )
            return discussions

    async def get_actions(self):
        """Get all action-type messages."""
        async with self.lock:
            actions = [msg for msg in self.messages if msg["type"] == "action"]
            logging.info(f"[BLACKBOARD_GET] Retrieved {len(actions)} action messages")
            return actions

    async def get_all(self):
        """Get all messages from the blackboard."""
        async with self.lock:
            logging.info(
                f"[BLACKBOARD_GET_ALL] Retrieved {len(self.messages)} total messages"
            )
            return list(self.messages)

    async def get_by_type(self, type_):
        """Get messages of a specific type."""
        async with self.lock:
            results = [msg for msg in self.messages if msg["type"] == type_]
            logging.info(
                f"[BLACKBOARD_GET_TYPE] Retrieved {len(results)} messages of type '{type_}'"
            )
            return results

    async def get_by_sender(self, sender):
        """Get messages from a specific sender."""
        async with self.lock:
            results = [msg for msg in self.messages if msg["sender"] == sender]
            logging.info(
                f"[BLACKBOARD_GET_SENDER] Retrieved {len(results)} messages from sender '{sender}'"
            )
            return results

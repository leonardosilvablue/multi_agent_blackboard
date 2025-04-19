import asyncio
import logging
import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional
from config.constants import BLACKBOARD_DATA_FILE


class Blackboard:
    def __init__(self):
        self.messages = []
        self.lock = asyncio.Lock()
        self._load_messages()
        logging.info("[BB] Initialized")

    def _load_messages(self):
        # Create file with empty array if it doesn't exist
        if not BLACKBOARD_DATA_FILE.exists():
            try:
                # Ensure the directory exists
                BLACKBOARD_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
                # Create an empty but valid JSON file
                with open(BLACKBOARD_DATA_FILE, "w") as f:
                    f.write("[]")
                logging.info("[BB] Created new empty blackboard file")
            except Exception as e:
                logging.error(f"[BB_ERROR] Failed to create blackboard file: {e}")
                self.messages = []
                return

        # Load the file
        try:
            with open(BLACKBOARD_DATA_FILE, "r") as f:
                file_content = f.read().strip()
                # Handle empty file
                if not file_content:
                    logging.warning(
                        "[BB] Empty file found, initializing with empty array"
                    )
                    self.messages = []
                    # Write a valid empty JSON array
                    with open(BLACKBOARD_DATA_FILE, "w") as f:
                        f.write("[]")
                    return

                # Parse JSON content
                data = json.loads(file_content)
                if isinstance(data, list):
                    self.messages = data
                else:
                    logging.warning("[BB] Invalid data format, initializing empty")
                    self.messages = []
                    # Fix the file
                    with open(BLACKBOARD_DATA_FILE, "w") as f:
                        f.write("[]")
            logging.info(f"[BB] Loaded {len(self.messages)} messages")
        except json.JSONDecodeError as e:
            logging.error(f"[BB_ERROR] Invalid JSON: {e}")
            logging.info("[BB] Resetting blackboard file with empty array")
            self.messages = []
            # Reset the file with valid JSON
            try:
                with open(BLACKBOARD_DATA_FILE, "w") as f:
                    f.write("[]")
            except Exception as write_err:
                logging.error(
                    f"[BB_ERROR] Failed to reset blackboard file: {write_err}"
                )
        except Exception as e:
            logging.error(f"[BB_ERROR] Error loading messages: {e}")
            self.messages = []

    def _save_messages(self):
        try:
            # Ensure the directory exists
            BLACKBOARD_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Write to a temporary file first
            temp_file = BLACKBOARD_DATA_FILE.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(self.messages, f, indent=2)

            # Only replace the original file if writing was successful
            temp_file.replace(BLACKBOARD_DATA_FILE)

            logging.debug(f"[BB] Saved {len(self.messages)} messages")
        except Exception as e:
            logging.error(f"[BB_ERROR] Error saving: {e}")
            # Don't clear messages on save error

    async def post(
        self,
        sender: str,
        content: str,
        type_: str = "discussion",
        department: Optional[str] = None,
        metadata: Optional[Dict] = None,
        reference_id: Optional[str] = None,
    ) -> str:
        message_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()

        message = {
            "id": message_id,
            "sender": sender,
            "content": content,
            "type": type_,
            "department": department,
            "timestamp": timestamp,
            "metadata": metadata or {},
        }

        # Add reference to original demand if provided
        if reference_id:
            message["reference_id"] = reference_id

        async with self.lock:
            self.messages.append(message)
            logging.debug(f"[BB] Messages count: {len(self.messages)}")
            self._save_messages()
            logging.info(
                f"[BB] Posted: id={message_id}, sender={sender}, type={type_}, dept={department}"
            )
            logging.debug(
                f"[BB] Content: {content[:50]}..."
                if len(content) > 50
                else f"[BB] Content: {content}"
            )

        return message_id

    async def get_demands(self, department: Optional[str] = None) -> List[Dict]:
        async with self.lock:
            # Recarregar mensagens do arquivo a cada verificação
            self._load_messages()
            logging.info("[BB] Reloaded messages from disk")

            # Log todos os tipos de mensagens para depuração
            message_types = [msg["type"] for msg in self.messages]
            logging.info(f"[BB] All message types: {message_types}")

            # Log para verificar se há mensagens de demanda e seu estado
            demand_msgs = [
                {"id": msg["id"], "processed": msg.get("processed", False)}
                for msg in self.messages
                if msg["type"] == "demand"
            ]
            logging.info(f"[BB] All demands (before filtering): {demand_msgs}")

            demands = [
                msg
                for msg in self.messages
                if msg["type"] == "demand"
                and not msg.get("processed", False)
                and (department is None or msg["department"] == department)
            ]
            if demands:
                logging.info(
                    f"[BB] Retrieved {len(demands)} demands"
                    + (f" for dept {department}" if department else "")
                )
            return demands

    async def mark_demand_processed(self, demand_id: str) -> bool:
        """Mark a demand as processed to prevent reprocessing"""
        async with self.lock:
            logging.info(f"[BB] Attempting to mark demand {demand_id} as processed")

            # Log do estado atual para depuração
            before_marking = [
                {"id": msg["id"], "processed": msg.get("processed", False)}
                for msg in self.messages
                if msg["type"] == "demand"
            ]
            logging.info(f"[BB] Demands before marking: {before_marking}")

            found = False
            for msg in self.messages:
                if msg["id"] == demand_id and msg["type"] == "demand":
                    msg["processed"] = True
                    found = True
                    logging.info(
                        f"[BB] Found and marked demand {demand_id} as processed"
                    )
                    break

            if found:
                # Salva imediatamente para persistir a alteração
                self._save_messages()

                # Log do estado após para confirmar a alteração
                after_marking = [
                    {"id": msg["id"], "processed": msg.get("processed", False)}
                    for msg in self.messages
                    if msg["type"] == "demand"
                ]
                logging.info(f"[BB] Demands after marking: {after_marking}")

                logging.info(f"[BB] Marked demand {demand_id} as processed")
                return True
            else:
                logging.warning(
                    f"[BB] Could not find demand {demand_id} to mark as processed"
                )
                return False

    async def get_latest_demands(self, limit: int = 3) -> List[Dict]:
        """Retorna as demandas mais recentes, ordenadas por data (mais recente primeiro)"""
        async with self.lock:
            # Primeiro recarregamos os dados do arquivo
            self._load_messages()

            # Filtramos as mensagens do tipo "demand"
            demands = [msg for msg in self.messages if msg["type"] == "demand"]

            # Ordenamos por timestamp (mais recente primeiro)
            demands.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            # Retornamos até o limite especificado
            return demands[:limit]

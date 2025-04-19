import asyncio
import logging
import json

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination

from blackboard import Blackboard
from ai_agents.ai_agents import head, squad_leader, worker


class DemandMonitor:
    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard
        self.running = True
        logging.info("[DEMAND] Monitor initialized")

    async def start(self):
        logging.info("[DEMAND] Starting monitor service")
        while self.running:
            try:
                await self._check_new_demands()
                await asyncio.sleep(5)
            except Exception as e:
                logging.error(f"[DEMAND_ERROR] Monitor error: {str(e)}")
                await asyncio.sleep(5)

    async def stop(self):
        self.running = False
        logging.info("[DEMAND] Stopping monitor service")

    async def _check_new_demands(self):
        try:
            demands = await self.blackboard.get_demands()

            if demands:
                logging.info(f"[DEMAND] Found demands: {[d['id'] for d in demands]}")

            for demand in demands:
                demand_id = demand["id"]
                logging.info(f"[DEMAND] Processing: {demand_id}")
                try:
                    await self._process_demand(demand)
                    # Mark in the blackboard
                    await self.blackboard.mark_demand_processed(demand_id)
                    logging.debug(f"[DEMAND] {demand_id}: Marked as processed")
                except Exception as e:
                    logging.error(
                        f"[DEMAND_ERROR] Failed to process {demand_id}: {str(e)}"
                    )
                    # Mark in the blackboard to avoid infinite retry loop
                    await self.blackboard.mark_demand_processed(demand_id)
                    logging.debug(
                        f"[DEMAND] {demand_id}: Marked failed demand as processed"
                    )
        except Exception as e:
            logging.error(f"[DEMAND_ERROR] Error checking for new demands: {str(e)}")

    async def _process_demand(self, demand):
        try:
            demand_content = str(demand["content"])
            demand_id = demand["id"]
            content_summary = (
                demand_content[:50] + "..."
                if len(demand_content) > 50
                else demand_content
            )
            logging.info(f"[DEMAND] Processing: {demand_id} - {content_summary}")

            # Process with head agent
            try:
                head_team = [head]
                head_chat = RoundRobinGroupChat(
                    head_team,
                    termination_condition=MaxMessageTermination(max_messages=10),
                )
                head_result = await head_chat.run(task=demand_content)

                if not head_result:
                    logging.warning(
                        f"[DEMAND] {demand_id}: Head agent returned empty result"
                    )
                    head_result = "No response from head agent"

                serialized_head_result = self._serialize_result(head_result)
                logging.info(f"[DEMAND] {demand_id}: Received head result")
            except Exception as e:
                logging.error(f"[DEMAND_ERROR] {demand_id}: Head agent error: {str(e)}")
                raise

            # Process with squad leader agent
            try:
                squad_team = [squad_leader]
                squad_chat = RoundRobinGroupChat(
                    squad_team,
                    termination_condition=MaxMessageTermination(max_messages=10),
                )
                squad_result = await squad_chat.run(task=serialized_head_result)

                if not squad_result:
                    logging.warning(
                        f"[DEMAND] {demand_id}: Squad leader returned empty result"
                    )
                    squad_result = "No response from squad leader"

                serialized_squad_result = self._serialize_result(squad_result)
                logging.info(f"[DEMAND] {demand_id}: Received squad result")
            except Exception as e:
                logging.error(
                    f"[DEMAND_ERROR] {demand_id}: Squad leader error: {str(e)}"
                )
                raise

            # Process with worker agent
            try:
                worker_team = [worker]
                worker_chat = RoundRobinGroupChat(
                    worker_team,
                    termination_condition=MaxMessageTermination(max_messages=10),
                )
                worker_result = await worker_chat.run(task=serialized_squad_result)

                if not worker_result:
                    logging.warning(
                        f"[DEMAND] {demand_id}: Worker returned empty result"
                    )
                    worker_result = "No response from worker"

                serialized_worker_result = self._serialize_result(worker_result)
                logging.info(f"[DEMAND] {demand_id}: Received worker result")
            except Exception as e:
                logging.error(f"[DEMAND_ERROR] {demand_id}: Worker error: {str(e)}")
                raise

            # Post result to blackboard with reference to original demand
            result_msg = await self.blackboard.post(
                "system",
                f"Demand {demand_id} completed. Results: {serialized_worker_result}",
                type_="result",
                department=demand.get("department"),
                reference_id=demand_id,  # Link the result to the demand
            )

            logging.info(
                f"[DEMAND] {demand_id}: Successfully processed with result {result_msg}"
            )

        except Exception as e:
            logging.error(f"[DEMAND_ERROR] {demand['id']}: {str(e)}")
            logging.debug("Exception details:", exc_info=True)
            await self.blackboard.post(
                "system",
                f"Error processing demand {demand['id']}: {str(e)}",
                type_="error",
                department=demand.get("department"),
                reference_id=demand["id"],  # Link error messages to the demand
            )
            raise

    def _serialize_result(self, result):
        """Safely serialize complex results to a string"""
        if result is None:
            return "No result provided"

        if isinstance(result, str):
            return result

        try:
            # Try to convert to string directly
            return str(result)
        except Exception:
            try:
                # Try JSON serialization
                return json.dumps(result)
            except Exception:
                # Fallback to simple representation
                return f"Complex result (type: {type(result).__name__})"

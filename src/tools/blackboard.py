from agents import function_tool
from blackboard import Blackboard
import logging
import uuid

blackboard = Blackboard()


@function_tool
def post_demand_to_blackboard(demand: str) -> str:
    """Post a demand to the blackboard using the synchronous post method."""
    demand_id = str(uuid.uuid4())[:8]

    logging.info(
        f"[TOOL_CALLED] [DemandID: {demand_id}] Director is posting demand to blackboard"
    )
    logging.info(f"[DEMAND_CONTENT] [DemandID: {demand_id}] Content: {demand}")

    try:
        message_id = blackboard.post_sync("director", demand, type_="demand")
        logging.info(
            f"[DEMAND_POSTED] [DemandID: {demand_id}] [MessageID: {message_id}] Successfully posted to blackboard"
        )
        return f"Demand posted to blackboard successfully with ID: {message_id}"
    except Exception as e:
        logging.error(
            f"[DEMAND_ERROR] [DemandID: {demand_id}] Error posting to blackboard: {str(e)}"
        )
        return f"Failed to post demand to blackboard: {str(e)}"

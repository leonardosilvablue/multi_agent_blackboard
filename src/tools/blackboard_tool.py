from autogen_core.tools import FunctionTool
import logging
import uuid

# Will be initialized later
blackboard = None


def set_blackboard(blackboard_instance):
    global blackboard
    blackboard = blackboard_instance


async def post_demand_to_blackboard(demand: str) -> str:
    """
    Post a demand to the blackboard system.

    Args:
        demand: The text content of the demand to post

    Returns:
        A string confirmation message with the demand ID
    """
    if blackboard is None:
        return "Error: Blackboard not initialized. Please set the blackboard instance first."

    demand_id = str(uuid.uuid4())[:8]

    logging.info(
        f"[TOOL_CALLED] [DemandID: {demand_id}] Director is posting demand to blackboard"
    )
    logging.info(f"[DEMAND_CONTENT] [DemandID: {demand_id}] Content: {demand}")

    # Tentar encontrar o departamento no texto da demanda
    department = None
    if "Departamento:" in demand:
        try:
            # Extrai o departamento após "Departamento:" até o próximo ponto ou fim da string
            dept_text = demand.split("Departamento:")[1].split(".")[0].strip()
            department = dept_text
            logging.info(
                f"[DEMAND_DEPT] [DemandID: {demand_id}] Extracted department: {department}"
            )
        except Exception as e:
            logging.warning(
                f"[DEMAND_WARNING] [DemandID: {demand_id}] Failed to extract department: {str(e)}"
            )

    try:
        message_id = await blackboard.post(
            "director", demand, type_="demand", department=department
        )
        logging.info(
            f"[DEMAND_POSTED] [DemandID: {demand_id}] [MessageID: {message_id}] Successfully posted to blackboard"
        )
        return f"Demand posted to blackboard successfully with ID: {message_id}"
    except Exception as e:
        logging.error(
            f"[DEMAND_ERROR] [DemandID: {demand_id}] Error posting to blackboard: {str(e)}"
        )
        return f"Failed to post demand to blackboard: {str(e)}"


# Create the tool instance
post_demand_tool = FunctionTool(
    name="post_demand_to_blackboard",
    description="Post a demand to the blackboard for processing. The tool takes a single argument: the demand text.",
    func=post_demand_to_blackboard,
)

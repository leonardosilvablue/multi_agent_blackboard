import asyncio
import logging
from typing import Optional, List, Dict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from main import process_with_boss, message_ids
from blackboard import Blackboard

# Create logger for API
api_logger = logging.getLogger("api.demands")

# Initialize router
router = APIRouter(prefix="/api/v1/demands", tags=["demands"])

# Initialize blackboard
blackboard = Blackboard()


class DemandRequest(BaseModel):
    """Request model for submitting a new demand."""

    demand: str
    priority: Optional[str] = "normal"
    department: Optional[str] = None


class ProcessingStep(BaseModel):
    """Model for a processing step in the demand lifecycle."""

    agent: str
    action: str
    timestamp: str
    status: str


class DemandResponse(BaseModel):
    """Response model for demand submission."""

    task_id: str
    message: str
    status: str
    processing_complete: bool = False
    processing_steps: Optional[List[ProcessingStep]] = None
    last_update: Optional[str] = None


async def get_processing_details(task_id: str) -> Dict:
    """
    Get detailed processing information for a demand.
    """
    messages = await blackboard.get_all()
    task_messages = [msg for msg in messages if task_id in str(msg.get("content", ""))]

    steps = []
    for msg in task_messages:
        # Convert known message types to processing steps
        if msg["type"] == "demand":
            steps.append(
                ProcessingStep(
                    agent="director",
                    action="posted_demand",
                    timestamp=msg["timestamp"],
                    status="complete",
                )
            )
        elif msg["type"] == "structured_plan":
            steps.append(
                ProcessingStep(
                    agent="head",
                    action="created_plan",
                    timestamp=msg["timestamp"],
                    status="complete",
                )
            )
        elif msg["type"] == "task_breakdown":
            steps.append(
                ProcessingStep(
                    agent="squad_leader",
                    action="broke_down_tasks",
                    timestamp=msg["timestamp"],
                    status="complete",
                )
            )
        elif msg["type"] == "demand_processed":
            steps.append(
                ProcessingStep(
                    agent="system",
                    action="completed_processing",
                    timestamp=msg["timestamp"],
                    status="complete",
                )
            )

    is_complete = any(msg["type"] == "demand_processed" for msg in task_messages)
    last_update = (
        max(msg["timestamp"] for msg in task_messages) if task_messages else None
    )

    return {"steps": steps, "is_complete": is_complete, "last_update": last_update}


async def wait_for_demand_completion(task_id: str, timeout: int = 60) -> Dict:
    """
    Wait for a demand to be fully processed.
    Returns processing details and completion status.
    """
    start_time = asyncio.get_event_loop().time()

    while (asyncio.get_event_loop().time() - start_time) < timeout:
        details = await get_processing_details(task_id)

        if details["is_complete"]:
            return details

        await asyncio.sleep(1)  # Check every second

    # If we timed out, return current state
    return await get_processing_details(task_id)


@router.post("", response_model=DemandResponse)
async def create_demand(
    request: DemandRequest,
    wait_complete: bool = Query(
        False, description="Whether to wait for complete processing before returning"
    ),
):
    """
    Submit a new demand to the system.

    The demand will be processed by the boss agent and delegated through the hierarchy.
    If wait_complete is True, will wait for full processing before returning.
    """
    try:
        api_logger.info(f"[API_REQUEST] Received new demand: {request.demand}")

        # Process the demand through the boss agent
        result = await process_with_boss(request.demand)

        # Get task_id from message_ids dictionary
        task_id = message_ids.get(request.demand, "unknown")

        api_logger.info(f"[API_SUCCESS] Processed demand with task ID: {task_id}")

        # Get processing details
        if wait_complete:
            api_logger.info(
                f"[API_WAITING] Waiting for complete processing of task {task_id}"
            )
            details = await wait_for_demand_completion(task_id)
            api_logger.info(
                f"[API_WAIT_COMPLETE] Task {task_id} processing {'completed' if details['is_complete'] else 'timed out'}"
            )
        else:
            details = await get_processing_details(task_id)

        return DemandResponse(
            task_id=task_id,
            message=result,
            status="success",
            processing_complete=details["is_complete"],
            processing_steps=details["steps"],
            last_update=details["last_update"],
        )

    except Exception as e:
        api_logger.error(
            f"[API_ERROR] Error processing demand: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Error processing demand: {str(e)}"
        )


@router.get("/{task_id}/status")
async def get_demand_status(task_id: str):
    """
    Get the status of a specific demand by its task ID.
    """
    try:
        # Get all messages from the blackboard
        messages = await blackboard.get_all()

        # Filter messages related to this task
        task_messages = [
            msg for msg in messages if task_id in str(msg.get("content", ""))
        ]

        if not task_messages:
            raise HTTPException(
                status_code=404, detail=f"No demand found with task ID: {task_id}"
            )

        # Determine the status
        status = (
            "completed"
            if any(msg["type"] == "demand_processed" for msg in task_messages)
            else "in_progress"
        )

        return {
            "task_id": task_id,
            "status": status,
            "message_count": len(task_messages),
            "latest_update": max(msg["timestamp"] for msg in task_messages),
        }

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"[API_ERROR] Error getting demand status: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Error retrieving demand status: {str(e)}"
        )

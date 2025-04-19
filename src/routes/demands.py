import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from main import DemandProcessor


router = APIRouter(prefix="/api/v1", tags=["demands"])


class DemandRequest(BaseModel):
    request: str


@router.post("/demands")
async def create_demand(demand: DemandRequest):
    try:
        processor = DemandProcessor()
        result = await processor.process_demand(demand.request)
        return result
    except Exception as e:
        logging.error(f"Error processing demand: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing demand: {str(e)}",
        )

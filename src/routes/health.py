from fastapi import APIRouter

# Initialize router
router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy", "version": "1.0.0"}

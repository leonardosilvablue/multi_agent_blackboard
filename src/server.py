import logging
import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from routes import demands, health
from config.settings import settings
from main import monitor_blackboard_for_demands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agent_system.log"),
    ],
)

logger = logging.getLogger("server")

# Load environment variables
load_dotenv()

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = settings.openai_api_key

# Background task for monitoring blackboard
monitor_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events for the FastAPI application.
    This will start the blackboard monitor when the app starts
    and clean it up when the app shuts down.
    """
    # Start up
    global monitor_task
    logger.info("[SERVER_STARTUP] Starting blackboard monitor...")
    monitor_task = asyncio.create_task(monitor_blackboard_for_demands())

    yield

    # Shutdown
    if monitor_task:
        logger.info("[SERVER_SHUTDOWN] Stopping blackboard monitor...")
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            logger.info("[SERVER_SHUTDOWN] Blackboard monitor stopped successfully")


# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Blackboard System API",
    description="API for interacting with the multi-agent blackboard system",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(demands.router)
app.include_router(health.router)


def main():
    """Run the FastAPI server."""
    logger.info("[SERVER_START] Starting Multi-Agent Blackboard System API server")

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()

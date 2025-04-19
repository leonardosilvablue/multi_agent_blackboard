import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from routes import demands
from config.settings import settings
from blackboard import Blackboard
from demand_monitor import DemandMonitor

import logging
from core.logger import setup_logging

load_dotenv()

os.environ["OPENAI_API_KEY"] = settings.openai_api_key

# Global instances
blackboard = None
demand_monitor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global blackboard, demand_monitor
    setup_logging()

    blackboard = Blackboard()
    demand_monitor = DemandMonitor(blackboard)
    asyncio.create_task(demand_monitor.start())

    yield

    if demand_monitor:
        await demand_monitor.stop()


app = FastAPI(lifespan=lifespan)

app.include_router(demands.router)


def main():
    logging.info("Starting server...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()

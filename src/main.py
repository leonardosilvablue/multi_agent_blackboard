import os
import asyncio
import logging

from config.settings import settings
from agents import Runner
from agents.boss import boss

os.environ["OPENAI_API_KEY"] = settings.openai_api_key

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


async def main():
    task = input("Enter a task: ")

    result = await Runner.run(boss, task, max_turns=50)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())

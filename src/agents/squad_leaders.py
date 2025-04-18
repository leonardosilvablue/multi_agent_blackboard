from agents import Agent
from agents.heads import head
from agents.workers import worker

dynamic_instructions = """
Você é um lider em uma empresa.
"""

squad_leader = Agent(
    name="squad_leader",
    instructions=dynamic_instructions,
    model="o3",
    handoff=[
        head,
    ],
    tools=[
        worker.as_tool(),
    ],
)

from agents import Agent
from agents.directors import director
from agents.squad_leaders import squad_leader

dynamic_instructions = """
Você é head de uma empresa.
"""

head = Agent(
    name="head",
    instructions=dynamic_instructions,
    model="o3",
    handoff=[
        director,
        squad_leader,
    ],
)

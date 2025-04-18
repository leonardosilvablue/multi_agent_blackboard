from agents import Agent
from agents.directors import director

dynamic_instructions = """
Você é um dono de uma empresa.
"""


boss = Agent(
    name="boss",
    instructions=dynamic_instructions,
    model="o3",
    handoff=[
        director,
    ],
)

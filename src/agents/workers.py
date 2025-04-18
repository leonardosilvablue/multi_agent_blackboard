from agents import Agent
from agents.squad_leaders import squad_leader


dynamic_instructions = """
Você é um trabalhador de uma empresa.
"""

worker = Agent(
    name="worker",
    instructions=dynamic_instructions,
    model="o3",
    handoff=[
        squad_leader,
    ],
)

from agents import Agent
from agents.boss import boss
from agents.heads import head

dynamic_instructions = """
Você é um diretor de uma empresa.
"""

director = Agent(
    name="director",
    instructions=dynamic_instructions,
    model="o3",
    handoff=[
        boss,
        head,
    ],
)

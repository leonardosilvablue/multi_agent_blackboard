from agents import Agent
from agents.extensions.visualization import draw_graph

boss = Agent(
    name="boss",
    instructions="Você é um dono de uma empresa.",
    model="o3",
    handoffs=[],
)
director = Agent(
    name="director",
    instructions="Você é um diretor de uma empresa.",
    model="o3-mini",
    handoffs=[],
)
head = Agent(
    name="head",
    instructions="Você é head de uma empresa.",
    model="gpt-4o",
    handoffs=[],
)
squad_leader = Agent(
    name="squad_leader",
    instructions="Você é um lider em uma empresa.",
    model="gpt-4o",
    handoffs=[],
    tools=[],
)
worker = Agent(
    name="worker",
    instructions="Você é um trabalhador de uma empresa.",
    model="gpt-4.1-nano",
    handoffs=[],
)

boss.handoffs = [director]
director.handoffs = [head]
head.handoffs = [squad_leader]
squad_leader.handoffs = [worker]

squad_leader.tools = [
    worker.as_tool(
        tool_name="worker_tool",
        tool_description="Executa tarefas como um trabalhador da empresa.",
    ),
]

__all__ = ["boss", "director", "head", "squad_leader", "worker"]

draw_graph(boss, "./agents_graph")

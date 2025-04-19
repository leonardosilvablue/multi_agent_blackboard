from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination

from blackboard import Blackboard
from ai_agents.ai_agents import (
    boss,
    director,
    head,
    worker,
    squad_leader,
)
from tools.blackboard_tool import set_blackboard


class DemandProcessor:
    def __init__(self):
        self.blackboard = Blackboard()
        set_blackboard(self.blackboard)
        self.agents = [boss, director, head, worker, squad_leader]

    async def process_demand(self, demand: str):
        executive_team = [boss, director]
        executive_team_chat = RoundRobinGroupChat(
            executive_team, termination_condition=MaxMessageTermination(max_messages=10)
        )
        await executive_team_chat.run(task=demand)

        latest_demands = await self.blackboard.get_latest_demands(limit=1)
        demand_info = latest_demands[0] if latest_demands else None

        return {
            "status": "success",
            "message": "Demand submitted successfully for processing",
            "demand": {
                "id": demand_info["id"] if demand_info else None,
                "content": demand_info["content"][:100] + "..."
                if demand_info and len(demand_info["content"]) > 100
                else demand_info["content"]
                if demand_info
                else None,
                "department": demand_info["department"] if demand_info else None,
                "timestamp": demand_info["timestamp"] if demand_info else None,
            }
            if demand_info
            else None,
        }

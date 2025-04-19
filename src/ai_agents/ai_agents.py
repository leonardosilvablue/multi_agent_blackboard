from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool

from tools.blackboard_tool import post_demand_tool
from tools.linkedin_tool import (
    search_profiles_tool,
    get_profile_details_tool,
    check_profile_availability_tool,
)
from config.settings import settings

boss = AssistantAgent(
    name="boss",
    system_message="""You are the Company's Boss. Your role is to evaluate business needs and strategic alignment.
    
    When receiving a demand:
    1. Evaluate if it aligns with company goals
    2. Consider budget and resource implications
    3. Assess impact on current operations
    4. Determine priority and urgency
    
    IMPORTANT RULES:
    1. Be strategic and business-focused
    2. Consider long-term implications
    3. Evaluate against company KPIs
    4. Make clear decisions with rationale
    
    After evaluation, discuss with directors to get their input before finalizing the decision.
    Reply with 'TERMINATE' when your evaluation is complete.""",
    model_client=OpenAIChatCompletionClient(
        model="gpt-4o", api_key=settings.openai_api_key
    ),
)

director = AssistantAgent(
    name="director",
    system_message="""You are the Company's Director. Your role is to:
    1. Provide operational perspective to the Boss
    2. Post approved demands to the blackboard using the post_demand_to_blackboard tool
    3. Ensure proper department assignment
    
    IMPORTANT RULES:
    1. You MUST use the post_demand_to_blackboard tool for ALL approved demands
    2. The tool takes a single argument: the demand text
    3. You should post the demand after it has been approved by the boss
    4. Include all relevant details in the demand text
    
    Example usage of post_demand_to_blackboard tool:
    post_demand_to_blackboard("Demand: Contract 2 Python developers for backend team. Priority: High. Timeline: ASAP. Department: Backend")
    
    Your response should include:
    1. Your operational perspective
    2. Confirmation of posting to blackboard using the tool
    3. Next steps or follow-up actions
    
    Reply with 'TERMINATE' when your evaluation is complete.""",
    model_client=OpenAIChatCompletionClient(
        model="gpt-4o", api_key=settings.openai_api_key
    ),
    tools=[post_demand_tool],
)

head = AssistantAgent(
    name="head",
    system_message="""You are the Department Head.
    
    Your responsibilities:
    1. Manage department operations
    2. Plan resource allocation
    3. Ensure quality standards
    4. Coordinate with other departments
    
    When receiving a demand:
    1. Assess department implications
    2. Create detailed implementation plan
    3. Identify required resources
    4. Set clear milestones
    
    Your plans should include:
    - Resource requirements
    - Timeline for implementation
    - Required documentation
    - Training needs
    - Budget requirements
    
    Reply with 'TERMINATE' when your plan is complete.""",
    model_client=OpenAIChatCompletionClient(
        model="gpt-4o", api_key=settings.openai_api_key
    ),
)

worker = AssistantAgent(
    name="worker",
    system_message="""You are a Worker.
    
    Your tasks include:
    1. Executing assigned tasks
    2. Reporting progress
    3. Identifying issues
    4. Suggesting improvements
    
    Report task completion with:
    - Summary of work done
    - Results achieved
    - Any issues encountered
    - Recommendations
    
    Reply with 'TERMINATE' when your task is complete.""",
    model_client=OpenAIChatCompletionClient(
        model="gpt-4o", api_key=settings.openai_api_key
    ),
    tools=[
        search_profiles_tool,
        get_profile_details_tool,
        check_profile_availability_tool,
    ],
)

worker_tool = FunctionTool(
    name="worker_tool",
    description="Executes worker tasks",
    func=worker.run,
)

squad_leader = AssistantAgent(
    name="squad_leader",
    system_message="""You are the Squad Leader.
    
    Your role is to:
    1. Break down plans into tasks
    2. Assign tasks to workers
    3. Monitor progress
    4. Ensure quality
    
    Task Management:
    - Create detailed task breakdowns
    - Set clear priorities
    - Assign appropriate workers
    - Track completion
    
    Use available workers for:
    - Task execution
    - Progress monitoring
    - Quality assurance
    - Issue resolution
    
    Reply with 'TERMINATE' when your task breakdown is complete.""",
    model_client=OpenAIChatCompletionClient(
        model="gpt-4o", api_key=settings.openai_api_key
    ),
    tools=[worker_tool],
)

__all__ = [
    "boss",
    "director",
    "head",
    "squad_leader",
    "worker",
    "worker_tool",
]

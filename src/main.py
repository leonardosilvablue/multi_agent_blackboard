import asyncio
import logging
import os
import uuid
from datetime import datetime

from agents import Runner

from ai_agents.ai_agents import boss, director, head, squad_leader, worker
from blackboard import Blackboard
from config.settings import settings
import tools.blackboard

blackboard = Blackboard()
tools.blackboard.blackboard = blackboard

os.environ["OPENAI_API_KEY"] = settings.openai_api_key

message_ids = {}


async def process_with_boss(task):
    """Process the initial task with the boss agent."""
    task_id = str(uuid.uuid4())[:8]
    logging.info(f"[FLOW_START] [TaskID: {task_id}] New task received: {task}")
    logging.info(f"[BOSS_START] [TaskID: {task_id}] Boss processing task: {task}")

    start_time = datetime.now()
    result = await Runner.run(boss, task, max_turns=50)
    end_time = datetime.now()

    processing_time = (end_time - start_time).total_seconds()
    logging.info(
        f"[BOSS_COMPLETE] [TaskID: {task_id}] Boss completed processing in {processing_time:.2f} seconds"
    )
    logging.info(f"[BOSS_OUTPUT] [TaskID: {task_id}] Output: {result.final_output}")

    if hasattr(result, "handoff_details") and result.handoff_details:
        agent_name = result.handoff_details.get("agent_name", "unknown")
        logging.info(f"[HANDOFF] [TaskID: {task_id}] Boss handed off to {agent_name}")

        if agent_name == "director":
            logging.info(
                f"[DIRECTOR_START] [TaskID: {task_id}] Director receiving handoff from boss"
            )
            handoff_message = result.handoff_details.get("message", task)
            director_start_time = datetime.now()
            director_result = await Runner.run(director, handoff_message, max_turns=50)
            director_end_time = datetime.now()

            director_processing_time = (
                director_end_time - director_start_time
            ).total_seconds()
            logging.info(
                f"[DIRECTOR_COMPLETE] [TaskID: {task_id}] Director completed processing in {director_processing_time:.2f} seconds"
            )
            logging.info(
                f"[DIRECTOR_OUTPUT] [TaskID: {task_id}] Output: {director_result.final_output}"
            )

            result.final_output += (
                f"\n\nDirector's response: {director_result.final_output}"
            )

    message_ids[task] = task_id
    return result.final_output


async def monitor_blackboard_for_demands():
    """Monitor the blackboard for new demands and trigger head agents to discuss."""
    logging.info("[MONITOR_START] Starting to monitor blackboard for demands...")

    while True:
        all_messages = await blackboard.get_all()
        logging.debug(
            f"[BLACKBOARD_CHECK] Checking blackboard. Found {len(all_messages)} messages."
        )

        demands = [msg for msg in all_messages if msg["type"] == "demand"]

        if demands:
            logging.info(
                f"[DEMANDS_FOUND] Found {len(demands)} demand(s) on blackboard."
            )
            for demand in demands:
                demand_id = str(uuid.uuid4())[:8]
                demand_content = demand["content"]
                logging.info(
                    f"[DEMAND_PROCESSING] [DemandID: {demand_id}] Processing demand: {demand_content[:50]}..."
                )

                await heads_discussion(demand_content, demand_id)

                for msg in all_messages:
                    if msg == demand:
                        old_type = msg["type"]
                        msg["type"] = "demand_processed"
                        logging.info(
                            f"[DEMAND_MARKED] [DemandID: {demand_id}] Changed type from '{old_type}' to 'demand_processed'"
                        )
                        await blackboard.post(
                            sender="system",
                            content=f"Demand {demand_id} marked as processed: {demand_content[:30]}...",
                            type_="system_log",
                        )

        await asyncio.sleep(5)


async def heads_discussion(demand_content, demand_id):
    """Use the head agent to discuss and structure the demand."""
    logging.info(
        f"[HEAD_START] [DemandID: {demand_id}] Head starting to process demand"
    )

    discussion_prompt = f"""
    As a company head, analyze this demand thoroughly:
    
    DEMAND: {demand_content}
    
    First, think about different perspectives on this demand.
    Then, create a structured plan with the following:
    1. Clear understanding of what is being requested
    2. Key considerations and potential challenges
    3. Resources needed
    4. Timeline for implementation
    5. Action items for different teams
    
    Present your complete analysis and structured plan.
    """

    logging.info(
        f"[HEAD_THINKING] [DemandID: {demand_id}] Head is analyzing the demand"
    )
    start_time = datetime.now()

    result = await Runner.run(head, discussion_prompt, max_turns=20)
    structured_plan = result.final_output

    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    logging.info(
        f"[HEAD_COMPLETE] [DemandID: {demand_id}] Head finished analysis in {processing_time:.2f} seconds"
    )

    plan_id = str(uuid.uuid4())[:8]
    await blackboard.post(
        sender="head", content=structured_plan, type_="structured_plan"
    )

    logging.info(
        f"[PLAN_POSTED] [DemandID: {demand_id}] [PlanID: {plan_id}] Head posted structured plan to blackboard"
    )
    logging.info(f"[PLAN_SUMMARY] [PlanID: {plan_id}] Plan summary: {structured_plan}")

    logging.info(
        f"[PLAN_READY] [PlanID: {plan_id}] Plan is ready for squad leaders to implement"
    )

    await process_with_squad_leader(structured_plan, plan_id, demand_id)

    return structured_plan


async def process_with_squad_leader(plan, plan_id, demand_id):
    """Process the structured plan with the squad leader."""
    logging.info(
        f"[SQUAD_LEADER_START] [PlanID: {plan_id}] Squad leader processing plan"
    )

    breakdown_prompt = f"""
    As a squad leader, you have received this implementation plan:
    
    {plan}
    
    Your task is to break this down into specific, actionable tasks that can be assigned to workers.
    For each task, include:
    1. Task description
    2. Priority (High/Medium/Low)
    3. Required skills
    4. Estimated time to complete
    5. Dependencies (if any)
    
    Organize these tasks into a clear, structured breakdown.
    """

    start_time = datetime.now()
    result = await Runner.run(squad_leader, breakdown_prompt, max_turns=20)
    task_breakdown = result.final_output
    end_time = datetime.now()

    processing_time = (end_time - start_time).total_seconds()
    logging.info(
        f"[SQUAD_LEADER_COMPLETE] [PlanID: {plan_id}] Completed in {processing_time:.2f} seconds"
    )

    message_id = await blackboard.post(
        sender="squad_leader", content=task_breakdown, type_="task_breakdown"
    )

    logging.info(
        f"[TASKS_POSTED] [PlanID: {plan_id}] [MessageID: {message_id}] Tasks posted to blackboard"
    )
    logging.info(f"[TASKS_SUMMARY] [PlanID: {plan_id}] Summary: {task_breakdown}")

    task_lines = task_breakdown.split("\n")
    high_priority_tasks = [
        line
        for line in task_lines
        if "Priority: High" in line or "Priority:High" in line
    ]

    if high_priority_tasks:
        task_description = high_priority_tasks[0]
        task_id = str(uuid.uuid4())[:8]

        await process_with_worker(task_description, task_id, plan_id)

    return task_breakdown


async def process_with_worker(task, task_id, plan_id):
    """Assign a task to a worker and get execution results."""
    logging.info(
        f"[WORKER_START] [TaskID: {task_id}] Worker processing task from plan {plan_id}"
    )

    execution_prompt = f"""
    You have been assigned the following task:
    
    {task}
    
    Please execute this task and provide:
    1. A detailed execution report
    2. Any challenges encountered
    3. Status (Complete/In Progress/Blocked)
    4. Next steps or recommendations
    """

    start_time = datetime.now()
    result = await Runner.run(worker, execution_prompt, max_turns=15)
    execution_result = result.final_output
    end_time = datetime.now()

    processing_time = (end_time - start_time).total_seconds()
    logging.info(
        f"[WORKER_COMPLETE] [TaskID: {task_id}] Completed in {processing_time:.2f} seconds"
    )

    message_id = await blackboard.post(
        sender="worker", content=execution_result, type_="task_execution"
    )

    logging.info(
        f"[EXECUTION_POSTED] [TaskID: {task_id}] [MessageID: {message_id}] Result posted to blackboard"
    )
    logging.info(f"[EXECUTION_SUMMARY] [TaskID: {task_id}] Summary: {execution_result}")

    return execution_result


async def view_blackboard():
    """Display the current blackboard messages in a readable format."""
    messages = await blackboard.get_all()
    print("\n=== BLACKBOARD CONTENTS ===")
    print(f"Total messages: {len(messages)}\n")

    for msg in messages:
        print(f"Message ID: {msg['id']}")
        print(f"Type: {msg['type']}")
        print(f"Sender: {msg['sender']}")
        print(f"Timestamp: {msg['timestamp']}")
        print("Content:")
        print(f"{msg['content']}")
        print("-" * 50)
    print("===========================\n")


async def get_process_status(task_id):
    """Get the status of a specific task process."""
    all_messages = await blackboard.get_all()
    task_messages = [
        msg for msg in all_messages if task_id in str(msg.get("content", ""))
    ]
    return {
        "task_id": task_id,
        "total_messages": len(task_messages),
        "status": "completed"
        if any(msg["type"] == "demand_processed" for msg in task_messages)
        else "in_progress",
    }


async def main():
    logging.info("[SYSTEM_START] Multi-agent blackboard system starting up")

    for agent_name in ["squad_leader", "worker"]:
        if not logging.getLogger(agent_name).handlers:
            agent_logger = logging.getLogger(agent_name)
            agent_logger.setLevel(logging.INFO)
            for handler in logging.getLogger().handlers:
                agent_logger.addHandler(handler)

    logging.info("[MONITOR_LAUNCH] Starting blackboard monitoring service")
    blackboard_monitor = asyncio.create_task(monitor_blackboard_for_demands())

    try:
        task = input("Enter a task: ")
        logging.info(f"[TASK_RECEIVED] User entered task: {task}")

        await process_with_boss(task)

        logging.info(
            "[SYSTEM_RUNNING] System is now running and monitoring the blackboard (interactive CLI disabled)"
        )

        heartbeat_counter = 0
        while True:
            heartbeat_counter += 1
            logging.info(
                f"[HEARTBEAT] System running for {heartbeat_counter} minute(s)"
            )
            await asyncio.sleep(60)

    except KeyboardInterrupt:
        logging.info("[SHUTDOWN_INITIATED] User initiated shutdown")
        blackboard_monitor.cancel()
        try:
            await blackboard_monitor
        except asyncio.CancelledError:
            logging.info("[MONITOR_STOPPED] Blackboard monitor has been cancelled")
    except Exception as e:
        logging.error(f"[ERROR] Unexpected error occurred: {str(e)}", exc_info=True)
    finally:
        logging.info("[SYSTEM_SHUTDOWN] System shutting down")


if __name__ == "__main__":
    asyncio.run(main())

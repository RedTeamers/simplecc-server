from fastapi import APIRouter
from simplec2.models.models import TaskRequest
from simplec2.routes.agents import agents

router = APIRouter()

@router.post("/")
def add_task(task: TaskRequest):
    if task.agent_id in agents:
        agents[task.agent_id]["tasks"].append(task.command)
        return {"status": "added"}
    return {"error": "invalid agent"}

@router.get("/{agent_id}")
def get_tasks(agent_id: str):
    return agents.get(agent_id, {}).get("tasks", [])
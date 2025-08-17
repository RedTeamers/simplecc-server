from fastapi import APIRouter
from simplec2.models.models import AgentRegister

router = APIRouter()

agents = {}

@router.post("/register")
def register(agent: AgentRegister):
    agent_id = agent.agent_id  # on garde l'ID fourni
    agents[agent_id] = {"info": agent.dict(), "tasks": [], "results": [], "status": "new"}
    return {"id": agent_id}

@router.get("/list")
def list_agents():
    return agents
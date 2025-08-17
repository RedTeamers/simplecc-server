from fastapi import APIRouter
from simplec2.models.models import ResultSubmit
from simplec2.routes.agents import agents

router = APIRouter()

@router.post("/")
def submit_result(result: ResultSubmit):
    if result.agent_id in agents:
        agents[result.agent_id]["results"].append(result.output)
        agents[result.agent_id]["tasks"] = []  # clear tasks
        return {"status": "received"}
    return {"error": "unknown agent"}

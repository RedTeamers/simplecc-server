from fastapi import APIRouter
from simplec2.models.models import Beacon
from simplec2.routes.agents import agents

router = APIRouter()

@router.post("/")
def post_beacon(beacon: Beacon):
    if beacon.agent_id in agents:
        agents[beacon.agent_id]["status"] = beacon.status
        return {"tasking": agents[beacon.agent_id]["tasks"]}
    return {"error": "unknown agent"}

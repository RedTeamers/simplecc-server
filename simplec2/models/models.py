from pydantic import BaseModel
from typing import Optional, List

class TaskRequest(BaseModel):
    agent_id: str
    command: str

class ResultSubmit(BaseModel):
    agent_id: str
    output: str

class Beacon(BaseModel):
    agent_id: str
    status: Optional[str] = "idle"

class AgentRegister(BaseModel):
    agent_id: str
    hostname: str
    os: str
    ip: str


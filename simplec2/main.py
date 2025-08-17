from fastapi import FastAPI
from simplec2.routes import agents, task, beacon, result

app = FastAPI()

app.include_router(agents.router, prefix="/agent")
app.include_router(task.router, prefix="/task")
app.include_router(beacon.router, prefix="/beacon")
app.include_router(result.router, prefix="/result")
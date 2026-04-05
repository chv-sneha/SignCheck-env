from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
from .models import ResetRequest, StepRequest, StepResponse, Observation, Action
from .env import SignCheckEnv
from .grader import Grader

app = FastAPI(title="SignCheck-env")
env = SignCheckEnv()
grader = Grader()

@app.get("/tasks")
def get_tasks():
    import yaml
    with open("openenv.yaml", "r") as f:
        config = yaml.safe_load(f)
    return {"tasks": config.get("tasks", [])}

@app.post("/reset", response_model=Observation)
def reset_env(req: ResetRequest):
    try:
        obs = env.reset(req.task_id)
        return obs
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step", response_model=StepResponse)
def step_env(req: StepRequest):
    if env.scenario is None:
        raise HTTPException(status_code=400, detail="Environment not reset.")
    
    response = env.step(req.action)
    
    # If done, we can optionally grade it and attach to info
    if response.done:
        score = grader.grade(
            history=env.history,
            total_reward=env.total_reward,
            info=response.info,
            max_steps=env.scenario["max_steps"]
        )
        response.info["final_score"] = score
        response.info["total_reward"] = env.total_reward
        
    return response

@app.get("/state", response_model=Observation)
def get_state():
    if env.scenario is None:
        raise HTTPException(status_code=400, detail="Environment not reset.")
    return env.state()

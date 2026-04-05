import os
import time
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# We configure to talk to the local FastAPI Environment
ENV_URL = "http://localhost:7860"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy"), base_url=API_BASE_URL)

def run_task(task_id: int):
    print(f"[START] Task {task_id}")
    
    # Reset Environment
    res = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    if res.status_code != 200:
        print(f"Failed to reset environment: {res.text}")
        return
        
    obs = res.json()
    done = False
    
    # Simple prompt describing the options
    system_prompt = """You are an AI first-responder agent monitoring an ICU patient.
You will receive JSON observations.
Select strictly one Action from the following list to stabilize or escalate:
SOUND_WARD_ALARM, CALL_ATTENDING_DOCTOR, CALL_ICU_SPECIALIST, CALL_CODE_BLUE, CHECK_EQUIPMENT, CHECK_PATIENT_AIRWAY, REPOSITION_PATIENT, START_MANUAL_BAGGING, ADJUST_OXYGEN_FLOW, SILENCE_ALARM, CHECK_IV_LINE, ADMINISTER_EMERGENCY_MED, WAIT_AND_MONITOR.
Output only the action name."""

    messages = [{"role": "system", "content": system_prompt}]
    
    while not done:
        obs_str = str(obs)
        messages.append({"role": "user", "content": obs_str})
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=10,
                temperature=0.0
            )
            action = response.choices[0].message.content.strip()
            
            # Extract just the action if model becomes chatty
            valid_actions = ["SOUND_WARD_ALARM", "CALL_ATTENDING_DOCTOR", "CALL_ICU_SPECIALIST", "CALL_CODE_BLUE", "CHECK_EQUIPMENT", "CHECK_PATIENT_AIRWAY", "REPOSITION_PATIENT", "START_MANUAL_BAGGING", "ADJUST_OXYGEN_FLOW", "SILENCE_ALARM", "CHECK_IV_LINE", "ADMINISTER_EMERGENCY_MED", "WAIT_AND_MONITOR"]
            
            selected_action = "WAIT_AND_MONITOR"
            for va in valid_actions:
                if va in action:
                    selected_action = va
                    break
            
            print(f"[STEP] Action: {selected_action}")
            messages.append({"role": "assistant", "content": selected_action})
            
            step_res = requests.post(f"{ENV_URL}/step", json={"action": selected_action})
            if step_res.status_code != 200:
                print(f"Error stepping environment: {step_res.text}")
                break
                
            step_data = step_res.json()
            obs = step_data["observation"]
            reward = step_data["reward"]
            done = step_data["done"]
            info = step_data["info"]
            
            print(f"       Reward: {reward['reward']} | Msg: {reward['message']}")
            
            if done:
                print(f"[END] Task {task_id} finished. Final Info: {info}")
                
        except Exception as e:
            print(f"Inference error: {e}")
            break

def main():
    # Wait for the server to be up
    for _ in range(10):
        try:
            requests.get(f"{ENV_URL}/tasks")
            break
        except:
            time.sleep(1)
            
    tasks_res = requests.get(f"{ENV_URL}/tasks")
    if tasks_res.status_code == 200:
        tasks = tasks_res.json().get("tasks", [])
        for task in tasks:
            run_task(task["task_id"])
    else:
        print("Failed to get tasks.")

if __name__ == "__main__":
    main()

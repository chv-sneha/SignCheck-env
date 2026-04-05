from typing import Dict, Any

class Grader:
    def __init__(self):
        pass
    
    def grade(self, history: list, total_reward: float, info: Dict[str, Any], max_steps: int) -> float:
        # survival 40%, vital stability 30%, escalation quality 20%, step efficiency 10%
        score = 0.0
        
        status = info.get("episode_status", "")
        
        # Survival (40%)
        if status == "success_doctor_arrival":
            score += 0.4
            
        # Vital stability (30%)
        cr_vitals = info.get("critical_vitals", 0)
        if cr_vitals == 0:
            score += 0.3
        elif cr_vitals == 1:
            score += 0.15
        
        # Escalation quality (20%)
        escalation_actions = ["CALL_ATTENDING_DOCTOR", "CALL_ICU_SPECIALIST", "CALL_CODE_BLUE"]
        escalation_count = sum(1 for action in history if action in escalation_actions)
        if status == "success_doctor_arrival" and escalation_count == 1:
            score += 0.2
        elif escalation_count > 1:
            score += 0.1 # Spamming escalation reduces quality
            
        # Step efficiency (10%)
        step_count = info.get("step_count", max_steps)
        if step_count < max_steps * 0.5:
            score += 0.1
        elif step_count < max_steps * 0.8:
            score += 0.05
            
        return round(min(1.0, max(0.0, score)), 2)

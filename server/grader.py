from pydantic import BaseModel
from typing import List, Dict, Any
from .models import Action, PatientOutcome
from .vitals import compute_stability_score, VitalSigns

class GradeResult(BaseModel):
    final_score: float
    survival_score: float
    stability_score: float
    escalation_score: float
    efficiency_score: float
    passed: bool

def grade_episode(
    task_id: int, 
    action_history: List[Action], 
    vital_log: List[VitalSigns], 
    outcome: PatientOutcome, 
    step_count: int, 
    max_steps: int
) -> GradeResult:
    # 1. Survival Score (0.4 weight)
    if outcome == PatientOutcome.SAVED:
        survival_score = 1.0
    elif outcome in [PatientOutcome.STABLE, PatientOutcome.DETERIORATING]:
        survival_score = 0.5
    else: # DECEASED or CRITICAL
        survival_score = 0.0
        
    # 2. Stability Score (0.3 weight)
    if vital_log:
        scores = [compute_stability_score(v) for v in vital_log]
        stability_score = sum(scores) / len(scores)
    else:
        stability_score = 0.0
        
    # 3. Escalation Score (0.2 weight)
    escalation_score = 0.0
    if task_id == 1:
        if Action.CALL_ATTENDING_DOCTOR in action_history:
            escalation_score = 1.0
    elif task_id == 2:
        if Action.CALL_ICU_SPECIALIST in action_history:
            escalation_score = 1.0
    elif task_id == 3:
        if Action.CALL_CODE_BLUE in action_history:
            idx = action_history.index(Action.CALL_CODE_BLUE)
            if idx < 4:
                escalation_score = 1.0
            else:
                escalation_score = 0.5
        elif Action.CALL_ATTENDING_DOCTOR in action_history:
            escalation_score = 0.1
                
    # 4. Efficiency Score (0.1 weight)
    efficiency_score = max(0.0, min(1.0, 1.0 - (step_count / max_steps)))
    
    # Final Score Compilation
    final_score = (
        (survival_score * 0.4) +
        (stability_score * 0.3) +
        (escalation_score * 0.2) +
        (efficiency_score * 0.1)
    )
    final_score = max(0.0, min(1.0, final_score))
    
    return GradeResult(
        final_score=round(final_score, 3),
        survival_score=round(survival_score, 3),
        stability_score=round(stability_score, 3),
        escalation_score=round(escalation_score, 3),
        efficiency_score=round(efficiency_score, 3),
        passed=(final_score >= 0.6)
    )

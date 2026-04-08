from enum import Enum
from pydantic import BaseModel
from typing import Dict, Optional, Any

class Action(str, Enum):
    SOUND_WARD_ALARM = "SOUND_WARD_ALARM"
    CALL_ATTENDING_DOCTOR = "CALL_ATTENDING_DOCTOR"
    CALL_ICU_SPECIALIST = "CALL_ICU_SPECIALIST"
    CALL_CODE_BLUE = "CALL_CODE_BLUE"
    CHECK_EQUIPMENT = "CHECK_EQUIPMENT"
    CHECK_PATIENT_AIRWAY = "CHECK_PATIENT_AIRWAY"
    REPOSITION_PATIENT = "REPOSITION_PATIENT"
    START_MANUAL_BAGGING = "START_MANUAL_BAGGING"
    ADJUST_OXYGEN_FLOW = "ADJUST_OXYGEN_FLOW"
    SILENCE_ALARM = "SILENCE_ALARM"
    CHECK_IV_LINE = "CHECK_IV_LINE"
    ADMINISTER_EMERGENCY_MED = "ADMINISTER_EMERGENCY_MED"
    WAIT_AND_MONITOR = "WAIT_AND_MONITOR"

class PatientOutcome(str, Enum):
    STABLE = "stable"
    DETERIORATING = "deteriorating"  
    CRITICAL = "critical"
    DECEASED = "deceased"
    SAVED = "saved"

class Observation(BaseModel):
    spo2: float
    heart_rate: int
    bp_systolic: int
    bp_diastolic: int
    resp_rate: int
    temperature: float
    consciousness: str  # AVPU scale
    equipment_status: dict
    power_status: str
    time_elapsed: int
    time_since_last_vitals_check: int
    doctor_eta: Optional[int] = None
    clinical_notes: str
    last_action_feedback: str
    step_count: int
    patient_outcome: PatientOutcome = PatientOutcome.STABLE

class Reward(BaseModel):
    reward: float
    message: str

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict

    model_config = {
        "json_schema_extra": {
            "example": {
                "observation": {
                    "spo2": 95.0,
                    "heart_rate": 85,
                    "bp_systolic": 120,
                    "bp_diastolic": 80,
                    "resp_rate": 18,
                    "temperature": 37.0,
                    "consciousness": "Alert",
                    "equipment_status": {"ventilator": "OK", "power": "OK"},
                    "power_status": "Normal",
                    "time_elapsed": 10,
                    "time_since_last_vitals_check": 0,
                    "doctor_eta": 15,
                    "clinical_notes": "Patient stable following medication.",
                    "last_action_feedback": "Administered O2, SpO2 improving.",
                    "step_count": 1,
                    "patient_outcome": "stable"
                },
                "reward": 1.0,
                "done": False,
                "info": {"outcome": "Ongoing"}
            }
        }
    }

class ResetResult(BaseModel):
    observation: Observation
    task_id: int
    task_description: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "observation": {
                    "spo2": 98.0,
                    "heart_rate": 72,
                    "bp_systolic": 118,
                    "bp_diastolic": 76,
                    "resp_rate": 16,
                    "temperature": 36.8,
                    "consciousness": "Alert",
                    "equipment_status": {"ventilator": "OK", "power": "OK"},
                    "power_status": "Normal",
                    "time_elapsed": 0,
                    "time_since_last_vitals_check": 0,
                    "doctor_eta": None,
                    "clinical_notes": "Initial patient assessment complete.",
                    "last_action_feedback": "None",
                    "step_count": 0,
                    "patient_outcome": "stable"
                },
                "task_id": 1,
                "task_description": "Task 1: Power Failure simulation."
            }
        }
    }

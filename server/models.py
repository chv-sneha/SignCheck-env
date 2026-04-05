from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any

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

class Observation(BaseModel):
    spo2: float
    heart_rate: float
    blood_pressure_systolic: float
    blood_pressure_diastolic: float
    respiratory_rate: float
    temperature: float
    avpu: str  # 'Alert', 'Verbal', 'Pain', 'Unresponsive'
    alarms_active: bool
    equipment_status: str
    patient_status_notes: str

class Reward(BaseModel):
    reward: float
    message: str

class StepResponse(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: Dict[str, Any]

class ResetRequest(BaseModel):
    task_id: int

class StepRequest(BaseModel):
    action: Action

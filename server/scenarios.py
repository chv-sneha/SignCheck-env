from typing import Dict, Any

def get_scenario(task_id: int) -> Dict[str, Any]:
    if task_id == 1:
        # Power failure, slow degradation
        return {
            "name": "Power failure",
            "initial_state": {
                "equipment_status": "ON_BATTERY",
                "patient_status_notes": "Stable but power to ward lost, using backup battery.",
                "avpu": "Alert",
                "alarms_active": True
            },
            "drifts": {
                "spo2": -0.2, # slow drop over 25 steps = ~5% drop
                "heart_rate": 0.5,
                "bp_sys": -1.0,
                "bp_dia": -0.5,
                "respiratory_rate": 0.2
            },
            "max_steps": 30, # Max total steps allowed as per specification
            "solution": ["SOUND_WARD_ALARM", "CHECK_EQUIPMENT", "ADJUST_OXYGEN_FLOW", "CALL_ATTENDING_DOCTOR", "WAIT_AND_MONITOR"]
        }
    elif task_id == 2:
        # Ventilator malfunction, distinguish equipment false
        return {
            "name": "Ventilator equipment malfunction",
            "initial_state": {
                "equipment_status": "FAULT_DETECTED",
                "patient_status_notes": "Ventilator reporting low pressure. Patient looks anxious.",
                "avpu": "Alert",
                "alarms_active": True
            },
            "drifts": {
                "spo2": -0.8,
                "heart_rate": 1.5,
                "bp_sys": 1.0,
                "bp_dia": 0.5,
                "respiratory_rate": 1.0
            },
            "max_steps": 30,
            "solution": ["CHECK_EQUIPMENT", "CHECK_PATIENT_AIRWAY", "START_MANUAL_BAGGING", "CALL_ICU_SPECIALIST"]
        }
    elif task_id == 3:
        # Sudden cardiac event, hard, 8 steps
        return {
            "name": "Sudden cardiac event",
            "initial_state": {
                "equipment_status": "NORMAL",
                "patient_status_notes": "Patient suddenly clutching chest, erratic ECG rhythm.",
                "avpu": "Pain", # degrading to unresponsive
                "alarms_active": True
            },
            "drifts": {
                "spo2": -1.5,
                "heart_rate": 5.0, # tachycardia leading to VTach
                "bp_sys": -5.0, # rapid drop
                "bp_dia": -3.0,
                "respiratory_rate": 2.0
            },
            "max_steps": 30,
            "solution": ["CALL_CODE_BLUE", "ADMINISTER_EMERGENCY_MED", "START_MANUAL_BAGGING", "CALL_ICU_SPECIALIST"]
        }
    else:
        raise ValueError("Invalid task ID")

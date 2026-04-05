from .models import Action, Observation, Reward, StepResponse
from .vitals import VitalsSim
from .scenarios import get_scenario

class SignCheckEnv:
    def __init__(self):
        self.task_id = 1
        self.scenario = None
        self.vitals = None
        self.step_count = 0
        self.history = []
        self.is_done = False
        self.total_reward = 0.0

    def reset(self, task_id: int):
        self.task_id = task_id
        self.scenario = get_scenario(task_id)
        self.vitals = VitalsSim()
        # Apply initial state
        initial = self.scenario["initial_state"]
        self.vitals.avpu = initial.get("avpu", "Alert")
        self.equipment_status = initial.get("equipment_status", "NORMAL")
        self.alarms_active = initial.get("alarms_active", False)
        self.patient_notes = initial.get("patient_status_notes", "")
        self.vitals.drift_rates = self.scenario.get("drifts", self.vitals.drift_rates)
        
        self.step_count = 0
        self.history = []
        self.is_done = False
        self.total_reward = 0.0
        
        # Determine solution tracking index
        self.solution_idx = 0
        
        return self.state()

    def state(self) -> Observation:
        if not self.vitals:
            self.reset(1)
        return Observation(
            spo2=round(self.vitals.spo2, 1),
            heart_rate=round(self.vitals.heart_rate, 1),
            blood_pressure_systolic=round(self.vitals.bp_sys, 1),
            blood_pressure_diastolic=round(self.vitals.bp_dia, 1),
            respiratory_rate=round(self.vitals.respiratory_rate, 1),
            temperature=round(self.vitals.temperature, 1),
            avpu=self.vitals.avpu,
            alarms_active=self.alarms_active,
            equipment_status=self.equipment_status,
            patient_status_notes=self.patient_notes
        )

    def step(self, action: Action) -> StepResponse:
        if self.is_done:
            return StepResponse(
                observation=self.state(),
                reward=Reward(reward=0.0, message="Episode already finished."),
                done=True,
                info={"episode_status": "finished"}
            )

        self.step_count += 1
        self.history.append(action.value)
        
        step_reward = -0.05 # Penalty for wasting a step
        reward_msg = f"Action taken: {action.value}. Wasted step penalty: -0.05."

        # Evaluate against the ideal solution script
        expected_solution = self.scenario["solution"]
        if self.solution_idx < len(expected_solution) and action.value == expected_solution[self.solution_idx]:
            self.solution_idx += 1
            step_reward += 0.5
            reward_msg += " Good action sequence! Stabilizing slightly."
            # Stabilize drifts slightly for taking correct action
            for k in self.vitals.drift_rates:
                self.vitals.drift_rates[k] *= 0.5 
        else:
            reward_msg += " Action did not progress the optimal sequence."

        # Process logical implications of certain actions regardless of ideal solution
        if action == Action.SILENCE_ALARM:
            self.alarms_active = False
            reward_msg += " Alarms silenced."
        
        # Apply vitals drift
        self.vitals.apply_drift()
        
        # Hard limits & checks
        critical_vitals = self.vitals.check_critical()
        if self.step_count > 3:
            if critical_vitals >= 2:
                self.is_done = True
                step_reward -= 1.0 # Failure 
                reward_msg = "Patient deteriorated significantly (2+ critical vitals). Failure."
                self.total_reward += step_reward
                return StepResponse(
                    observation=self.state(),
                    reward=Reward(reward=round(step_reward, 2), message=reward_msg),
                    done=True,
                    info={"episode_status": "failure_critical_vitals", "critical_count": critical_vitals}
                )

        if self.step_count >= 30: # Hardcoded rule: 30 steps exceeded
            self.is_done = True
            step_reward -= 0.5
            reward_msg = "Time threshold exceeded (30 steps). Failure."
            self.total_reward += step_reward
            return StepResponse(
                observation=self.state(),
                reward=Reward(reward=round(step_reward, 2), message=reward_msg),
                done=True,
                info={"episode_status": "failure_timeout"}
            )

        # Success check: Escalation/Doctor Arrival
        # A successful resolution is when doctor arrives AND patient is relatively stable
        escalation_actions = [Action.CALL_ATTENDING_DOCTOR, Action.CALL_ICU_SPECIALIST, Action.CALL_CODE_BLUE]
        if action in escalation_actions:
            self.is_done = True
            step_reward += 2.0
            reward_msg = "Doctor/Specialist arrived, patient handed over! Success."
            self.total_reward += step_reward
            return StepResponse(
                observation=self.state(),
                reward=Reward(reward=round(step_reward, 2), message=reward_msg),
                done=True,
                info={"episode_status": "success_doctor_arrival"}
            )

        self.total_reward += step_reward
        return StepResponse(
            observation=self.state(),
            reward=Reward(reward=round(step_reward, 2), message=reward_msg),
            done=False,
            info={"step_count": self.step_count, "critical_vitals": critical_vitals}
        )

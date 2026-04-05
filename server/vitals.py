import random

class VitalsSim:
    def __init__(self):
        self.spo2 = 98.0
        self.heart_rate = 75.0
        self.bp_sys = 120.0
        self.bp_dia = 80.0
        self.respiratory_rate = 16.0
        self.temperature = 37.0
        self.avpu = "Alert"
        
        self.drift_rates = {
            "spo2": 0.0,
            "heart_rate": 0.0,
            "bp_sys": 0.0,
            "bp_dia": 0.0,
            "respiratory_rate": 0.0,
        }
    
    def apply_drift(self):
        # Adding some random noise on top of drift
        self.spo2 += self.drift_rates["spo2"] + random.uniform(-0.5, 0.5)
        self.heart_rate += self.drift_rates["heart_rate"] + random.uniform(-1.0, 1.0)
        self.bp_sys += self.drift_rates["bp_sys"] + random.uniform(-1.0, 1.0)
        self.bp_dia += self.drift_rates["bp_dia"] + random.uniform(-0.5, 0.5)
        self.respiratory_rate += self.drift_rates["respiratory_rate"] + random.uniform(-0.5, 0.5)

        # Clamping values into physiological limits
        self.spo2 = max(0.0, min(100.0, self.spo2))
        self.heart_rate = max(0.0, min(300.0, self.heart_rate))
        self.bp_sys = max(0.0, min(300.0, self.bp_sys))
        self.bp_dia = max(0.0, min(200.0, self.bp_dia))
        self.respiratory_rate = max(0.0, min(60.0, self.respiratory_rate))
    
    def check_critical(self):
        critical_count = 0
        if self.spo2 < 85.0: critical_count += 1
        if self.heart_rate < 40 or self.heart_rate > 140: critical_count += 1
        if self.bp_sys < 80 or self.bp_sys > 180: critical_count += 1
        if self.respiratory_rate < 8 or self.respiratory_rate > 35: critical_count += 1
        if self.avpu == "Unresponsive": critical_count += 1
        return critical_count

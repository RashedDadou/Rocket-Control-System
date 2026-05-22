# Thrust_Measurement_System.py


import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ThrustReading:
    engine_id: int
    thrust_newtons: float          # القوة بالنيوتن
    thrust_kilonewtons: float
    throttle_percent: float
    timestamp: float
    sensor_status: str             # OK, WARNING, FAULT
    temperature: float = 0.0       # درجة حرارة المحرك (اختياري)


class ThrustMeasurementSystem:
    """
    نظام قياس قوة الدفع لمحركات Raptor
    """

    def __init__(self, total_engines: int = 33):
        self.total_engines = total_engines
        self.readings: Dict[int, ThrustReading] = {}
        self.calibration_factor = 1.0  # يمكن تعديله حسب المعايرة
        
        # تهيئة القراءات
        for i in range(total_engines):
            self.readings[i] = ThrustReading(
                engine_id=i,
                thrust_newtons=0.0,
                thrust_kilonewtons=0.0,
                throttle_percent=0.0,
                timestamp=time.time(),
                sensor_status="OK"
            )
        
        logger.info(f"✅ ThrustMeasurementSystem جاهز | {total_engines} محرك")

    def read_thrust(self, engine_id: int) -> ThrustReading:
        """قراءة قوة الدفع لمحرك معين (محاكاة + إمكانية ربط بحساس حقيقي)"""
        if engine_id not in self.readings:
            logger.error(f"Engine {engine_id} غير موجود")
            return None

        # محاكاة واقعية (يمكن استبدالها بقراءة من Load Cell حقيقي)
        current_throttle = self.readings[engine_id].throttle_percent
        
        # Raptor engine thrust تقريباً 2300 kN في Full Power
        base_thrust = 2300000  # نيوتن
        measured_thrust = base_thrust * (current_throttle / 100.0) * self.calibration_factor
        
        # إضافة ضوضاء عشوائية واقعية
        noise = np.random.normal(0, measured_thrust * 0.008)
        final_thrust = measured_thrust + noise

        reading = ThrustReading(
            engine_id=engine_id,
            thrust_newtons=final_thrust,
            thrust_kilonewtons=final_thrust / 1000,
            throttle_percent=current_throttle,
            timestamp=time.time(),
            sensor_status="OK",
            temperature=650 + np.random.normal(0, 30)  # درجة حرارة تقريبية
        )

        self.readings[engine_id] = reading
        return reading

    def read_all_engines(self) -> List[ThrustReading]:
        """قراءة جميع المحركات"""
        return [self.read_thrust(i) for i in range(self.total_engines)]

    def get_total_thrust(self) -> Tuple[float, float]:
        """إجمالي قوة الدفع (نيوتن + كيلو نيوتن)"""
        total_n = sum(r.thrust_newtons for r in self.readings.values())
        return total_n, total_n / 1000

    def update_throttle(self, engine_id: int, throttle_percent: float):
        """تحديث نسبة الـ Throttle (يُستدعى من Valve Controller)"""
        if engine_id in self.readings:
            self.readings[engine_id].throttle_percent = min(max(throttle_percent, 0), 100)

    def detect_anomalies(self) -> List[Dict]:
        """كشف المحركات غير الطبيعية"""
        anomalies = []
        for engine_id, reading in self.readings.items():
            expected = 2300 * (reading.throttle_percent / 100)  # kN
            actual = reading.thrust_kilonewtons
            
            deviation = abs(actual - expected) / expected * 100 if expected > 0 else 0
            
            if deviation > 12 or reading.sensor_status == "FAULT":
                anomalies.append({
                    "engine_id": engine_id,
                    "expected_kn": expected,
                    "actual_kn": actual,
                    "deviation_percent": deviation,
                    "status": reading.sensor_status
                })
        
        if anomalies:
            logger.warning(f"⚠️ تم اكتشاف {len(anomalies)} محرك غير طبيعي")
        
        return anomalies

    def emergency_thrust_check(self) -> bool:
        """فحص طارئ للدفع الكلي"""
        total_thrust_kn = self.get_total_thrust()[1]
        min_acceptable = 45000  # 45,000 kN كحد أدنى تقريبي في الإقلاع
        
        if total_thrust_kn < min_acceptable:
            logger.critical(f"🚨 THRUST TOO LOW! Total: {total_thrust_kn:.0f} kN")
            return False
        return True
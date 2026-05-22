# Smart_Raptor_Controller.py

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from Thrust_Measurement_System import ThrustMeasurementSystem, ThrustReading
from Fuel_Tanks_Measurement_System import FuelTanksMeasurementSystem, TankReading

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class ValveState(Enum):
    CLOSED = 0
    OPEN = 1
    OPENING = 2
    CLOSING = 3
    FAULT = 4


@dataclass
class EngineValve:
    engine_id: int
    state: ValveState
    throttle_percent: float = 0.0   # 0% إلى 100%
    last_command_time: float = 0.0
    fault_detected: bool = False


class RocketValveController:
    """
    نظام التحكم في عنفات رؤوس المحركات (Raptor Engines)
    """

    def __init__(self, total_engines: int = 33):
        self.total_engines = total_engines
        self.engines: Dict[int, EngineValve] = {}
        self.thrust_system = Thrust_Measurement_System(total_engines)
        self.fuel_system = Fuel_Tanks_Measurement_System()

        
        # تهيئة جميع المحركات
        for i in range(total_engines):
            self.engines[i] = EngineValve(
                engine_id=i,
                state=ValveState.CLOSED,
                throttle_percent=0.0
            )
        
        logger.info(f"🚀 RocketValveController جاهز | عدد المحركات: {total_engines}")

    def detect_valve_status(self, engine_id: int) -> Dict:
        """كشف حالة العنفة لمحرك معين"""
        if engine_id not in self.engines:
            return {"error": "Engine ID غير موجود"}
        
        valve = self.engines[engine_id]
        
        return {
            "engine_id": engine_id,
            "state": valve.state.name,
            "throttle_percent": valve.throttle_percent,
            "fault_detected": valve.fault_detected,
            "last_command_seconds_ago": time.time() - valve.last_command_time
        }

    def detect_all_valves(self) -> List[Dict]:
        """كشف حالة جميع العنفات"""
        return [self.detect_valve_status(i) for i in range(self.total_engines)]

    def command_valve(self, engine_id: int, target_state: ValveState, throttle: float = 100.0) -> bool:
        """أمر بفتح أو إغلاق عنفة محرك معين"""
        if engine_id not in self.engines:
            logger.error(f"Engine {engine_id} غير موجود")
            return False

        valve = self.engines[engine_id]
        valve.last_command_time = time.time()

        # محاكاة زمن الاستجابة
        if target_state == ValveState.OPEN:
            valve.state = ValveState.OPENING
            time.sleep(0.08)  # زمن افتراضي لفتح العنفة
            valve.state = ValveState.OPEN
            valve.throttle_percent = min(max(throttle, 0), 100)
            logger.info(f"✅ Engine {engine_id} → OPEN | Throttle: {throttle}%")
            
        elif target_state == ValveState.CLOSED:
            valve.state = ValveState.CLOSING
            time.sleep(0.12)  # زمن إغلاق أطول
            valve.state = ValveState.CLOSED
            valve.throttle_percent = 0.0
            logger.info(f"✅ Engine {engine_id} → CLOSED")
        
        return True

    def set_thrust_profile(self, active_engines: List[int], throttle_percent: float = 100.0):
        """ضبط ملف الدفع (أي محركات تشتغل وبأي قوة)"""
        logger.info(f"🔧 Setting Thrust Profile | Active Engines: {len(active_engines)} | Throttle: {throttle_percent}%")
        
        # إغلاق كل المحركات أولاً
        for engine in self.engines.values():
            if engine.engine_id not in active_engines:
                self.command_valve(engine.engine_id, ValveState.CLOSED)
        
        # فتح المحركات المطلوبة
        for engine_id in active_engines:
            self.command_valve(engine_id, ValveState.OPEN, throttle_percent)

        # بعد تغيير Throttle
        self.thrust_system.update_throttle(engine_id, throttle)
        
        # فحص فوري
        if self.thrust_system.emergency_thrust_check() == False:
            self.emergency_shutdown()

    def emergency_shutdown(self):
        """إغلاق طارئ لكل المحركات"""
        logger.critical("🚨 EMERGENCY SHUTDOWN ACTIVATED")
        for engine_id in range(self.total_engines):
            self.command_valve(engine_id, ValveState.CLOSED)
        logger.critical("✅ All engines shut down")

# ====================== مثال الاستخدام ======================

if __name__ == "__main__":
    controller = RocketValveController(total_engines=33)
    
    print("=== اختبار النظام ===")
    
    # مرحلة الإقلاع: كل المحركات 100%
    controller.set_thrust_profile(list(range(33)), throttle_percent=100.0)
    
    time.sleep(2)
    
    # بعد 12 كم: إيقاف 6 محركات
    active = list(range(27))
    controller.set_thrust_profile(active, throttle_percent=92.0)
    
    # كشف حالة بعض المحركات
    print("\n=== حالة بعض العنفات ===")
    for i in [0, 10, 32]:
        status = controller.detect_valve_status(i)
        print(status)
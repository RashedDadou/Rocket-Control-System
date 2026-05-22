# Advanced_Thrust_Control_System.py

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class ThrustGroup(Enum):
    ALL = "all"
    SINGLE = "single"
    EVEN = "even"
    ODD = "odd"
    OUTER_RING = "outer_ring"
    INNER_RING = "inner_ring"
    CENTER = "center"


@dataclass
class ThrustCommand:
    group: ThrustGroup
    target_throttle: float      # 0-100%
    engine_id: Optional[int] = None   # للتحكم في محرك واحد
    duration: Optional[float] = None


class AdvancedThrustControlSystem:
    """
    نظام تحكم متقدم بقوة الدفع لـ 33 محرك Raptor
    يدعم التحكم على عدة مستويات
    """

    def __init__(self, valve_controller):
        self.valve_controller = valve_controller
        self.total_engines = 33
        
        # تعريف الحلقات (Rings) حسب تصميم Starship
        self.outer_ring = list(range(0, 9))           # 9 محركات خارجية
        self.inner_ring = list(range(9, 24))          # 15 محرك داخلي
        self.center_engines = [24, 25, 26, 27, 28, 29, 30, 31, 32]  # 9 محركات مركزية

    def set_thrust_group(self, group: ThrustGroup, throttle_percent: float, engine_id: Optional[int] = None):
        """التحكم الرئيسي حسب المجموعة"""
        throttle = max(0, min(100, throttle_percent))
        
        if group == ThrustGroup.ALL:
            active_engines = list(range(self.total_engines))
            logger.info(f"🔥 ALL ENGINES → {throttle}% Thrust")
            
        elif group == ThrustGroup.SINGLE and engine_id is not None:
            active_engines = [engine_id]
            logger.info(f"🎯 SINGLE Engine {engine_id} → {throttle}%")
            
        elif group == ThrustGroup.EVEN:
            active_engines = [i for i in range(self.total_engines) if i % 2 == 0]
            logger.info(f"🔄 EVEN Engines → {throttle}%")
            
        elif group == ThrustGroup.ODD:
            active_engines = [i for i in range(self.total_engines) if i % 2 == 1]
            logger.info(f"🔄 ODD Engines → {throttle}%")
            
        elif group == ThrustGroup.OUTER_RING:
            active_engines = self.outer_ring
            logger.info(f"🌍 OUTER RING ({len(active_engines)} engines) → {throttle}%")
            
        elif group == ThrustGroup.INNER_RING:
            active_engines = self.inner_ring
            logger.info(f"🔵 INNER RING ({len(active_engines)} engines) → {throttle}%")
            
        elif group == ThrustGroup.CENTER:
            active_engines = self.center_engines
            logger.info(f"⭐ CENTER ENGINES ({len(active_engines)} engines) → {throttle}%")
            
        else:
            logger.error("مجموعة غير معروفة")
            return False

        # تنفيذ الأمر عبر Valve Controller
        self.valve_controller.set_thrust_profile(active_engines, throttle)
        return True

    def ramp_thrust(self, group: ThrustGroup, target_throttle: float, ramp_time: float = 3.0, engine_id: Optional[int] = None):
        """زيادة أو تقليل الدفع تدريجياً (Ramp)"""
        logger.info(f"📈 Ramping {group.value} to {target_throttle}% over {ramp_time} seconds")
        
        steps = int(ramp_time * 10)  # 10 تحديثات في الثانية
        current = 0.0
        step_size = target_throttle / steps
        
        for _ in range(steps):
            current += step_size
            self.set_thrust_group(group, current, engine_id)
            time.sleep(ramp_time / steps)

    def asymmetric_thrust(self, left_percent: float, right_percent: float):
        """تحكم غير متماثل (للتوجيه الجانبي)"""
        left_engines = [i for i in range(self.total_engines) if i % 3 != 2]   # مثال تقريبي
        right_engines = [i for i in range(self.total_engines) if i % 3 == 2]
        
        self.valve_controller.set_thrust_profile(left_engines, left_percent)
        self.valve_controller.set_thrust_profile(right_engines, right_percent)
        
        logger.info(f"↔️ Asymmetric Thrust | Left: {left_percent}% | Right: {right_percent}%")

    def get_thrust_status(self) -> Dict:
        """تقرير شامل لحالة الدفع"""
        active = sum(1 for v in self.valve_controller.engines.values() if v.state.name == "OPEN")
        return {
            "total_engines": self.total_engines,
            "active_engines": active,
            "outer_ring_active": sum(1 for i in self.outer_ring if self.valve_controller.engines[i].state.name == "OPEN"),
            "inner_ring_active": sum(1 for i in self.inner_ring if self.valve_controller.engines[i].state.name == "OPEN"),
            "center_active": sum(1 for i in self.center_engines if self.valve_controller.engines[i].state.name == "OPEN")
        }
# Fuel_Tanks_Measurement_System.py

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class PropellantType(Enum):
    LOX = "Liquid Oxygen"
    METHANE = "Liquid Methane"
    RP1 = "RP-1 Kerosene"


@dataclass
class TankReading:
    tank_id: str
    propellant_type: PropellantType
    current_volume: float          # متر مكعب
    current_percent: float         # 0-100%
    temperature_kelvin: float
    pressure_bar: float
    flow_rate_kgs: float = 0.0     # معدل التدفق (كيلوجرام/ثانية)
    status: str = "NORMAL"         # NORMAL, LOW, CRITICAL, LEAK
    last_updated: float = 0.0


class FuelTanksMeasurementSystem:
    """
    نظام قياس خزانات الوقود لصاروخ Starship
    """

    def __init__(self):
        self.tanks: Dict[str, TankReading] = {}
        
        # تهيئة خزانات Starship (تقريبي)
        self._initialize_tanks()
        
        logger.info("✅ FuelTanksMeasurementSystem تم تهيئته | عدد الخزانات: 6")

    def _initialize_tanks(self):
        """تهيئة خزانات Starship V3"""
        tanks_config = [
            ("LOX_Header", PropellantType.LOX, 1200, 90.0, 92.0),      # خزان رأسي
            ("LOX_Main", PropellantType.LOX, 2400, 88.0, 91.5),
            ("CH4_Header", PropellantType.METHANE, 800, 89.0, 110.0),
            ("CH4_Main", PropellantType.METHANE, 1800, 87.0, 112.0),
            ("LOX_Reserve", PropellantType.LOX, 300, 75.0, 90.0),
            ("CH4_Reserve", PropellantType.METHANE, 250, 72.0, 108.0),
        ]
        
        for tank_id, prop_type, max_vol, percent, temp in tanks_config:
            self.tanks[tank_id] = TankReading(
                tank_id=tank_id,
                propellant_type=prop_type,
                current_volume=max_vol * (percent / 100),
                current_percent=percent,
                temperature_kelvin=temp,
                pressure_bar=4.8 if prop_type == PropellantType.LOX else 3.2,
                last_updated=time.time()
            )

    def read_tank(self, tank_id: str) -> Optional[TankReading]:
        """قراءة حالة خزان معين"""
        if tank_id not in self.tanks:
            logger.error(f"خزان {tank_id} غير موجود")
            return None
        
        tank = self.tanks[tank_id]
        
        # محاكاة تغييرات طفيفة (يمكن ربطها بحساسات حقيقية)
        self._simulate_realistic_change(tank)
        
        return tank

    def read_all_tanks(self) -> List[TankReading]:
        """قراءة جميع الخزانات"""
        return [self.read_tank(tid) for tid in self.tanks.keys()]

    def _simulate_realistic_change(self, tank: TankReading):
        """محاكاة تغييرات واقعية في الخزان"""
        import random
        tank.last_updated = time.time()
        
        # انخفاض طفيف في مستوى الوقود
        consumption = random.uniform(0.08, 0.35)
        tank.current_percent = max(5.0, tank.current_percent - consumption)
        tank.current_volume = tank.current_percent * 0.01 * 3000  # تقريبي

        # تغير درجة الحرارة
        tank.temperature_kelvin += random.uniform(-0.3, 0.4)

        # تحديث الحالة
        if tank.current_percent < 15:
            tank.status = "CRITICAL"
        elif tank.current_percent < 35:
            tank.status = "LOW"
        else:
            tank.status = "NORMAL"

    def get_total_propellant(self) -> Dict[str, float]:
        """إجمالي الوقود المتبقي"""
        total_lox = sum(t.current_volume for t in self.tanks.values() 
                       if t.propellant_type == PropellantType.LOX)
        total_ch4 = sum(t.current_volume for t in self.tanks.values() 
                       if t.propellant_type == PropellantType.METHANE)
        
        return {
            "LOX_m3": round(total_lox, 2),
            "Methane_m3": round(total_ch4, 2),
            "Total_Propellant_m3": round(total_lox + total_ch4, 2)
        }

    def get_fuel_status_summary(self) -> Dict:
        """تقرير شامل لحالة الوقود"""
        total = self.get_total_propellant()
        low_tanks = [t for t in self.tanks.values() if t.status in ["LOW", "CRITICAL"]]
        
        return {
            "status": "CRITICAL" if len(low_tanks) > 2 else "WARNING" if low_tanks else "NORMAL",
            "total_propellant_m3": total,
            "low_tanks_count": len(low_tanks),
            "critical_tanks": [t.tank_id for t in low_tanks if t.status == "CRITICAL"],
            "timestamp": time.time()
        }

    def emergency_fuel_dump(self, tank_id: str = None):
        """تفريغ طارئ لخزان أو كل الخزانات"""
        if tank_id:
            if tank_id in self.tanks:
                self.tanks[tank_id].current_percent = 0
                logger.critical(f"🚨 EMERGENCY DUMP ACTIVATED for tank {tank_id}")
        else:
            for tank in self.tanks.values():
                tank.current_percent = 0
            logger.critical("🚨 FULL EMERGENCY FUEL DUMP ACTIVATED - All tanks emptied")
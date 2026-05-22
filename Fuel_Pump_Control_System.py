# Fuel_Pump_Control_System.py

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class PumpState(Enum):
    OFF = 0
    STARTING = 1
    RUNNING = 2
    SHUTDOWN = 3
    FAULT = 4


@dataclass
class Turbopump:
    pump_id: str
    propellant_type: str          # LOX or Methane
    rpm: float                    # دورات في الدقيقة
    target_rpm: float
    pressure_output_bar: float
    temperature_celsius: float
    state: PumpState
    power_percent: float = 0.0
    last_command_time: float = 0.0
    fault_code: str = ""


class FuelPumpControlSystem:
    """
    نظام التحكم في محركات ضخ الوقود (Turbopumps) لصاروخ Starship
    """

    def __init__(self):
        self.pumps: Dict[str, Turbopump] = {}
        self._initialize_pumps()
        
        logger.info("✅ FuelPumpControlSystem تم تهيئته | 8 Turbopumps (4 LOX + 4 Methane)")

    def _initialize_pumps(self):
        """تهيئة محركات الضخ (Raptor لديه turbopump منفصل لكل وقود)"""
        configs = [
            ("LOX_Pump_1", "LOX", 28000),
            ("LOX_Pump_2", "LOX", 28500),
            ("LOX_Pump_3", "LOX", 27500),
            ("LOX_Pump_4", "LOX", 28200),
            ("CH4_Pump_1", "METHANE", 32000),
            ("CH4_Pump_2", "METHANE", 31800),
            ("CH4_Pump_3", "METHANE", 32500),
            ("CH4_Pump_4", "METHANE", 31500),
        ]
        
        for pid, ptype, base_rpm in configs:
            self.pumps[pid] = Turbopump(
                pump_id=pid,
                propellant_type=ptype,
                rpm=0.0,
                target_rpm=base_rpm,
                pressure_output_bar=0.0,
                temperature_celsius=25.0,
                state=PumpState.OFF
            )

    def start_pump(self, pump_id: str, target_rpm: Optional[float] = None) -> bool:
        """تشغيل مضخة وقود معينة"""
        if pump_id not in self.pumps:
            logger.error(f"Pump {pump_id} غير موجود")
            return False

        pump = self.pumps[pump_id]
        pump.last_command_time = time.time()
        pump.state = PumpState.STARTING
        
        if target_rpm:
            pump.target_rpm = target_rpm

        # محاكاة وقت بدء التشغيل
        time.sleep(0.35)
        pump.state = PumpState.RUNNING
        pump.rpm = pump.target_rpm * 0.98
        pump.pressure_output_bar = 280 if "LOX" in pump_id else 180
        pump.power_percent = 92.0

        logger.info(f"🚀 Pump {pump_id} STARTED | RPM: {pump.rpm:.0f} | Pressure: {pump.pressure_output_bar:.1f} bar")
        return True

    def set_pump_speed(self, pump_id: str, rpm_percent: float):
        """ضبط سرعة المضخة (نسبة مئوية)"""
        if pump_id not in self.pumps:
            return False

        pump = self.pumps[pump_id]
        pump.target_rpm = pump.target_rpm * (rpm_percent / 100)
        pump.power_percent = rpm_percent
        pump.rpm = pump.target_rpm * 0.97
        
        logger.info(f"⚙️ Pump {pump_id} Speed set to {rpm_percent}% | RPM: {pump.rpm:.0f}")
        return True

    def shutdown_pump(self, pump_id: str):
        """إيقاف مضخة معينة"""
        if pump_id not in self.pumps:
            return False

        pump = self.pumps[pump_id]
        pump.state = PumpState.SHUTDOWN
        time.sleep(0.25)
        pump.rpm = 0.0
        pump.pressure_output_bar = 0.0
        pump.power_percent = 0.0
        pump.state = PumpState.OFF
        
        logger.info(f"⛔ Pump {pump_id} SHUTDOWN")
        return True

    def emergency_all_pumps_shutdown(self):
        """إغلاق طارئ لكل مضخات الوقود"""
        logger.critical("🚨 EMERGENCY TURBOPUMPS SHUTDOWN ACTIVATED")
        for pump_id in self.pumps.keys():
            self.shutdown_pump(pump_id)
        logger.critical("✅ All Turbopumps have been shut down")

    def get_pumps_status(self) -> List[Dict]:
        """تقرير حالة جميع المضخات"""
        return [{
            "pump_id": p.pump_id,
            "type": p.propellant_type,
            "state": p.state.name,
            "rpm": round(p.rpm, 0),
            "target_rpm": round(p.target_rpm, 0),
            "pressure_bar": round(p.pressure_output_bar, 1),
            "power_percent": round(p.power_percent, 1),
            "temperature": round(p.temperature_celsius, 1)
        } for p in self.pumps.values()]

    def get_system_summary(self) -> Dict:
        """ملخص النظام"""
        running = sum(1 for p in self.pumps.values() if p.state == PumpState.RUNNING)
        total_pressure = sum(p.pressure_output_bar for p in self.pumps.values())
        
        return {
            "total_pumps": len(self.pumps),
            "running_pumps": running,
            "average_pressure_bar": round(total_pressure / len(self.pumps), 1),
            "status": "NOMINAL" if running >= 6 else "DEGRADED"
        }
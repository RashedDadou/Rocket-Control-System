# Gimbal_AI_Controller.py

import time
import logging
import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class GimbalCommand:
    engine_id: int
    gimbal_x: float      # Pitch direction
    gimbal_y: float      # Yaw direction
    throttle: float


class GimbalAIController:
    """نظام التحكم الذكي في زوايا المحركات (Gimbal Control)"""
    
    def __init__(self, max_gimbal_angle: float = 12.0):
        self.max_gimbal_angle = max_gimbal_angle
        self.current_angles: Dict[int, Tuple[float, float]] = {}
        logger.info(f"✅ GimbalAIController جاهز | Max Gimbal Angle: ±{max_gimbal_angle}°")

    def calculate_gimbal_commands(self, 
                                  desired_pitch: float, 
                                  desired_yaw: float, 
                                  desired_roll: float) -> Dict[int, GimbalCommand]:
        """
        حساب زوايا الجيمبال بطريقة أكثر ذكاءً
        """
        commands = {}
        
        for engine_id in range(33):
            # حساب الزاوية المحيطية للمحرك
            engine_angle = (engine_id * 360.0) / 33
            
            # تأثير كل محرك على المحاور الثلاثة
            pitch_effect = desired_pitch * np.cos(np.radians(engine_angle))
            yaw_effect   = desired_yaw   * np.sin(np.radians(engine_angle))
            roll_effect  = desired_roll * 0.25   # تأثير أقل على الـ Roll
            
            # الزاوية النهائية
            gimbal_x = np.clip(pitch_effect + roll_effect, -self.max_gimbal_angle, self.max_gimbal_angle)
            gimbal_y = np.clip(yaw_effect, -self.max_gimbal_angle, self.max_gimbal_angle)
            
            # تقليل الـ Throttle للمحركات اللي زاويتها كبيرة (للسلامة)
            throttle = 100.0 * (1 - (abs(gimbal_x) + abs(gimbal_y)) / (self.max_gimbal_angle * 2.5))
            
            commands[engine_id] = GimbalCommand(
                engine_id=engine_id,
                gimbal_x=round(gimbal_x, 3),
                gimbal_y=round(gimbal_y, 3),
                throttle=round(max(60, throttle), 1)   # الحد الأدنى 60%
            )

        return commands

    def log_commands(self, commands: Dict):
        """طباعة ملخص للأوامر"""
        total_gimbal = sum(abs(c.gimbal_x) + abs(c.gimbal_y) for c in commands.values())
        logger.info(f"📡 Gimbal Commands Calculated | Total Gimbal Effort: {total_gimbal:.2f}°")
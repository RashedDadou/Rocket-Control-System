# Rocket_3D_Visualizer.py

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import time
from typing import Dict
from Rocket_Valve_Controller import RocketValveController
from Thrust_Measurement_System import ThrustMeasurementSystem

class Rocket3DVisualizer:
    """
    واجهة عرض 3D تفاعلية لرؤوس محركات Starship (33 محرك Raptor)
    """
    
    def __init__(self, valve_controller: RocketValveController, thrust_system: ThrustMeasurementSystem):
        self.valve_controller = valve_controller
        self.thrust_system = thrust_system
        self.fig = None
        self.ax = None
        self.engine_points = None
        self.colors = None

    def setup_3d_view(self):
        """إعداد الواجهة الثلاثية الأبعاد"""
        self.fig = plt.figure(figsize=(12, 9))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_title('Starship V3 - Raptor Engines 3D Visualization', fontsize=14, pad=20)
        self.ax.set_xlabel('X Position')
        self.ax.set_ylabel('Y Position')
        self.ax.set_zlabel('Z (Height)')

        # إعداد محركات في شكل دائري (9 محركات خارجية + 3 داخلية + ... إلخ)
        self.update_visualization()
        plt.show(block=False)

    def update_visualization(self):
        """تحديث الواجهة بالبيانات الحية"""
        if self.ax is None:
            return

        self.ax.clear()
        self.ax.set_title('Starship V3 - Raptor Engines Live Status', fontsize=14)
        
        x, y, z = [], [], []
        colors = []
        sizes = []
        labels = []

        for engine_id in range(self.valve_controller.total_engines):
            valve = self.valve_controller.engines[engine_id]
            thrust = self.thrust_system.read_thrust(engine_id)
            
            # ترتيب المحركات في شكل دائري واقعي
            angle = (engine_id / self.valve_controller.total_engines) * 2 * np.pi
            radius = 4.5 if engine_id < 9 else 2.8 if engine_id < 24 else 1.2  # توزيع واقعي
            
            pos_x = radius * np.cos(angle)
            pos_y = radius * np.sin(angle)
            pos_z = 0
            
            x.append(pos_x)
            y.append(pos_y)
            z.append(pos_z)
            
            # تحديد اللون حسب الحالة
            if valve.state == "OPEN":
                intensity = thrust.thrust_kilonewtons / 2500
                color = (1.0, 0.3, 0.0, intensity) if intensity > 0.7 else (1.0, 0.6, 0.0, intensity)
            else:
                color = (0.3, 0.3, 0.3, 0.6)
            
            colors.append(color)
            sizes.append(180 if valve.state == "OPEN" else 80)
            labels.append(f"R{engine_id}")

        # رسم النقاط
        scatter = self.ax.scatter(x, y, z, c=colors, s=sizes, depthshade=True, alpha=0.9)

        # إضافة تسميات
        for i, txt in enumerate(labels):
            self.ax.text(x[i], y[i], z[i]+0.3, txt, fontsize=8)

        self.ax.set_xlim(-6, 6)
        self.ax.set_ylim(-6, 6)
        self.ax.set_zlim(-1, 2)

        # معلومات جانبية
        total_thrust = self.thrust_system.get_total_thrust()[1]
        active = sum(1 for v in self.valve_controller.engines.values() if v.state == "OPEN")
        
        info_text = f'Total Thrust: {total_thrust:.0f} kN\nActive Engines: {active}/{self.valve_controller.total_engines}'
        self.ax.text2D(0.02, 0.95, info_text, transform=self.ax.transAxes, fontsize=11, 
                      bbox=dict(facecolor='black', alpha=0.7))

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def live_monitor(self, interval: float = 1.0):
        """تشغيل مراقبة حية"""
        print("🚀 بدء المراقبة الحية لمحركات Starship (اضغط Ctrl+C للإيقاف)")
        try:
            while True:
                self.update_visualization()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 تم إيقاف المراقبة")
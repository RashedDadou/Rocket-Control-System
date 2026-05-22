# Rocket-Control-System
Advanced Control System for Starship V3 Rocket Engines (33 Raptor Engines)

---

## Overview

**Rocket-Control-System-v1** is an engineering simulation project that replicates the complete propulsion control system for the Starship rocket engines. It focuses on precise thrust control, turbine management, and guidance using both standard and advanced methods.


### Main Objective
Design of a **Multi-Layer Control System** that supports:
- Full control of 33 Raptor engines
- Control by group (all engines, single, double, outer/inner loops, central)
- Steering control (Gimbal Control)
- Monitoring of thrust, fuel, and pumps
- Safety and emergency systems

---

## Main Components

### 1. RocketValveController
- Controls the opening and closing of engine turbines
- Supports group and single commands

### 2. ThrustMeasurementSystem
- Measures the thrust of each engine in N and kN
- Detects anomalies and deviations

### 3. FuelTanksMeasurementSystem
- Monitors LOX and Methane tanks
- Calculates consumption and status

### 4. FuelPumpControlSystem
- Controls turbopumps (fuel pumps)
- Controls pressure and speed

### 5. Advanced Thrust Control System
- Advanced Group Thrust Control
- Asymmetric Thrust (for steering)
- Ramp Control (gradual change)

### 6. Gimbal AI Controller
- Intelligent Motor Angle Control (Gimbal)
- Angle Calculation Based on Pitch, Yaw, and Roll

---

## Project Features

- **Modular** Expandable Structure
- **Multi-Level Control** Support (All, Single, Loops, Even/Odd)
- Realistic Measurement Simulation (Thrust, Pressure, Temperature)
- Basic Safety System (Emergency Shutdown)
- Detailed Logging
- Design Similar to the Real Engineering of Starship

---

## How to Run

```bash
# Run the Main System
python main.py

```

---

Project Status/Current Stage:

Prototype/Simulation
Mode: Under Development (Simulation Only)
Rating: 8.4/10
Future (Roadmap)
Integration with a Realistic 3D Interface
Adding a PID Controller to the Gimbal
AI Optimizer for Thrust Distribution
Telemetry and Ground Control System
Complete Safety & Redundancy Layer

Note:
This project is designed as an educational/experimental engineering simulation and is not a real rocket control system. 

Developer: Rashed Dadouch
(In collaboration with Grok)

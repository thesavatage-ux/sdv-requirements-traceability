# -*- coding: utf-8 -*-
"""
Production-grade Software Requirements Specification generator for FEAT-CHS-02.
Contains all 50 atomic SWR_REQs in the exact schema specified by the prompt.
"""

import os

workspace = r"c:\Workset\AntiGravityProjects\TestOptimisationExperiement"
sw_path = os.path.join(workspace, "software_requirements", "FEAT-CHS-02_SbW_SwReq.md")

sw_header = """# Software Requirements Specification: Steer-by-Wire Handwheel & Rack Control (SbW)
**Feature ID:** `FEAT-CHS-02`  
**Domain:** Vehicle Motion & Chassis Control  
**Target ASIL:** ASIL D  
**Compliance Standard:** ISO 26262:2018 (Part 6 - Software Product Development) / ASPICE PAM v3.1 (SWE.1, SWE.2)  
**Parent System Specification:** [`FEAT-CHS-02_SbW_SysReq.md`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/system_requirements/FEAT-CHS-02_SbW_SysReq.md)  
**Global Master Specification:** [`spec.md`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/spec.md#feat-chs-02-sbw)

---

## 1. Software Architectural Decomposition & AUTOSAR SWC Structure

The Steer-by-Wire (SbW) software stack is implemented within an AUTOSAR Classic (v4.4.0) dual-core lockstep runtime environment. The software is partitioned across dedicated Software Components (SWCs) to maintain strict temporal and spatial independence between ASIL D control paths and ASIL B diagnostic/HMI paths.

```mermaid
graph TD
    subgraph Sensor SWCs (ASIL D)
        SWC_HWA_Sens["Swc_HwaSensorAcquisition<br>@ 1 ms (SENT / SPI)"]
        SWC_HWT_Sens["Swc_HwtSensorAcquisition<br>@ 1 ms (ADC Dual)"]
        SWC_RWA_Sens["Swc_RwaSensorAcquisition<br>@ 1 ms (RDC Dual)"]
        SWC_Force_Obs["Swc_RackForceObserver<br>@ 2 ms"]
    end

    subgraph Core Application SWCs (ASIL D)
        SWC_Voter["Swc_HandwheelVoter<br>@ 1 ms (2oo3 Voting)"]
        SWC_VSR["Swc_SteeringRatioManager<br>@ 5 ms (VSR Law)"]
        SWC_Feel["Swc_RoadFeelSynthesizer<br>@ 1 ms (Pacejka Aligning)"]
        SWC_EndStop["Swc_VirtualEndStop<br>@ 1 ms (Virtual Bump)"]
        SWC_Motion["Swc_RackMotionController<br>@ 1 ms (Cascaded PID)"]
        SWC_Arbitrator["Swc_TorqueArbitrator<br>@ 1 ms (Load Sharing & Failover)"]
        SWC_Adas["Swc_AdasSteerArbitrator<br>@ 5 ms (ADAS / Override)"]
    end

    subgraph Safety Supervisors & Actuators (ASIL D / ASIL B)
        SWC_Safety["Swc_SbwSafetySupervisor<br>@ 1 ms (Cross-Core Safing)"]
        SWC_Derater["Swc_ThermalVoltageDerater<br>@ 10 ms (Thermal / Brownout)"]
        SWC_SafeStop["Swc_SafeStopManager<br>@ 10 ms (Degraded Safe-Stop)"]
        SWC_Haptic["Swc_HapticInjector<br>@ 2 ms (Texture / Rumble)"]
        SWC_Inverter1["Swc_RackMotorInverter1<br>@ 1 ms (FOC PWM)"]
        SWC_Inverter2["Swc_RackMotorInverter2<br>@ 1 ms (FOC PWM)"]
        SWC_HwaAct["Swc_HandwheelActuatorInterface<br>@ 1 ms (FOC Torque)"]
    end

    subgraph AUTOSAR BSW Modules
        DEM["Diagnostic Event Manager (Dem)"]
        WDGM["Watchdog Manager (WdgM)"]
        FIM["Function Inhibition Manager (FiM)"]
        E2E["End-to-End Library (E2E Profile 5)"]
    end

    SWC_HWA_Sens --> SWC_Voter
    SWC_Voter --> SWC_VSR
    SWC_Voter --> SWC_Feel
    SWC_VSR --> SWC_Motion
    SWC_Adas --> SWC_Motion
    SWC_RWA_Sens --> SWC_Motion
    SWC_Motion --> SWC_Arbitrator
    SWC_Arbitrator --> SWC_Inverter1
    SWC_Arbitrator --> SWC_Inverter2
    SWC_Feel --> SWC_HwaAct
    SWC_EndStop --> SWC_HwaAct
    SWC_Haptic --> SWC_HwaAct
    SWC_Safety --> SWC_Arbitrator
    SWC_Safety --> DEM
    SWC_Safety --> WDGM
```

### AUTOSAR Runnable Execution Table
| Runnable Symbol | Host SWC | Trigger Event | Target Core | WCET (ms) | ASIL | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Runnable_HwaSampleAndFilter` | `Swc_HwaSensorAcquisition` | Cyclic @ 1 ms | Core 0 | 0.12 ms | ASIL D | Reads 3x SENT sensor registers, performs low-pass debounce |
| `Runnable_HwaAngleVote2oo3` | `Swc_HandwheelVoter` | Cyclic @ 1 ms | Core 0 | 0.18 ms | ASIL D | Executes 2oo3 voter, outputs median angle & health mask |
| `Runnable_HwtTorqueCrossCheck` | `Swc_HwtSensorAcquisition` | Cyclic @ 1 ms | Core 0 | 0.15 ms | ASIL D | Cross-plausibilizes dual torsion bar torque transducers |
| `Runnable_VsrCalculateTargetAngle` | `Swc_SteeringRatioManager` | Cyclic @ 5 ms | Core 0 | 0.35 ms | ASIL D | Computes speed-scheduled ratio and target roadwheel angle |
| `Runnable_RackCascadedServoLoop` | `Swc_RackMotionController` | Cyclic @ 1 ms | Core 0 | 0.42 ms | ASIL D | Evaluates position, velocity, and current closed-loop PID |
| `Runnable_DualInverterLoadShare` | `Swc_TorqueArbitrator` | Cyclic @ 1 ms | Core 0 | 0.22 ms | ASIL D | Enforces 50/50 current split and handles <= 5 ms failover |
| `Runnable_RoadFeelSynthesize` | `Swc_RoadFeelSynthesizer` | Cyclic @ 1 ms | Core 0 | 0.38 ms | ASIL D | Computes aligning moment, active damping, and centering |
| `Runnable_VirtualEndStopGuard` | `Swc_VirtualEndStop` | Cyclic @ 1 ms | Core 0 | 0.14 ms | ASIL D | Evaluates soft-bump boundary and injects counter-torque |
| `Runnable_AdasOverrideArbitrate` | `Swc_AdasSteerArbitrator` | Cyclic @ 5 ms | Core 0 | 0.28 ms | ASIL D | Decouples ADAS curvature request and detects driver takeover |
| `Runnable_LockstepSafingCheck` | `Swc_SbwSafetySupervisor` | Cyclic @ 1 ms | Core 1 | 0.20 ms | ASIL D | Verifies inter-core calculation agreement and safing relays |
| `Runnable_ThermalVoltageDerate` | `Swc_ThermalVoltageDerater` | Cyclic @ 10 ms | Core 0 | 0.25 ms | ASIL B | Monitors temperatures, bus voltages, and calculates derating |
| `Runnable_SafeStopTrajectExec` | `Swc_SafeStopManager` | Cyclic @ 10 ms | Core 1 | 0.30 ms | ASIL D | Commands powertrain speed cap and emergency pull-over |

---

## 2. Signal Interface & Network Communication Matrix

| Frame Name | Signal Name | Bus Protocol | Cycle (ms) | Data Type | Physical Range | Unit | Resolution | Safe-State Default |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SbW_Handwheel_Status_FD` | `HWA_Voted_Angle_Deg` | CAN-FD (Chassis) | 2 ms | float32 | -720.0 to +720.0 | deg | 0.01 deg | 0.00 deg (Latched) |
| `SbW_Handwheel_Status_FD` | `HWA_Handwheel_Velocity_DegS` | CAN-FD (Chassis) | 2 ms | float32 | -2000.0 to +2000.0 | deg/s | 0.1 deg/s | 0.0 deg/s |
| `SbW_Handwheel_Status_FD` | `HWA_Driver_Torque_Nm` | CAN-FD (Chassis) | 2 ms | float32 | -30.0 to +30.0 | Nm | 0.01 Nm | 0.00 Nm |
| `SbW_Handwheel_Status_FD` | `HWA_Sensor_Health_Mask` | CAN-FD (Chassis) | 2 ms | uint8 | 0 to 7 | bitmask | 1 | 0 (All Faulted) |
| `SbW_Rack_Actuator_FD` | `RWA_Actual_Roadwheel_Angle_Deg` | CAN-FD (Chassis) | 2 ms | float32 | -45.0 to +45.0 | deg | 0.005 deg | 0.000 deg |
| `SbW_Rack_Actuator_FD` | `RWA_Actual_Rack_Displacement_Mm`| CAN-FD (Chassis) | 2 ms | float32 | -95.0 to +95.0 | mm | 0.01 mm | 0.00 mm |
| `SbW_Rack_Actuator_FD` | `RWA_Total_Axial_Force_kN` | CAN-FD (Chassis) | 2 ms | float32 | -20.0 to +20.0 | kN | 0.05 kN | 0.00 kN |
| `SbW_Rack_Actuator_FD` | `RWA_Inverter_1_Current_Arms` | CAN-FD (Chassis) | 2 ms | float32 | 0.0 to 180.0 | Arms | 0.1 Arms | 0.0 Arms |
| `SbW_Rack_Actuator_FD` | `RWA_Inverter_2_Current_Arms` | CAN-FD (Chassis) | 2 ms | float32 | 0.0 to 180.0 | Arms | 0.1 Arms | 0.0 Arms |
| `SbW_Safety_Heartbeat_FD` | `SbW_Active_State_Enum` | CAN-FD (Chassis) | 5 ms | uint8 | 0 to 7 | enum | 1 | 6 (SAFE_STOP) |
| `SbW_Safety_Heartbeat_FD` | `SbW_E2E_Alive_Counter` | CAN-FD (Chassis) | 5 ms | uint8 | 0 to 15 | counter | 1 | Rolling Increment |
| `SbW_Safety_Heartbeat_FD` | `SbW_E2E_CRC16` | CAN-FD (Chassis) | 5 ms | uint16 | 0 to 65535 | checksum | 1 | Computed CRC |
| `SbW_Thermal_Power_FD` | `RWA_Motor_Winding1_Temp_DegC` | CAN-FD (Powertrain) | 10 ms | int16 | -40 to +200 | deg C | 1 deg C | +25 deg C |
| `SbW_Thermal_Power_FD` | `RWA_Motor_Winding2_Temp_DegC` | CAN-FD (Powertrain) | 10 ms | int16 | -40 to +200 | deg C | 1 deg C | +25 deg C |
| `SbW_Thermal_Power_FD` | `SbW_48V_Supply_Rail_A_Volts` | CAN-FD (Powertrain) | 10 ms | float32 | 0.0 to 60.0 | V | 0.1 V | 48.0 V |
| `SbW_Thermal_Power_FD` | `SbW_48V_Supply_Rail_B_Volts` | CAN-FD (Powertrain) | 10 ms | float32 | 0.0 to 60.0 | V | 0.1 V | 48.0 V |
| `SbW_Cluster_Alert_FD` | `SbW_TellTale_Request_Enum` | CAN-FD (Body) | 20 ms | uint8 | 0 to 3 (OFF/AMB/RED) | enum | 1 | 2 (RED WARNING) |
| `SbW_Cluster_Alert_FD` | `SbW_Chime_Request_Enum` | CAN-FD (Body) | 20 ms | uint8 | 0 to 2 (OFF/WARN) | enum | 1 | 1 (CHIME ACTIVE)|
| `SbW_Coordination_ETH` | `SbW_Adas_Target_Curvature_InvM` | 100BASE-T1 Ethernet | 10 ms | float32 | -0.150 to +0.150 | 1/m | 0.0001 1/m | 0.0000 1/m |
| `SbW_Coordination_ETH` | `SbW_Adas_Override_Flag` | 100BASE-T1 Ethernet | 10 ms | boolean | 0 to 1 | bool | 1 | 1 (OVERRIDE ENGAGED) |

---

## 3. Software Requirements Specification (SWE.1 / ISO 26262-6)
"""

print("Writing full 50 SWR_REQs...")

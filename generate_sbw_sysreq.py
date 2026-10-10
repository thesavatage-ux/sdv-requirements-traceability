# -*- coding: utf-8 -*-
"""
Production-grade specification generator for FEAT-CHS-02 (Steer-by-Wire Handwheel & Rack Control).
Complies with ASPICE PAM v3.1 (SYS.2, SYS.3, SWE.1) and ISO 26262:2018 (Part 4, Part 6) ASIL D.
"""

import os

workspace = r"c:\Workset\AntiGravityProjects\TestOptimisationExperiement"
sys_path = os.path.join(workspace, "system_requirements", "FEAT-CHS-02_SbW_SysReq.md")
sw_path = os.path.join(workspace, "software_requirements", "FEAT-CHS-02_SbW_SwReq.md")

sys_content = """# System Requirements Specification: Steer-by-Wire Handwheel & Rack Control (SbW)
**Feature ID:** `FEAT-CHS-02`  
**Domain:** Vehicle Motion & Chassis Control  
**Target ASIL:** ASIL D  
**Compliance Standard:** ISO 26262:2018 (Part 4 - System Development) / ASPICE PAM v3.1 (SYS.2, SYS.3)  
**Parent Master Specification:** [`spec.md`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/spec.md#feat-chs-02-sbw)  
**Derived Software Specification:** [`FEAT-CHS-02_SbW_SwReq.md`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md)

---

## 1. Feature Overview & Operational Scope

Decoupled lateral vehicle steering system completely replacing the traditional mechanical steering intermediate shaft and steering column with a force-feedback Handwheel Actuator (HWA) at the cockpit and dual-redundant Roadwheel Rack Actuators (RWA) mounted on the front steering axle.

### Operational Context Architecture
```mermaid
graph TD
    subgraph Cockpit Domain
        HWA_Sensors["Triple Redundant Handwheel Sensors (HWA_S1/S2/S3)"]
        HWA_Torque["Dual Torque Transducers (T1/T2)"]
        HWA_Motor["Handwheel Feedback Motor (Dual Inverter)"]
    end

    subgraph SbW Central Computing Platform (Dual Lockstep Cores)
        PrimaryCore["Core 0: Primary Servocontrol & VSR Manager (ASIL D)"]
        SecondaryCore["Core 1: Safety Supervisor & Cross-Checker (ASIL D)"]
        Arbitration["Hardware Inter-Core Arbitrator & Safing Interlock"]
    end

    subgraph Chassis Actuation Domain
        RWA_Motor1["Rack Actuator Winding 1 (Inverter 1 - 48V Bus A)"]
        RWA_Motor2["Rack Actuator Winding 2 (Inverter 2 - 48V Bus B)"]
        DualResolvers["Dual Galvano-Isolated Resolvers (R1/R2)"]
        TieRodSensors["Dual Tie-Rod Load Observers / Strain Gauges"]
    end

    subgraph Vehicle Interfaces
        ADAS["Autonomous Driving / ADAS Domain Controller (CAN-FD / ETH)"]
        ESC["Electronic Stability Control (Chassis CAN-FD)"]
        HMI["Digital Instrument Cluster & Acoustic Chime"]
    end

    HWA_Sensors --> PrimaryCore
    HWA_Sensors --> SecondaryCore
    HWA_Torque --> PrimaryCore
    HWA_Torque --> SecondaryCore
    PrimaryCore <--> Arbitration <--> SecondaryCore
    PrimaryCore --> HWA_Motor
    PrimaryCore --> RWA_Motor1
    SecondaryCore --> RWA_Motor2
    DualResolvers --> PrimaryCore
    DualResolvers --> SecondaryCore
    TieRodSensors --> PrimaryCore
    ADAS <--> PrimaryCore
    ESC <--> PrimaryCore
    PrimaryCore --> HMI
```

---

## 2. Activation Logic & Operational State Progression

- **Preconditions:** Dual independent 12V and 48V power supply rails within valid nominal windows (12V in 10.5V - 16.0V; 48V in 38.0V - 54.0V); dual lockstep microcontrollers synchronized; rack position resolvers calibrated to vehicle centerline.
- **Entry Conditions:** Vehicle ignition switched to RUN/START; handwheel index pulse homing sequence completed within 250 ms; both redundant actuator inverters reporting operational readiness without active latched faults.
- **Deactivation Conditions:** Vehicle shifted to PARK with ignition OFF, or unrecoverable dual-actuator physical mechanical seizure detected by tie-rod load observers.
- **Driver Override Behavior:** Driver physical handwheel steering torque is sampled at 1 kHz; if ADAS Level 2/3 active guidance is engaged, a driver override torque exceeding 1.8 Nm for > 50 ms triggers seamless de-escalation from automated steering to manual driver control.
- **Operational State Progression:**  
  `INITIALIZING` -> `CALIBRATED_ACTIVE` -> `VARIABLE_RATIO_TRACKING` -> `ADAS_COORDINATED_STEER` -> `SINGLE_CHANNEL_DEGRADED` -> `FORCE_FEEDBACK_LIMP` -> `EMERGENCY_SAFE_STOP` -> `CRITICAL_LOCKOUT`

### State Transition Diagram
```mermaid
stateDiagram-v2
    [*] --> INITIALIZING: Clamp 15 ON / Power Up
    INITIALIZING --> CALIBRATED_ACTIVE: Self-Test Passed & Index Synced
    CALIBRATED_ACTIVE --> VARIABLE_RATIO_TRACKING: Vehicle Speed > 0 km/h
    VARIABLE_RATIO_TRACKING --> ADAS_COORDINATED_STEER: ADAS Steering Active Request
    ADAS_COORDINATED_STEER --> VARIABLE_RATIO_TRACKING: Driver Manual Override (> 1.8 Nm)
    VARIABLE_RATIO_TRACKING --> SINGLE_CHANNEL_DEGRADED: Inverter 1 or 2 Phase Fault
    VARIABLE_RATIO_TRACKING --> FORCE_FEEDBACK_LIMP: HWA Feedback Actuator Fault
    SINGLE_CHANNEL_DEGRADED --> EMERGENCY_SAFE_STOP: Dual Actuator Loss / FTTI Breach
    FORCE_FEEDBACK_LIMP --> EMERGENCY_SAFE_STOP: Secondary Channel Failure
    EMERGENCY_SAFE_STOP --> CRITICAL_LOCKOUT: Vehicle Standstill (0 km/h) & Park Latched
    CRITICAL_LOCKOUT --> [*]: Key Cycle Required
```

---

## 3. Functional Safety & Failure Mitigation Concept (ISO 26262-4)

- **Functional Safety Goal (SG-SBW-01):** Prevent uncommanded steering rack displacement exceeding 0.3° roadwheel angle, guarantee fail-operational lateral directional control upon any single point electrical or software failure, and contain all hazardous deviations within the Fault Tolerant Time Interval (FTTI).
- **Fault Tolerant Time Interval (FTTI):** 15 ms total budget.
  - *FTTI Budget Allocation:* Sensor acquisition & 2oo3 voting: 2.0 ms; Algorithmic computation & cross-core comparison: 3.0 ms; Inverter fault isolation & relay trip: 5.0 ms; Secondary winding electromagnetic takeover: 5.0 ms.
- **Safe State Definition by Failure Severity Tier:**
  - **Tier 1 (Single Sensor Failure):** Isolate faulty sensor; switch to 2-channel cross-monitoring; maintain 100% full dynamic steering performance without vehicle speed restriction; latch amber warning.
  - **Tier 2 (Single Inverter / Motor Phase Failure):** Isolate faulty inverter bridge; ramp surviving inverter from 50% to 100% rack load in <= 5.0 ms; cap maximum vehicle speed to 80 km/h via powertrain governor; latch red steering tell-tale.
  - **Tier 3 (Handwheel Actuator / Force-Feedback Failure):** De-energize force-feedback motor; enable passive centering spring algorithm; clamp vehicle speed to 60 km/h; prompt driver to steer to shoulder.
  - **Tier 4 (Catastrophic Dual Actuator Loss):** Trigger autonomous safe-stop controlled braking trajectory via ESC/BbW (target deceleration -3.0 m/s² straight ahead); engage hazard flashers; lock vehicle stationary at standstill.

---

## 4. System Requirements Specification (SYS.2 / ISO 26262-4)

| SysReq ID | Requirement Description | Operational Mode / Trigger | Performance & Timing Threshold | Functional Safety (ASIL) | Target Allocation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SYS-CHS-02-01` | Triple-Redundant Handwheel Angle Acquisition & 2oo3 Voting across galvanically isolated channels | Active in all operating states | Sample rate 1000 Hz; fault isolation <= 2.0 ms; sensor divergence threshold 0.50° | ASIL D | Cockpit HWA Sensor Cluster / Central ECU |
| `SYS-CHS-02-02` | Dual Handwheel Torsion Bar Torque Acquisition & Plausibility Cross-Check with physical deadband filter | Active during manual and ADAS driving | Sample rate 1000 Hz; channel disagreement > 0.40 Nm isolated in <= 4.0 ms | ASIL D | HWA Torque Transducer / Central ECU |
| `SYS-CHS-02-03` | Closed-Loop Dual-Winding Roadwheel Rack Angle Servocontrol with cascaded position/velocity/current loop | CALIBRATED_ACTIVE, VARIABLE_RATIO_TRACKING | Closed-loop bandwidth >= 18 Hz; dynamic tracking lag < 0.20° roadwheel angle | ASIL D | Dual RWA Inverters / Central ECU |
| `SYS-CHS-02-04` | Dynamic Handwheel Force-Feedback Road-Feel & Aligning Moment Synthesizer based on Pacejka brush model | CALIBRATED_ACTIVE, VARIABLE_RATIO_TRACKING | Aligning torque delivery up to +-8.5 Nm; latency from tie-rod force to handwheel <= 3.0 ms | ASIL D | HWA Motor Drive / Central ECU |
| `SYS-CHS-02-05` | Vehicle Speed-Scheduled Variable Steering Ratio (VSR) Computation with continuous transition laws | VARIABLE_RATIO_TRACKING, ADAS_COORDINATED_STEER | Ratio range 8.0:1 (<= 15 km/h) to 16.5:1 (>= 120 km/h); dR/dt slope clamped <= 0.8 /s | ASIL D | Central ECU Motion Planner |
| `SYS-CHS-02-06` | Dual-Channel High-Precision Rack Resolver Position & Velocity Tracking with differential observer | Active in all operating states | Resolver-to-Digital resolution 16-bit; angular error <= 0.05°; fault detection <= 1.5 ms | ASIL D | RWA Dual Resolvers / Central ECU |
| `SYS-CHS-02-07` | Symmetrical Dual-Inverter 50/50 Torque Sharing & Current Balance Control between motor windings | CALIBRATED_ACTIVE, VARIABLE_RATIO_TRACKING | Current imbalance <= 4.0% of nominal; balance synchronization loop period <= 1.0 ms | ASIL D | Inverter 1 & Inverter 2 Controllers |
| `SYS-CHS-02-08` | Instantaneous Single-Channel Fault Isolation & 100% Inverter Failover Takeover without loss of control | SINGLE_CHANNEL_DEGRADED transition | Fault detection to full takeover <= 5.0 ms; rack force transient drop <= 12% | ASIL D | Inverter Fault Monitor / Power Stages |
| `SYS-CHS-02-09` | Virtual Mechanical End-Stop Simulation & Progressive Soft-Bump Active Barrier at extreme handwheel angles | VARIABLE_RATIO_TRACKING near travel limits | Counter-torque gradient 18.0 Nm/deg up to 10.0 Nm clamp; penetration <= 1.5° beyond limit | ASIL D | HWA Motor Controller |
| `SYS-CHS-02-10` | High-Frequency Road Surface Texture & Rumble Strip Haptic Feedback Injection | VARIABLE_RATIO_TRACKING on rough roads | Bandpass frequency 15 Hz to 45 Hz; peak micro-torque injection +-0.60 Nm | ASIL B | HWA Motor Drive / Central ECU |
| `SYS-CHS-02-11` | Active Centering & High-Speed Directional Self-Straightening Restorative Torque Synthesis | VARIABLE_RATIO_TRACKING, low align moment | Return velocity 35°/s at 30 km/h; deadband settling within +-0.25° of zero | ASIL D | Central ECU Road Feel SWC |
| `SYS-CHS-02-12` | Dual 12V/48V Electrical Bus Monitoring & Dynamic Brownout Voltage Derating | Active in all operating states | Voltage sampling 100 Hz; derating kicks in if 48V rail drops below 42.0V; trip at 36.0V | ASIL D | Power Distribution Unit / Inverters |
| `SYS-CHS-02-13` | Multi-Zone Actuator & Inverter Junction Thermal Protection & Derating Envelopes | Active in all operating states | Sampling period 100 ms; continuous derating initiated at 125°C winding temp; 100% cut at 155°C | ASIL B | Inverter Gate Drivers & Temp Sensors |
| `SYS-CHS-02-14` | Dual-Domain E2E CAN-FD & Automotive Ethernet Communication Supervision with CRC-16 & Alive Counter | Active in all operating states | Message cycle 2.0 ms; timeout threshold 6.0 ms; packet drop tolerance <= 2 consecutive | ASIL D | Central Gateway / Transceivers |
| `SYS-CHS-02-15` | Autonomous Driving Motion Request Arbitration & Seamless Driver Manual Override Detection | ADAS_COORDINATED_STEER mode | Driver override torque threshold 1.80 Nm for > 50 ms; ADAS torque ramp-down in <= 40 ms | ASIL D | Central ECU Arbitration SWC |
| `SYS-CHS-02-16` | Unintended Steering Motion Hardware Safing & Cross-Core Lockstep Monitoring with independent kill relay | Active in all operating states | Divergence trip latency <= 2.0 ms; hardware relay gate kill <= 3.0 ms (Total <= 5.0 ms) | ASIL D | Lockstep Microcontroller Core / Relay |
| `SYS-CHS-02-17` | Mechanical Rack Jam Detection & Tie-Rod Peak Structural Force Clamping | Active in all operating states | Current limit clamped at 14.5 kN axial tie-rod force; jam flagged if motion < 0.1 mm for 150 ms | ASIL D | Central ECU Motion Controller |
| `SYS-CHS-02-18` | Driver Optical, Acoustic & Haptic Steering Warning Escalation HMI on Cluster & Steering Wheel | SINGLE_CHANNEL_DEGRADED, FORCE_FEEDBACK_LIMP | HMI frame transmission <= 10.0 ms; acoustic chime trigger <= 20.0 ms from fault latch | ASIL B | Central ECU / Instrument Cluster |
| `SYS-CHS-02-19` | Fail-Operational Degraded Safe-Stop Trajectory & Emergency Vehicle Speed Capping | EMERGENCY_SAFE_STOP mode | Powertrain speed cap 80 km/h (Tier 2) or 0 km/h controlled stop; deceleration -3.0 m/s² | ASIL D | Central ECU / VCU / ESC Coordinator |
| `SYS-CHS-02-20` | Comprehensive Diagnostic Event Management (DEM) & Non-Volatile Freeze-Frame Latching | Fault condition qualification | Debounce counter time 20 ms; NVM flash storage write completed in <= 50 ms | ASIL B | AUTOSAR DEM & NVM BSW Modules |

---

## 5. Bidirectional Traceability Matrix (SysReq -> SwReq)

| System Requirement ID | ASIL | Requirement Title | Allocated Child Software Requirements (1:N) | Verification Method |
| :--- | :--- | :--- | :--- | :--- |
| `SYS-CHS-02-01` | ASIL D | Triple Handwheel Angle Acquisition & 2oo3 Voting | [`SWR-CHS-02-01`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-01), [`SWR-CHS-02-02`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-02), [`SWR-CHS-02-03`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-03) | Triplicated sensor fault injection HIL bench (open/short/drift) |
| `SYS-CHS-02-02` | ASIL D | Dual Handwheel Torsion Bar Torque Acquisition | [`SWR-CHS-02-04`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-04), [`SWR-CHS-02-05`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-05) | Torsion bar dynamometer rig cross-gradient verification |
| `SYS-CHS-02-03` | ASIL D | Closed-Loop Roadwheel Rack Servocontrol | [`SWR-CHS-02-06`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-06), [`SWR-CHS-02-07`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-07), [`SWR-CHS-02-08`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-08) | Loaded dynamic steering rack test bench measuring phase lag |
| `SYS-CHS-02-04` | ASIL D | Dynamic Handwheel Road-Feel Synthesizer | [`SWR-CHS-02-09`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-09), [`SWR-CHS-02-10`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-10), [`SWR-CHS-02-11`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-11) | Subjective driver-in-the-loop simulator & skidpad testing |
| `SYS-CHS-02-05` | ASIL D | Speed-Scheduled Variable Steering Ratio | [`SWR-CHS-02-12`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-12), [`SWR-CHS-02-13`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-13) | Parking slalom and high-speed lane change proving ground tests |
| `SYS-CHS-02-06` | ASIL D | Dual-Channel Rack Resolver Tracking | [`SWR-CHS-02-14`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-14), [`SWR-CHS-02-15`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-15) | Resolver signal emulator phase shift & noise injection tests |
| `SYS-CHS-02-07` | ASIL D | Dual-Inverter 50/50 Torque Sharing & Current Balance | [`SWR-CHS-02-16`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-16), [`SWR-CHS-02-17`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-17), [`SWR-CHS-02-18`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-18) | Dual-bridge inverter current probe balance validation |
| `SYS-CHS-02-08` | ASIL D | Single-Channel Fault Isolation & 100% Failover | [`SWR-CHS-02-19`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-19), [`SWR-CHS-02-20`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-20), [`SWR-CHS-02-21`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-21) | High-speed MOSFET open-circuit/short-circuit transient test |
| `SYS-CHS-02-09` | ASIL D | Virtual Mechanical End-Stop Simulation | [`SWR-CHS-02-22`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-22), [`SWR-CHS-02-23`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-23) | Handwheel lock-to-lock hard strike robot test stand |
| `SYS-CHS-02-10` | ASIL B | Road Surface Texture & Rumble Strip Haptic Injection | [`SWR-CHS-02-24`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-24), [`SWR-CHS-02-25`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-25) | Cobblestone track and highway rumble strip subjective analysis |
| `SYS-CHS-02-11` | ASIL D | Active Centering & High-Speed Restorative Torque | [`SWR-CHS-02-26`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-26), [`SWR-CHS-02-27`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-27) | Low-speed U-turn handwheel release return test |
| `SYS-CHS-02-12` | ASIL D | Dual 12V/48V Bus Monitoring & Brownout Derating | [`SWR-CHS-02-28`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-28), [`SWR-CHS-02-29`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-29), [`SWR-CHS-02-30`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-30) | Programmable DC power supply voltage sag and ripple injection |
| `SYS-CHS-02-13` | ASIL B | Multi-Zone Actuator & Inverter Thermal Derating | [`SWR-CHS-02-31`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-31), [`SWR-CHS-02-32`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-32) | Thermal chamber continuous high-load steering dyno test |
| `SYS-CHS-02-14` | ASIL D | Dual-Domain E2E CAN-FD & Ethernet Supervision | [`SWR-CHS-02-33`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-33), [`SWR-CHS-02-34`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-34), [`SWR-CHS-02-35`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-35) | Automated CAN-FD error frame and packet corruption injection |
| `SYS-CHS-02-15` | ASIL D | ADAS Request Arbitration & Driver Override Detection | [`SWR-CHS-02-36`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-36), [`SWR-CHS-02-37`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-37), [`SWR-CHS-02-38`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-38) | HIL simulated ADAS trajectory with robot driver intervention |
| `SYS-CHS-02-16` | ASIL D | Unintended Steering Motion Safing & Lockstep Relay | [`SWR-CHS-02-39`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-39), [`SWR-CHS-02-40`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-40), [`SWR-CHS-02-41`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-41) | Microcontroller clock glitching and register corruption test |
| `SYS-CHS-02-17` | ASIL D | Mechanical Rack Jam Detection & Tie-Rod Load Limit | [`SWR-CHS-02-42`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-42), [`SWR-CHS-02-43`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-43) | Physical mechanical rack wedge clamp stall dynamometer test |
| `SYS-CHS-02-18` | ASIL B | Driver Optical, Acoustic & Haptic Warning HMI | [`SWR-CHS-02-44`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-44), [`SWR-CHS-02-45`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-45) | Cluster HMI bus monitor and acoustic decibel verification |
| `SYS-CHS-02-19` | ASIL D | Degraded Safe-Stop Trajectory & Speed Capping | [`SWR-CHS-02-46`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-46), [`SWR-CHS-02-47`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-47), [`SWR-CHS-02-48`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-48) | Complete vehicle proving ground emergency pull-over maneuver |
| `SYS-CHS-02-20` | ASIL B | DEM Diagnostic Management & Freeze-Frame Storage | [`SWR-CHS-02-49`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-49), [`SWR-CHS-02-50`](file:///c:/Workset/AntiGravityProjects/TestOptimisationExperiement/software_requirements/FEAT-CHS-02_SbW_SwReq.md#swr-chs-02-50) | UDS ISO 14229 Service $19 and $14 diagnostic compliance test |
"""

print(f"Generated SysReq length: {len(sys_content)} chars")
with open(sys_path, "w", encoding="utf-8") as f:
    f.write(sys_content)
print("Saved SysReq file successfully.")

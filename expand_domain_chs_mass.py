# -*- coding: utf-8 -*-
"""
Expands Chassis Domain features (FEAT-CHS-01 to FEAT-CHS-08) to 15-20 SYS and 32-50 SWR each.
Complies with ASPICE SYS.2, SYS.3, SWE.1 and ISO 26262:2018 ASIL D / ASIL C.
"""

import features_chs_full

def expand_chs():
    feats = {f["id"]: f for f in features_chs_full.full_chs_features}
    
    # -------------------------------------------------------------------------
    # FEAT-CHS-01: Electronic Stability Control (ESC) [ASIL D] -> 16 SYS, 36 SWR
    # -------------------------------------------------------------------------
    f1 = feats["FEAT-CHS-01"]
    # Existing has 5 SYS, 10 SWR. Let's add SYS-CHS-01-06 to SYS-CHS-01-16 (11 new SYS, 26 new SWR) -> Total 16 SYS, 36 SWR
    existing_sys_ids = {s["id"] for s in f1["sys_reqs"]}
    
    new_sys_f1 = [
        {
            "id": "SYS-CHS-01-06",
            "title": "Traction Control System (TCS) Wheel Slip Acceleration Limiter",
            "asil": "ASIL D",
            "statement": "The System SHALL sample all four wheel speed sensors at 100 Hz, detect excessive driven wheel slip (> 10% relative to vehicle reference speed), and command motor torque reduction in <= 15 ms while applying drive wheel brake intervention.",
            "activation": "Active during vehicle acceleration when drive wheel slip exceeds threshold.",
            "ftti": "30 ms",
            "safe_state": "Zero TCS brake pressure request; restore driver requested torque.",
            "failure_reaction": "If one wheel speed sensor drops out, estimate axle speed from opposite wheel.",
            "inputs": "Wheel_Speed_Ticks_Array[4], Longitudinal_Acceleration_Mps2, Driver_Torque_Demand_Nm",
            "outputs": "TCS_Brake_Pressure_FL_FR_RL_RR_Bar, TCS_Torque_Clamp_Nm",
            "verification": "Low-friction ice track launch acceleration testing according to ISO 14512.",
            "downstream": ["SWR-CHS-01-11", "SWR-CHS-01-12"]
        },
        {
            "id": "SYS-CHS-01-07",
            "title": "Hydraulic Brake Proportioning & Electronic Brakeforce Distribution (EBD)",
            "asil": "ASIL D",
            "statement": "The System SHALL compute dynamic rear-axle brake pressure proportioning based on dynamic axle load transfer, limiting rear caliper pressure to prevent rear wheel lockup prior to front wheel lockup across all vehicle payloads.",
            "activation": "Active on every braking event from 10 km/h to 250 km/h.",
            "ftti": "25 ms",
            "safe_state": "Revert to fixed baseline mechanical hydraulic proportioning curve.",
            "failure_reaction": "If rear pressure sensor faults, cap rear pressure to 65% of front master pressure.",
            "inputs": "Master_Cylinder_Pressure_Bar, Longitudinal_Decel_Mps2, Suspension_Deflection_FL_FR_RL_RR",
            "outputs": "EBD_Max_Rear_Pressure_Limit_Bar, EBD_Rear_Inlet_Valve_Hold_Flag",
            "verification": "FMVSS 135 rear wheel lockup prevention test on high-mu and low-mu surfaces.",
            "downstream": ["SWR-CHS-01-13", "SWR-CHS-01-14"]
        },
        {
            "id": "SYS-CHS-01-08",
            "title": "Anti-Lock Braking System (ABS) High-Frequency Pressure Modulation",
            "asil": "ASIL D",
            "statement": "The System SHALL modulate individual wheel hydraulic caliper pressure between 0 bar and 140 bar at up to 25 Hz modulation frequency when wheel slip exceeds optimal tire friction peak (slip ratio > 15%), maintaining maximum steerability and shortest stopping distance.",
            "activation": "Active during heavy braking when individual wheel deceleration exceeds -12.0 m/s².",
            "ftti": "20 ms",
            "safe_state": "Open all inlet solenoid valves; vent outlet valves to unpressurized reservoir.",
            "failure_reaction": "If wheel solenoid valve sticks closed, open dump circuit to prevent wheel lockup.",
            "inputs": "Individual_Wheel_Slip_Ratio_Array[4], Wheel_Rotational_Decel_Mps2, Master_Pressure_Bar",
            "outputs": "ABS_Valve_Duty_Cycle_FL_FR_RL_RR, ABS_Return_Pump_Motor_Cmd",
            "verification": "ECE R13H Annex 6 ABS performance test on split-mu and transition road surfaces.",
            "downstream": ["SWR-CHS-01-15", "SWR-CHS-01-16"]
        },
        {
            "id": "SYS-CHS-01-09",
            "title": "Hill Start Assist (HSA) & Drive-Off Rollback Suppression",
            "asil": "ASIL B",
            "statement": "The System SHALL hold foundation brake pressure (minimum 25 bar) on uphill inclines (> 3.0% grade) for up to 2000 ms after driver releases the brake pedal, releasing pressure in <= 50 ms once powertrain delivered torque exceeds incline roll resistance.",
            "activation": "Active at standstill (0 km/h) on road grades > 3.0%.",
            "ftti": "100 ms",
            "safe_state": "Release hydraulic hold pressure; illuminate hill-hold indicator.",
            "failure_reaction": "If incline sensor signal is corrupted, engage EPB automatic hold.",
            "inputs": "IMU_Pitch_Angle_Deg, Master_Pressure_Bar, Powertrain_Delivered_Torque_Nm, Gear_Selection_Enum",
            "outputs": "HSA_Brake_Hold_Pressure_Cmd_Bar, HSA_Status_Enum",
            "verification": "15% and 30% incline vehicle launch roll-back distance testing (< 5 cm roll).",
            "downstream": ["SWR-CHS-01-17", "SWR-CHS-01-18"]
        },
        {
            "id": "SYS-CHS-01-10",
            "title": "Hydraulic Brake Fade Compensation (HBFC) Thermal Booster",
            "asil": "ASIL D",
            "statement": "The System SHALL estimate brake rotor temperature via energy dissipation observer: When thermal rotor fade causes deceleration loss (|a_x| < 0.6g at 100 bar master pressure), system SHALL automatically boost hydraulic line pressure by up to +40 bar using ESC return pump.",
            "activation": "Active when estimated brake rotor temperature > 450 °C and pedal pressure is high.",
            "ftti": "40 ms",
            "safe_state": "Zero supplementary hydraulic boost; rely on driver manual pedal force.",
            "failure_reaction": "If pump motor overheats, clamp boost pressure to +15 bar.",
            "inputs": "Master_Pressure_Bar, Vehicle_Decel_Mps2, Brake_Thermal_Energy_Observer_DegC",
            "outputs": "HBFC_Supplementary_Pressure_Bar, Brake_Overheat_Warning_Flag",
            "verification": "AMS brake fade endurance test sequence (10 consecutive 100-0 km/h stops).",
            "downstream": ["SWR-CHS-01-19", "SWR-CHS-01-20"]
        },
        {
            "id": "SYS-CHS-01-11",
            "title": "Trailer Stability Assist (TSA) Snaking Oscillation Damper",
            "asil": "ASIL D",
            "statement": "The System SHALL sample IMU yaw rate at 100 Hz, detect alternating trailer snaking yaw oscillations (frequency 0.8 Hz to 1.5 Hz, yaw rate amplitude > 0.05 rad/s), and apply alternating individual front caliper braking in <= 40 ms to dampen oscillation.",
            "activation": "Active at speeds > 60 km/h when trailer hitch electrical socket is connected.",
            "ftti": "40 ms",
            "safe_state": "Suspend differential braking; apply symmetrical gentle deceleration.",
            "failure_reaction": "If trailer connection signal fluctuates, verify trailer presence via yaw spectrum.",
            "inputs": "IMU_Yaw_Rate_RadS, Trailer_Attached_Flag, Vehicle_Speed_Kmph, Steering_Angle_Deg",
            "outputs": "TSA_Brake_Pressure_FL_FR_Bar, Powertrain_Torque_Damp_Cmd_Nm",
            "verification": "ISO 11555-1 trailer yaw stability dynamic proving ground test.",
            "downstream": ["SWR-CHS-01-21", "SWR-CHS-01-22"]
        },
        {
            "id": "SYS-CHS-01-12",
            "title": "Brake Disc Wiping (BDW) Wet Weather Film Remover",
            "asil": "ASIL B",
            "statement": "The System SHALL detect windshield wiper continuous operation (wiper stage 1 or 2): System SHALL cyclically apply 1.5 bar caliper pressure for 500 ms every 180 seconds to wipe water film from brake discs without inducing noticeable vehicle deceleration (decel < 0.02 m/s²).",
            "activation": "Active at vehicle speeds > 50 km/h while wipers are active.",
            "ftti": "500 ms",
            "safe_state": "Zero wiping pressure; disable BDW function.",
            "failure_reaction": "Inhibit wiping if driver is depressing accelerator pedal > 30%.",
            "inputs": "Windshield_Wiper_State_Enum, Rain_Sensor_Intensity, Vehicle_Speed_Kmph",
            "outputs": "BDW_Caliper_Wiping_Pressure_Bar, BDW_Cycle_Active_Flag",
            "verification": "Wet-weather brake pedal initial response distance test (ISO 21994).",
            "downstream": ["SWR-CHS-01-23", "SWR-CHS-01-24"]
        },
        {
            "id": "SYS-CHS-01-13",
            "title": "Automatic Emergency Braking (AEB) Deceleration Decoupling & Pressure Actuation",
            "asil": "ASIL D",
            "statement": "The System SHALL receive AEB autonomous deceleration demands (up to -9.0 m/s²) over chassis CAN-FD with E2E Profile 5 CRC, building 100 bar hydraulic pressure across all four calipers in <= 150 ms with tracking error <= 3.0 bar.",
            "activation": "Active upon valid E2E-protected AEB trigger frame.",
            "ftti": "25 ms",
            "safe_state": "Release autonomous pressure; transition to driver manual hydraulic pass-through.",
            "failure_reaction": "If CAN-FD communication drops, abort autonomous pressure build within 40 ms.",
            "inputs": "AEB_Decel_Demand_Mps2, AEB_Request_Valid_Flag, Master_Pressure_Bar",
            "outputs": "ESC_Autonomous_Pressure_Cmd_Bar, ESC_Pressure_Build_Active_Flag",
            "verification": "Euro NCAP AEB dynamic track stopping distance verification.",
            "downstream": ["SWR-CHS-01-25", "SWR-CHS-01-26"]
        },
        {
            "id": "SYS-CHS-01-14",
            "title": "Torque Vectoring by Braking (TVB) Agility Enhancer",
            "asil": "ASIL B",
            "statement": "The System SHALL detect high lateral acceleration cornering (a_y > 0.4g, understeer gradient > 1.2): System SHALL apply light hydraulic pressure (5 to 25 bar) to the inside rear wheel in <= 30 ms to induce a yaw moment into the turn without slowing vehicle.",
            "activation": "Active in DRIVE mode during dry high-speed cornering without brake pedal depression.",
            "ftti": "50 ms",
            "safe_state": "Zero TVB inside wheel pressure; maintain neutral open differential.",
            "failure_reaction": "Inhibit TVB if brake rotor temperature exceeds 350 °C.",
            "inputs": "Steering_Angle_Deg, Lateral_Acceleration_Mps2, Vehicle_Speed_Kmph, Accelerator_Pedal_Pct",
            "outputs": "TVB_Inside_Rear_Caliper_Pressure_Bar, TVB_Active_Status_Flag",
            "verification": "Skid-pad steady-state cornering radius and yaw responsiveness evaluation.",
            "downstream": ["SWR-CHS-01-27", "SWR-CHS-01-28"]
        },
        {
            "id": "SYS-CHS-01-15",
            "title": "Electronic Stability Control Watchdog & Core Lockstep Safing Monitor",
            "asil": "ASIL D",
            "statement": "The System SHALL execute continuous hardware watchdog challenge-response and cross-core lockstep ALU comparison at 1000 Hz: If CPU cores diverge or execution flow exceeds 2.0 ms deadline, hardware safing relay SHALL de-energize all 12 hydraulic valves to open state within <= 4.0 ms.",
            "activation": "Active at all times when ECU is powered.",
            "ftti": "10 ms",
            "safe_state": "De-energize all solenoid valves; restore 100% mechanical master cylinder pass-through.",
            "failure_reaction": "Hardware reset and latch unrecoverable safety shutdown until key-off.",
            "inputs": "CPU_Core0_Token, CPU_Core1_Token, Hardware_Watchdog_Heartbeat",
            "outputs": "ESC_Safing_Relay_State, Core_Compare_Fault_Line",
            "verification": "Clock glitching and ALU register bit-flip fault injection testing.",
            "downstream": ["SWR-CHS-01-29", "SWR-CHS-01-30", "SWR-CHS-01-31"]
        },
        {
            "id": "SYS-CHS-01-16",
            "title": "Diagnostic Event Management (DEM) & Hydraulic Valve Stiction Self-Test",
            "asil": "ASIL D",
            "statement": "The System SHALL perform an automated hydraulic valve micro-pulse self-test upon vehicle startup: Measure coil inductive flyback decay current (< 500 µs), confirm zero hydraulic pressure rise, and qualify DTCs with freeze-frame storage in non-volatile memory within <= 50 ms.",
            "activation": "Active at vehicle power-up during ignition ON self-test sequence.",
            "ftti": "100 ms",
            "safe_state": "Inhibit active ESC interventions; latch amber tell-tale on cluster.",
            "failure_reaction": "If valve coil open/short detected, disable affected circuit and record DTC C1020.",
            "inputs": "Solenoid_Coil_Current_ADC_Array[12], Startup_SelfTest_Trigger_Flag",
            "outputs": "Valve_Health_Bitmask, Dem_Event_ESC_Valve_Status",
            "verification": "Automated ISO 14229 UDS diagnostic compliance test bench.",
            "downstream": ["SWR-CHS-01-32", "SWR-CHS-01-33", "SWR-CHS-01-34", "SWR-CHS-01-35", "SWR-CHS-01-36"]
        }
    ]
    
    for s in new_sys_f1:
        if s["id"] not in existing_sys_ids:
            f1["sys_reqs"].append(s)
            
    # Now generate the child SWRs for SWR-CHS-01-11 to SWR-CHS-01-36
    existing_sw_ids = {w["id"] for w in f1["sw_reqs"]}
    
    # We will build software requirements corresponding to each downstream ID
    swr_data_f1 = [
        ("SWR-CHS-01-11", "TCS Driven Wheel Slip Ratio Observer", "SYS-CHS-01-06", "ASIL D", "EscTcsObserver_SWC", "10 ms", "0.8 ms", "Computes driven wheel longitudinal slip ratio: S = (V_wheel - V_ego) / V_ego. Applies deadband filter (2.0%) to reject tire radial vibration."),
        ("SWR-CHS-01-12", "TCS Powertrain Fast Torque Clamp & Caliper Regulator", "SYS-CHS-01-06", "ASIL D", "EscTcsController_SWC", "10 ms", "1.1 ms", "Calculates required torque reduction Delta_T = K_slip * (S - S_target) + D_slip * dS/dt. Transmits fast torque reduction frame to VCU via CAN-FD in <= 10 ms."),
        ("SWR-CHS-01-13", "EBD Dynamic Axle Load Transfer Estimator", "SYS-CHS-01-07", "ASIL D", "EscEbdEstimator_SWC", "10 ms", "0.6 ms", "Calculates instantaneous dynamic front/rear normal loads: Fz_rear = (M_vehicle * g * L_front - M_vehicle * a_x * h_cg) / Wheelbase. Enforces rear normal load threshold."),
        ("SWR-CHS-01-14", "EBD Rear Inlet Valve Pulse Modulator", "SYS-CHS-01-07", "ASIL D", "EscEbdActuator_SWC", "5 ms", "0.4 ms", "Monitors rear wheel slip relative to front wheels: If rear wheel slip exceeds front wheel slip by > 3.0%, pulses rear inlet solenoid valves CLOSED to freeze rear caliper pressure."),
        ("SWR-CHS-01-15", "ABS 5-Phase Wheel State Machine Logic", "SYS-CHS-01-08", "ASIL D", "EscAbsStateMachine_SWC", "5 ms", "0.9 ms", "Implements 5-phase ABS regulation cycle: Phase 0 (Apply), Phase 1 (Hold), Phase 2 (Fast Dump), Phase 3 (Slow Dump), Phase 4 (Staircase Pulse Re-apply) based on wheel acceleration thresholds."),
        ("SWR-CHS-01-16", "ABS Hydraulic Return Pump DC Motor Driver", "SYS-CHS-01-08", "ASIL D", "EscAbsPumpDriver_SWC", "5 ms", "0.3 ms", "Commands brushless DC hydraulic return pump motor to maximum speed during ABS pressure dump phases to evacuate brake fluid from low-pressure accumulators back to master cylinder."),
        ("SWR-CHS-01-17", "HSA Road Incline & Static Roll-Back Resistance Evaluator", "SYS-CHS-01-09", "ASIL B", "EscHsaEstimator_SWC", "10 ms", "0.4 ms", "Computes gravity roll-back force: F_roll = M_vehicle * g * sin(Theta_pitch). Computes minimum hydraulic caliper pressure required to overcome roll-back: P_hold = F_roll / (Caliper_Area * Eff)."),
        ("SWR-CHS-01-18", "HSA Smooth Drive-Off Pressure Ramp-Down Governor", "SYS-CHS-01-09", "ASIL B", "EscHsaRelease_SWC", "10 ms", "0.5 ms", "Monitors motor delivered drive torque: When delivered motor torque matches F_roll * Wheel_Radius, ramps hydraulic hold pressure to 0 bar at a controlled rate of 80 bar/s to prevent jerky launch."),
        ("SWR-CHS-01-19", "HBFC Brake Rotor Lumped-Capacitance Thermal Observer", "SYS-CHS-01-10", "ASIL D", "EscHbfcObserver_SWC", "100 ms", "0.5 ms", "Calculates accumulated thermal energy: Q_in = int(P_brake * v_ego * dT). Subtracts convective cooling Q_out = h_conv(v_ego) * (T_rotor - T_ambient). Flags brake fade if T_rotor > 450 °C."),
        ("SWR-CHS-01-20", "HBFC Supplementary Hydraulic Boost Dispatcher", "SYS-CHS-01-10", "ASIL D", "EscHbfcActuator_SWC", "10 ms", "0.7 ms", "When brake fade is active and pedal force is applied, activates hydraulic pump to boost caliper pressure by up to +40 bar above master cylinder pressure to restore expected vehicle deceleration."),
        ("SWR-CHS-01-21", "TSA Trailer Yaw Oscillation Spectral Analyzer", "SYS-CHS-01-11", "ASIL D", "EscTsaDetector_SWC", "10 ms", "0.8 ms", "Applies bandpass filter (0.5 Hz - 2.0 Hz) to IMU yaw rate signal. Computes moving Fourier energy: If peak energy in 0.8-1.5 Hz exceeds threshold for 3 full cycles, confirms trailer snaking oscillation."),
        ("SWR-CHS-01-22", "TSA Anti-Snaking Differential Caliper Pulse Controller", "SYS-CHS-01-11", "ASIL D", "EscTsaActuator_SWC", "10 ms", "0.9 ms", "Applies out-of-phase differential braking pulses (+-25 bar) to front left/right calipers alternating with yaw oscillation period, combined with gentle 50% engine torque cut, restoring trailer alignment."),
        ("SWR-CHS-01-23", "BDW Wiper Signal Debouncer & Speed Threshold Gate", "SYS-CHS-01-12", "ASIL B", "EscBdwSupervisor_SWC", "100 ms", "0.2 ms", "Debounces wiper active signals over CAN-FD: Confirms continuous wiper operation for > 10 seconds and vehicle speed > 50 km/h before issuing cyclic wiping trigger tokens."),
        ("SWR-CHS-01-24", "BDW Low-Pressure Micro-Wipe Pulse Regulator", "SYS-CHS-01-12", "ASIL B", "EscBdwActuator_SWC", "10 ms", "0.3 ms", "Executes gentle 1.5 bar hydraulic caliper pressure apply for exactly 500 ms across all 4 wheels. Monitors wheel speed difference to ensure vehicle speed does not drop by > 0.05 km/h during wipe."),
        ("SWR-CHS-01-25", "ESC AEB Deceleration Target Pressure Convertor", "SYS-CHS-01-13", "ASIL D", "EscAebInterface_SWC", "5 ms", "0.5 ms", "Converts external AEB target deceleration request (m/s²) into required caliper pressure using vehicle mass, tire rolling radius, and brake caliper torque factor: P_target = (a_target * M * R) / (4 * K_brake)."),
        ("SWR-CHS-01-26", "ESC AEB Pre-Fill High-Speed Pressure Commander", "SYS-CHS-01-13", "ASIL D", "EscAebActuator_SWC", "2 ms", "0.4 ms", "Upon receiving early AEB prefill warning, applies 4.0 bar pressure in <= 30 ms to eliminate caliper pad clearance gap, reducing subsequent full braking response time by 80 ms."),
        ("SWR-CHS-01-27", "TVB Lateral G & Understeer Gradient Monitor", "SYS-CHS-01-14", "ASIL B", "EscTvbMonitor_SWC", "10 ms", "0.6 ms", "Calculates instantaneous understeer angle: Delta_understeer = Steering_Angle - L * Yaw_Rate / v_ego. If Delta_understeer > 2.0° and lateral acceleration > 0.4g, arms torque vectoring braking."),
        ("SWR-CHS-01-28", "TVB Inside Rear Wheel Caliper Pressure Modulator", "SYS-CHS-01-14", "ASIL B", "EscTvbActuator_SWC", "10 ms", "0.5 ms", "Commands inside rear caliper inlet valve to modulate pressure between 5 and 25 bar proportionally to understeer angle, inducing restorative yaw moment while compensating powertrain torque."),
        ("SWR-CHS-01-29", "ESC Dual Lockstep Core Token Comparator", "SYS-CHS-01-15", "ASIL D", "EscCoreSupervisor_SWC", "1 ms", "0.15 ms", "Compares execution tokens generated by Core 0 and Core 1 at every 1 ms cycle. If token CRC differs, halts instruction execution and asserts Core_Compare_Fault_Line to hardware safing chip."),
        ("SWR-CHS-01-30", "ESC Program Flow Deadline & Execution Budget Guard", "SYS-CHS-01-15", "ASIL D", "EscWdgMonitor_SWC", "1 ms", "0.15 ms", "Implements AUTOSAR WdgM checkpoint monitoring across all critical control runnables: If any runnable exceeds 2.0 ms execution budget, triggers watchdog reset."),
        ("SWR-CHS-01-31", "ESC Hardware Safing Solenoid Power Cut Relay Driver", "SYS-CHS-01-15", "ASIL D", "EscSafingRelay_SWC", "1 ms", "0.1 ms", "Controls high-side power MOSFET switch supplying 12V to all hydraulic solenoid valve coils: Inverts gate drive within <= 2.0 ms upon any hardware safing fault."),
        ("SWR-CHS-01-32", "ESC Solenoid Coil Inductive Decay Pulse Evaluator", "SYS-CHS-01-16", "ASIL D", "EscValveDiag_SWC", "10 ms", "0.4 ms", "Applies 200 µs test voltage pulse to each valve coil during power-on self test, reads ADC current decay curve, and checks coil inductance (L in 8.0 mH - 14.0 mH) and resistance (R in 6.0 - 9.0 Ohm)."),
        ("SWR-CHS-01-33", "ESC Pressure Sensor Plausibility & Drift Monitor", "SYS-CHS-01-16", "ASIL D", "EscPressureDiag_SWC", "10 ms", "0.4 ms", "Monitors master cylinder and caliper pressure sensor readings at zero pedal apply: If sensor offset exceeds +-1.5 bar for > 500 ms, flags DEM_EVENT_PRESSURE_SENSOR_DRIFT."),
        ("SWR-CHS-01-34", "ESC Wheel Speed Sensor Signal Edge & Air Gap Monitor", "SYS-CHS-01-16", "ASIL D", "EscWheelSpeedDiag_SWC", "10 ms", "0.5 ms", "Monitors magnetic encoder pulse duty cycle and amplitude: If wheel speed amplitude drops below 2.5 mA (hall sensor air gap expansion > 1.8 mm), reports DTC C1015."),
        ("SWR-CHS-01-35", "ESC UDS Diagnostic Freeze-Frame Recorder", "SYS-CHS-01-16", "ASIL D", "EscFreezeFrame_SWC", "10 ms", "0.6 ms", "Captures 64-byte diagnostic freeze-frame snapshot (Vehicle Speed, Yaw Rate, Master Pressure, Lateral Accel, Steering Angle, DTC ID) and writes to EEPROM upon any ASIL D fault."),
        ("SWR-CHS-01-36", "ESC Tell-Tale Lamp & Cluster Warning Dispatcher", "SYS-CHS-01-16", "ASIL B", "EscHmiAlert_SWC", "20 ms", "0.3 ms", "Serializes ESC operational status and intervention state over CAN-FD: Commands flashing amber ESC icon during active intervention, solid amber on fault, and chime prompt on complete shutdown.")
    ]
    
    for sw_id, title, parent, asil, swc, period, wcet, algo in swr_data_f1:
        if sw_id not in existing_sw_ids:
            f1["sw_reqs"].append({
                "id": sw_id,
                "title": title,
                "parent": parent,
                "asil": asil,
                "swc": swc,
                "period": period,
                "wcet": wcet,
                "activation": f"Executed cyclically every {period}.",
                "algorithm": algo,
                "safety_mechanism": "Range limit, plausibility checks, and Dem diagnostic reporting.",
                "failure_reaction": "Default to safe state and log DEM fault code.",
                "inputs": "Sensor readings and vehicle state data via RTE.",
                "outputs": "Control commands and diagnostic flags via RTE.",
                "verification": "HiL test bench automated pass/fail verification."
            })
            
    print(f"FEAT-CHS-01 updated: {len(f1['sys_reqs'])} SYS, {len(f1['sw_reqs'])} SWR.")

if __name__ == "__main__":
    expand_chs()

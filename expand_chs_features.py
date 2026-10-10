# expand_chs_features.py
import features_chs_full

old_feats = {f["id"]: f for f in features_chs_full.full_chs_features}

# FEAT-CHS-01: ESC (Expanded to 5 sys reqs, 10 sw reqs)
f1 = old_feats["FEAT-CHS-01"]
f1["sys_reqs"].extend([
    {
        "id": "SYS-CHS-01-03",
        "title": "Split-Mu Low-Friction Differential Braking & Steer-Correction",
        "asil": "ASIL D",
        "statement": "The System SHALL detect split-friction road surfaces (e.g. ice on right wheels, dry asphalt on left wheels during braking), commanding asymmetric caliper pressure and electric power steering counter-torque (+-2.5 Nm) in <= 30 ms to prevent vehicle swerving.",
        "activation": "Active during emergency braking when friction difference |Delta_mu| > 0.3.",
        "ftti": "30 ms",
        "safe_state": "Symmetrize braking pressures; zero EPS counter-steering torque.",
        "failure_reaction": "If EPS communication drops, reduce braking pressure on high-friction wheels to preserve directional stability.",
        "inputs": "Wheel_Speed_Ticks_Array[4], Master_Cylinder_Pressure_Bar, EPS_Actual_Torque_Nm",
        "outputs": "Split_Mu_Pressure_FL_FR_RL_RR_Bar, EPS_Counter_Steer_Demand_Nm",
        "verification": "FMVSS 126 split-mu braking track testing at 80 km/h.",
        "downstream": ["SWR-CHS-01-05", "SWR-CHS-01-06"]
    },
    {
        "id": "SYS-CHS-01-04",
        "title": "Active Rollover Mitigation (ARM) & Tripping Prevention",
        "asil": "ASIL D",
        "statement": "The System SHALL sample 6-DOF IMU roll rate (p_roll) and lateral acceleration (a_y) at 100 Hz: If estimated wheel lift is detected, system SHALL build 80 bar braking pressure on outer front wheel in <= 80 ms while clamping powertrain torque to zero to mitigate rollover.",
        "activation": "Active when vehicle speed > 30 km/h and roll risk index > 0.8.",
        "ftti": "40 ms",
        "safe_state": "Release brake pressure once roll angle drops below 3.0 degrees.",
        "failure_reaction": "If IMU roll gyro faults, estimate roll risk from lateral acceleration and steering angle.",
        "inputs": "IMU_Roll_Rate_RadS, IMU_Lateral_Accel_Mps2, Suspension_Deflection_Array[4]",
        "outputs": "ARM_Intervention_Pressure_OuterFront_Bar, Powertrain_Torque_Kill_Cmd",
        "verification": "NHTSA Fishhook maneuver dynamic rollover stability tests.",
        "downstream": ["SWR-CHS-01-07", "SWR-CHS-01-08"]
    },
    {
        "id": "SYS-CHS-01-05",
        "title": "Emergency Hydraulic Brake Assist (HBA) Dynamic Pressure Booster",
        "asil": "ASIL D",
        "statement": "The System SHALL detect panic braking (pedal travel rate d(pedal)/dt > 300 %/s or pressure rise dP/dt > 200 bar/s) and automatically override driver pedal force to command full ABS lock-limit pressure (120 bar) in <= 60 ms.",
        "activation": "Active at speeds > 10 km/h upon panic brake depression.",
        "ftti": "30 ms",
        "safe_state": "Rely on driver manual physical hydraulic master cylinder pressure.",
        "failure_reaction": "Release booster override immediately when driver releases brake pedal.",
        "inputs": "Brake_Pedal_Depression_Rate_Pct_S, Master_Cylinder_Pressure_Rise_Bar_S",
        "outputs": "HBA_Full_Pressure_Boost_Cmd (boolean), Caliper_Pressure_Boost_Bar",
        "verification": "ECE R13H Brake Assist System emergency stopping distance verification.",
        "downstream": ["SWR-CHS-01-09", "SWR-CHS-01-10"]
    }
])
f1["sw_reqs"].extend([
    {
        "id": "SWR-CHS-01-05",
        "title": "Split-Mu Yaw Disturbance Moment Dynamic Observer",
        "parent": "SYS-CHS-01-03",
        "asil": "ASIL D",
        "swc": "EscSplitMuObserver_SWC",
        "period": "10 ms",
        "wcet": "0.6 ms",
        "activation": "Executed during braking.",
        "algorithm": "Estimates yaw disturbance moment induced by split friction: M_disturb = (F_x_left - F_x_right) * Track_Width / 2. Calculates restorative EPS counter-steering angle demand: Delta_steer = -K_split * M_disturb / (v_ego + 5.0).",
        "safety_mechanism": "Counter-steer torque limiter: Capped to maximum +-2.5 Nm to prevent snatching wheel from driver.",
        "failure_reaction": "Zero counter-steer demand if vehicle yaw rate opposes disturbance.",
        "inputs": "Wheel_Acceleration_FL_FR_RL_RR, Master_Pressure_Bar, Steering_Angle_Deg",
        "outputs": "Split_Mu_Yaw_Moment_Nm, Restorative_Steering_Torque_Nm",
        "verification": "Skidpad split-friction braking simulation with ice/concrete interface."
    },
    {
        "id": "SWR-CHS-01-06",
        "title": "High-Friction Caliper Pressure Gradient Regulator",
        "parent": "SYS-CHS-01-03",
        "asil": "ASIL D",
        "swc": "EscSplitMuBraker_SWC",
        "period": "10 ms",
        "wcet": "0.4 ms",
        "activation": "Active during split-mu braking.",
        "algorithm": "Modulates high-friction caliper pressure rise rate: Limits dP_high/dt to <= 120 bar/s to give driver time to react with steering before full yaw moment develops. Ramps to full braking as vehicle yaw stabilizes.",
        "safety_mechanism": "Stopping distance preservation: If vehicle heading deviation < 1.0 deg, allows full braking.",
        "failure_reaction": "Default to standard ABS pressure modulation if gradient controller faults.",
        "inputs": "Restorative_Steering_Torque_Nm, Driver_Handwheel_Angle_Deg",
        "outputs": "Target_HighMu_Caliper_Pressure_Bar, Gradient_Limiter_Active_Flag",
        "verification": "Straight-line split-mu stop distance and heading drift evaluation."
    },
    {
        "id": "SWR-CHS-01-07",
        "title": "Multi-Sensor Roll Angle & Wheel Lift Probability Estimator",
        "parent": "SYS-CHS-01-04",
        "asil": "ASIL D",
        "swc": "EscRollEstimator_SWC",
        "period": "10 ms",
        "wcet": "0.7 ms",
        "activation": "Cyclic 10 ms task.",
        "algorithm": "Integrates IMU roll rate p and lateral acceleration a_y via complementary filter: Phi_roll = (1 - alpha)*(Phi_prev + p*dT) + alpha * (a_y / g). Calculates Roll Energy index: E_roll = 0.5 * J_xx * p^2 + m * g * h_cg * (1 - cos(Phi)). Flags wheel lift if E_roll > 0.8 * E_crit.",
        "safety_mechanism": "Sensor redundancy check: Compares integrated roll angle against suspension height sensor differential.",
        "failure_reaction": "Inhibit ARM intervention if vehicle is on steep banked curve (speedway track).",
        "inputs": "IMU_Roll_Rate_RadS, IMU_Lateral_Accel_Mps2, Suspension_Height_Diff_FL_FR",
        "outputs": "Estimated_Vehicle_Roll_Angle_Rad, Wheel_Lift_Risk_Probability",
        "verification": "Fishhook dynamic maneuver testing on ISO 7401 vehicle dynamics bench."
    },
    {
        "id": "SWR-CHS-01-08",
        "title": "Outer Front Caliper Fast Hydraulic Pressurizer & Torque Cut",
        "parent": "SYS-CHS-01-04",
        "asil": "ASIL D",
        "swc": "EscArmActuator_SWC",
        "period": "5 ms",
        "wcet": "0.3 ms",
        "activation": "Triggered when Wheel_Lift_Risk_Probability > 0.85.",
        "algorithm": "Immediately commands ESC hydraulic return pump: Pressurizes outer front brake caliper to 80 bar in <= 80 ms to induce stabilizing understeer and drop lateral G. Broadcasts zero-torque demand to powertrain.",
        "safety_mechanism": "Pulse duration limiter: Clamps maximum ARM brake pulse to <= 1200 ms.",
        "failure_reaction": "Release brake pressure once lateral acceleration drops below 0.6g.",
        "inputs": "Wheel_Lift_Risk_Probability, Outer_Front_Wheel_Enum",
        "outputs": "ARM_Brake_Command_Bar, VCU_Torque_Override_Zero_Req (boolean)",
        "verification": "Proving ground dynamic rollover limit tests with outrigger wheels."
    },
    {
        "id": "SWR-CHS-01-09",
        "title": "Driver Panic Brake Depression Velocity Gradient Detector",
        "parent": "SYS-CHS-01-05",
        "asil": "ASIL D",
        "swc": "EscHbaDetector_SWC",
        "period": "5 ms",
        "wcet": "0.2 ms",
        "activation": "Continuous pedal monitoring.",
        "algorithm": "Calculates pedal depression speed: v_pedal = (Travel[k] - Travel[k-1]) / dT. If v_pedal > 300 %/s AND Master_Pressure > 15 bar within 80 ms, confirms panic emergency stop condition.",
        "safety_mechanism": "Threshold speed adaptation: Lowers threshold from 300 %/s to 200 %/s at highway speeds (> 100 km/h).",
        "failure_reaction": "Ignore HBA if accelerator pedal is simultaneously depressed.",
        "inputs": "Brake_Pedal_Travel_Pct, Master_Cylinder_Pressure_Bar, Vehicle_Speed_Kmph",
        "outputs": "Panic_Braking_Detected_Flag (boolean), HBA_Trigger_Timestamp",
        "verification": "Pedal robot dynamic impact testing measuring gradient detection latency."
    },
    {
        "id": "SWR-CHS-01-10",
        "title": "Electronic Brake Booster Full Lock-Limit Pressure Commander",
        "parent": "SYS-CHS-01-05",
        "asil": "ASIL D",
        "swc": "EscHbaActuator_SWC",
        "period": "5 ms",
        "wcet": "0.3 ms",
        "activation": "Active upon Panic_Braking_Detected_Flag.",
        "algorithm": "Overrides driver manual pedal effort: Commands electric booster motor to maximum force, delivering 120 bar hydraulic line pressure to all 4 calipers in <= 60 ms. Transitions seamlessly to ABS slip regulation.",
        "safety_mechanism": "Driver release override: If master cylinder pressure drops below 8 bar (driver removes foot), cancels HBA instantly.",
        "failure_reaction": "Revert to standard base hydraulic assist upon booster motor overtemperature.",
        "inputs": "Panic_Braking_Detected_Flag, Driver_Master_Pressure_Bar, ABS_Active_Status",
        "outputs": "HBA_Boosted_Pressure_Cmd_Bar, HBA_Active_State_Enum",
        "verification": "Stopping distance reduction verification according to ECE R13H Annex 9."
    }
])

# FEAT-CHS-02: SbW (Expanded to 4 sys reqs, 8 sw reqs)
f2 = old_feats["FEAT-CHS-02"]
f2["sys_reqs"].extend([
    {
        "id": "SYS-CHS-02-03",
        "title": "Force Feedback Handwheel Road-Feel & Aligning Torque Synthesizer",
        "asil": "ASIL D",
        "statement": "The System SHALL drive a brushless force-feedback torque actuator on the steering wheel column to synthesize realistic road feel (delivering up to +-8.0 Nm aligning torque at 1 kHz) based on tire lateral forces, road friction, and vehicle speed.",
        "activation": "Active at all times when SbW is active.",
        "ftti": "15 ms",
        "safe_state": "Limit force feedback torque to neutral centering spring mode (K = 1.0 Nm/deg).",
        "failure_reaction": "If force feedback motor overheats, clamp maximum feedback torque to 2.5 Nm.",
        "inputs": "Rack_Tie_Rod_Lateral_Force_kN, Vehicle_Velocity_Mps, Front_Tire_Sideslip_Rad",
        "outputs": "Handwheel_Torque_Demand_Nm, Handwheel_Damping_Factor",
        "verification": "Subjective steering feel evaluation on skidpad and rough Belgian block cobblestone tracks.",
        "downstream": ["SWR-CHS-02-05", "SWR-CHS-02-06"]
    },
    {
        "id": "SYS-CHS-02-04",
        "title": "Speed-Dependent Variable Steering Ratio & Parking Lockouts",
        "asil": "ASIL D",
        "statement": "The System SHALL compute dynamic steering gear ratio: Varying from ultra-direct 8:1 at parking speeds (< 15 km/h, requiring only +-170 deg lock-to-lock without hand-over-hand turning) to stable 16:1 at highway speeds (> 120 km/h).",
        "activation": "Active throughout vehicle motion.",
        "ftti": "20 ms",
        "safe_state": "Lock steering ratio to fixed mechanical baseline 13.5:1.",
        "failure_reaction": "If vehicle speed signal is lost, freeze ratio at safe intermediate 14:1.",
        "inputs": "Voted_Handwheel_Angle_Deg, Vehicle_Velocity_Kmph",
        "outputs": "Target_Road_Wheel_Angle_Demand_Deg, Active_Steering_Ratio_Value",
        "verification": "Lock-to-lock steering angle validation in low-speed slaloms and high-speed lane changes.",
        "downstream": ["SWR-CHS-02-07", "SWR-CHS-02-08"]
    }
])
f2["sw_reqs"].extend([
    {
        "id": "SWR-CHS-02-05",
        "title": "Tire Aligning Moment Observer & Brushless Handwheel Motor FOC Driver",
        "parent": "SYS-CHS-02-03",
        "asil": "ASIL D",
        "swc": "SbwRoadFeelSynthesizer_SWC",
        "period": "1 ms",
        "wcet": "0.25 ms",
        "activation": "Executed in 1 kHz high-speed motor ISR.",
        "algorithm": "Estimates self-aligning torque M_z using brush tire model: M_z = F_y * (n_trail + n_pneumatic). Generates handwheel torque: T_hw = (M_z / Ratio) * K_boost(v) + D_damping * Omega_hw. Drives brushless motor via FOC quadrature current I_q.",
        "safety_mechanism": "Handwheel torque clamp: Hardware torque limiter cuts power if commanded torque > 9.5 Nm.",
        "failure_reaction": "Switch to passive centering spring if rack force sensors fail.",
        "inputs": "Rack_Axial_Force_Sensor_kN, Handwheel_Angular_Velocity_RadS, Ego_Speed_Mps",
        "outputs": "Handwheel_Motor_Iq_Cmd_A, Synthesized_Aligning_Torque_Nm",
        "verification": "HIL steering test bench road texture frequency response analysis (0 to 50 Hz)."
    },
    {
        "id": "SWR-CHS-02-06",
        "title": "Road Surface Texture & Rumble Strip Haptic Feedback Injector",
        "parent": "SYS-CHS-02-03",
        "asil": "ASIL B",
        "swc": "SbwHapticInjector_SWC",
        "period": "2 ms",
        "wcet": "0.2 ms",
        "activation": "Active when driving over rough road surfaces.",
        "algorithm": "Extracts high-frequency rack acceleration signals (15-40 Hz): Injects proportional micro-vibration torque pulses (+-0.4 Nm @ 25 Hz) into handwheel motor to replicate authentic tactile feedback of road surface textures, potholes, and highway rumble strips.",
        "safety_mechanism": "Bandpass filter clamps vibration amplitude to <= 0.8 Nm to prevent driver hand fatigue.",
        "failure_reaction": "Disable haptic injection if rack accelerometer signal is saturated.",
        "inputs": "Rack_Vibration_Accelerometer_Z, Camera_Rumble_Strip_Marker_Flag",
        "outputs": "Haptic_Texture_Torque_Pulse_Nm, Surface_Roughness_Index",
        "verification": "Cobblestone and highway rumble strip tactile fidelity test bench verification."
    },
    {
        "id": "SWR-CHS-02-07",
        "title": "Speed-Scheduled Variable Steering Ratio Look-Up Generator",
        "parent": "SYS-CHS-02-04",
        "asil": "ASIL D",
        "swc": "SbwVariableRatio_SWC",
        "period": "10 ms",
        "wcet": "0.3 ms",
        "activation": "Cyclic 10 ms task.",
        "algorithm": "Computes variable ratio R_gear(v) = R_low + (R_high - R_low) / (1 + exp(-(v - v_mid)/K_steep)). At 0 km/h: R=8.5:1. At 120 km/h: R=15.8:1. Calculates target wheel angle: Delta_wheel = Theta_handwheel / R_gear(v).",
        "safety_mechanism": "Ratio gradient limiter: Rate of ratio change clamped to <= 0.5 ratio units per second.",
        "failure_reaction": "Default to fixed 13.5:1 ratio if vehicle speed drops to zero erratically.",
        "inputs": "Filtered_Vehicle_Speed_Kmph, Voted_Handwheel_Angle_Deg",
        "outputs": "Instantaneous_Steering_Ratio, Target_Road_Wheel_Angle_Deg",
        "verification": "Continuous steering ratio curve verification across 0 to 200 km/h."
    },
    {
        "id": "SWR-CHS-02-08",
        "title": "End-Stop Virtual Mechanical Lockout Soft-Bump Simulator",
        "parent": "SYS-CHS-02-04",
        "asil": "ASIL D",
        "swc": "SbwVirtualEndStop_SWC",
        "period": "1 ms",
        "wcet": "0.15 ms",
        "activation": "Executed when handwheel approaches lock angle.",
        "algorithm": "Simulates physical steering rack mechanical end-stop: When handwheel angle |Theta| approaches lock threshold (e.g. 175 deg at low speed), commands handwheel motor to deliver steep counter-torque spring barrier (K_stop = 15 Nm/deg) stopping driver handwheel motion.",
        "safety_mechanism": "Motor thermal overload guard: If driver holds handwheel against virtual end-stop > 5s, drops torque to 5 Nm.",
        "failure_reaction": "Limit maximum rack travel in software if handwheel bypasses virtual barrier.",
        "inputs": "Voted_Handwheel_Angle_Deg, Handwheel_Angular_Velocity_RadS",
        "outputs": "EndStop_Resistance_Torque_Nm, EndStop_Engaged_Flag (boolean)",
        "verification": "Handwheel lock-to-lock virtual stop impact feel and stiffness bench test."
    }
])

# FEAT-CHS-03: BbW (Expanded to 4 sys reqs, 8 sw reqs)
f3 = old_feats["FEAT-CHS-03"]
f3["sys_reqs"].extend([
    {
        "id": "SYS-CHS-03-03",
        "title": "Decoupled Hydraulic Pedal Feel Emulator & Force-Travel Curve",
        "asil": "ASIL D",
        "statement": "The System SHALL decouple brake pedal mechanically from wheel calipers in normal mode: Driving a spring-loaded hydraulic simulator cylinder to deliver progressive non-linear pedal feel (0 to 60 mm travel with 500 N force @ 60 mm) independent of regenerative braking.",
        "activation": "Active at all times when BbW system is energized.",
        "ftti": "20 ms",
        "safe_state": "Open mechanical bypass valve; couple pedal directly to master cylinder (100% passive fallback).",
        "failure_reaction": "If pedal emulator valve leaks, open fallback bypass in <= 20 ms.",
        "inputs": "Brake_Pedal_Force_Sensor_N, Brake_Pedal_Travel_Mm, Emulator_Chamber_Pressure_Bar",
        "outputs": "Emulator_Solenoid_Valve_State, Decoupled_Pedal_Active_Flag",
        "verification": "Pedal force-travel characteristic hysteresis curve test according to FMVSS 135.",
        "downstream": ["SWR-CHS-03-05", "SWR-CHS-03-06"]
    },
    {
        "id": "SYS-CHS-03-04",
        "title": "Passive Mechanical Fallback Hydraulic Valve & Dual Circuit Isolation",
        "asil": "ASIL D",
        "statement": "The System SHALL feature normally-open spring-return hydraulic isolation valves: Upon complete electrical power loss (12V cut) or dual micro crash, valves SHALL de-energize within <= 15 ms, reconnecting driver pedal mechanically to front wheel calipers to guarantee >= 0.44g deceleration (ECE R13H fallback requirement).",
        "activation": "Continuous passive safety architecture.",
        "ftti": "15 ms",
        "safe_state": "Mechanical hydraulic circuit closed; zero electronics required for braking.",
        "failure_reaction": "Maintain manual brake pass-through if primary boost cylinder fails.",
        "inputs": "Dual_12V_Power_Good_Signals, Microcontroller_Heartbeat_Line",
        "outputs": "Normally_Open_Isolation_Valve_State, Failsafe_Hydraulic_Connected_Flag",
        "verification": "Total electrical disconnect stopping distance test on FMVSS 135 proving ground."
        ,"downstream": ["SWR-CHS-03-07", "SWR-CHS-03-08"]
    }
])
f3["sw_reqs"].extend([
    {
        "id": "SWR-CHS-03-05",
        "title": "Non-Linear Pedal Force-Travel Characteristic Curve Mapper",
        "parent": "SYS-CHS-03-03",
        "asil": "ASIL D",
        "swc": "BbwPedalFeel_SWC",
        "period": "5 ms",
        "wcet": "0.3 ms",
        "activation": "Active during pedal depression.",
        "algorithm": "Maps pedal travel s to target driver deceleration request: a_req = K_initial * s for s < 15 mm (soft bite point); a_req = K_mid * s^1.8 for 15 mm <= s <= 45 mm (linear modulation zone); a_req = -10.0 m/s² for s > 50 mm (panic stop).",
        "safety_mechanism": "Redundant force-travel cross check: Discards travel reading if measured force is zero.",
        "failure_reaction": "Default to pure force-based deceleration mapping if travel sensor faults.",
        "inputs": "Pedal_Travel_Sensor_Mm, Pedal_Force_Sensor_N, Vehicle_Speed_Mps",
        "outputs": "Driver_Demanded_Deceleration_Mps2, Pedal_Displacement_Zone_Enum",
        "verification": "Automated pedal robot repeatability test across 10,000 brake cycles."
    },
    {
        "id": "SWR-CHS-03-06",
        "title": "Hydraulic Pedal Simulator Damping & Return Hysteresis Modulator",
        "parent": "SYS-CHS-03-03",
        "asil": "ASIL B",
        "swc": "BbwSimulatorDamping_SWC",
        "period": "10 ms",
        "wcet": "0.3 ms",
        "activation": "Active during pedal motion.",
        "algorithm": "Modulates hydraulic orifice restrictor valve in simulator cylinder: Delivers 15% hysteresis between push and release cycles to mimic physical brake fluid viscous friction, preventing pedal bounce during fast release.",
        "safety_mechanism": "Simulator pressure relief valve opens mechanically at 80 bar to protect seals.",
        "failure_reaction": "Open restrictor valve fully if coil current fluctuates.",
        "inputs": "Pedal_Travel_Velocity_Mm_S, Simulator_Fluid_Temp_DegC",
        "outputs": "Simulator_Orifice_PWM_Duty, Return_Damping_Active_Flag",
        "verification": "Brake pedal subjective release feel and acoustic NVH testing."
    },
    {
        "id": "SWR-CHS-03-07",
        "title": "Normally-Open Fallback Hydraulic Solenoid Valve Driver",
        "parent": "SYS-CHS-03-04",
        "asil": "ASIL D",
        "swc": "BbwFallbackDriver_SWC",
        "period": "1 ms",
        "wcet": "0.15 ms",
        "activation": "Executed in 1 kHz supervisory ISR.",
        "algorithm": "Continuously powers normally-open isolation valves to keep mechanical pushrod decoupled during normal drive-by-wire operation. Upon hardware fault signal or watchdog trip, cuts gate drive in <= 3 ms, allowing internal spring to snap valve open.",
        "safety_mechanism": "Hardware pull-down: De-energizes coil automatically if microcontroller resets.",
        "failure_reaction": "Latch fallback state and prohibit re-engagement until complete key cycle.",
        "inputs": "Watchdog_Heartbeat_Status, Hardware_Fault_Trip_Bit, 12V_Supply_Rail_ADC",
        "outputs": "Isolation_Valve_Coil_Drive_Pin, Mechanical_PassThrough_Active_Flag",
        "verification": "Power cut-off valve de-energization response time testing (< 5 ms)."
    },
    {
        "id": "SWR-CHS-03-08",
        "title": "Dual-Circuit Hydraulic Brake Balance & Splitter Supervisor",
        "parent": "SYS-CHS-03-04",
        "asil": "ASIL D",
        "swc": "BbwCircuitSupervisor_SWC",
        "period": "5 ms",
        "wcet": "0.3 ms",
        "activation": "Supervises hydraulic circuit integrity.",
        "algorithm": "Monitors primary (Front) and secondary (Rear) circuit pressures: P_front vs P_rear. If one circuit leaks (pressure < 5 bar while booster pumping), isolates leaky circuit via shuttle valve and maintains 100% braking on intact axle.",
        "safety_mechanism": "Brake fluid level reservoir reed switch read every 10 ms.",
        "failure_reaction": "Set DTC C1102 (Brake Hydraulic Circuit Leak) and illuminate red Master Brake tell-tale.",
        "inputs": "Pressure_Sensor_Circuit_A_Bar, Pressure_Sensor_Circuit_B_Bar, Fluid_Reservoir_Level_Switch",
        "outputs": "Hydraulic_Circuit_Isolated_Mask, Brake_Fluid_Low_Warning_Flag",
        "verification": "Intentional hydraulic line puncture test on high-speed proving ground."
    }
])

all_chs = [f1, f2, f3, old_feats["FEAT-CHS-04"], old_feats["FEAT-CHS-05"], old_feats["FEAT-CHS-06"], old_feats["FEAT-CHS-07"], old_feats["FEAT-CHS-08"]]

print(f"Total Chassis features compiled: {len(all_chs)}")
total_sys = sum(len(f['sys_reqs']) for f in all_chs)
total_sw = sum(len(f['sw_reqs']) for f in all_chs)
print(f"Total Chassis SysReqs: {total_sys}, Total Chassis SwReqs: {total_sw}")

code = "# Complete Vehicle Motion & Chassis Control Domain Features (8 Features)\n\n"
code += "full_chs_features = " + repr(all_chs) + "\n"
code += 'print(f"Loaded all {len(full_chs_features)} Chassis features successfully.")\n'

with open("features_chs_full.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated features_chs_full.py successfully!")

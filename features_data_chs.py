# Vehicle Motion & Chassis Control Features (Features 13 to 17)

chs_features = [
    {
        "id": "FEAT-CHS-01",
        "name": "Electronic Stability Control (ESC)",
        "slug": "ESC",
        "domain": "Vehicle Motion & Chassis Control",
        "asil": "ASIL D",
        "summary": "Stabilizes vehicle yaw dynamics during extreme cornering and low-friction situations by applying individual-wheel hydraulic braking and demanding powertrain torque reductions.",
        "activation_logic": {
            "preconditions": "Ignition in RUN, vehicle speed > 8 km/h, hydraulic pressure sensor healthy, 6-DOF IMU calibrated.",
            "entry_conditions": "Yaw rate error (|Delta_YawRate| > 0.08 rad/s) OR vehicle sideslip angle (|Beta| > 4.5 deg) exceeds dynamic instability threshold.",
            "states": ["MONITORING", "UNDERSTEER_INTERVENTION", "OVERSTEER_INTERVENTION", "SPLIT_MU_STABILIZATION", "TRACTION_CONTROL_ACTIVE", "DEGRADED_PASSIVE", "FAULT_SHUTDOWN"],
            "deactivation_conditions": "Vehicle yaw rate and sideslip return within linear stable envelope for > 200 ms, or vehicle comes to complete stop.",
            "override_behavior": "Driver can select 'ESC Sport' (raising intervention threshold by 40%), but system cannot be completely defeated if collision is detected."
        },
        "safety_concept": {
            "safety_goal": "SG-ESC-01: Prevent uncontrolled vehicle spin-out or drift-out; avoid unintended asymmetric braking on dry straight roads.",
            "ftti": "40 ms",
            "safe_state": "De-energize all hydraulic solenoid valves (return to open circuit); restore 100% standard driver hydraulic pass-through.",
            "warning_escalation": "Flashing ESC amber icon on cluster during active intervention; steady amber icon if system has faulted."
        },
        "failure_behaviors": {
            "imu_drift": "If IMU yaw rate sensor drifts by > 0.04 rad/s while vehicle is driving straight, isolate sensor and fallback to wheel speed differential estimation.",
            "hydraulic_valve_stuck": "If pressure sensor reveals valve failure to release pressure, immediately fire high-pressure relief valve to depressurize circuit."
        },
        "sys_reqs": [
            {
                "id": "SYS-CHS-01-01",
                "title": "Bicycle Reference Model & Vehicle Sideslip Observer",
                "asil": "ASIL D",
                "statement": "The System SHALL sample 6-DOF IMU (yaw rate, lateral acceleration) and 4 wheel speed sensors at 100 Hz, calculating desired yaw rate and vehicle body sideslip angle (Beta +- 0.5 deg) at <= 10 ms period.",
                "activation": "Active at all times while vehicle speed > 8 km/h.",
                "ftti": "30 ms",
                "safe_state": "Invalidate observer outputs; suspend active ESC interventions.",
                "failure_reaction": "If wheel speed pulse drops, isolate affected wheel and use remaining 3 wheels for velocity estimation.",
                "inputs": "IMU_Yaw_Rate_RadS, IMU_Lat_Accel_Mps2, 4x_Wheel_Speed_Ticks, Steering_Wheel_Angle_Deg",
                "outputs": "YawRate_Error_RadS, Vehicle_Sideslip_Beta_Rad, Road_Friction_Mu_Est",
                "verification": "Chassis dynamometer and skid-pad testing against ISO 7401 lateral transient standards.",
                "downstream": ["SWR-CHS-01-01", "SWR-CHS-01-02"]
            },
            {
                "id": "SYS-CHS-01-02",
                "title": "Differential Individual-Wheel Pressure & Engine Torque Reduction",
                "asil": "ASIL D",
                "statement": "The System SHALL build up hydraulic braking pressure up to 120 bar on targeted individual wheels in <= 120 ms to create corrective yaw moments, while demanding fast powertrain torque reduction via CAN-FD in <= 20 ms.",
                "activation": "Active when YawRate_Error or Sideslip_Beta exceeds instability envelope.",
                "ftti": "40 ms",
                "safe_state": "Open hydraulic release valves; zero torque reduction request.",
                "failure_reaction": "If hydraulic pump motor overheats, limit maximum intervention duration to 5.0 seconds.",
                "inputs": "YawRate_Error_RadS, Vehicle_Sideslip_Beta_Rad, Driver_Master_Cylinder_Pressure",
                "outputs": "Target_Caliper_Pressure_FL/FR/RL/RR (bar), VCU_Torque_Clamp_Req_Nm",
                "verification": "FMVSS 126 / ECE R13H 'Sine with Dwell' vehicle test maneuver.",
                "downstream": ["SWR-CHS-01-03", "SWR-CHS-01-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-CHS-01-01",
                "title": "Bicycle Linear Vehicle Dynamics Reference Model",
                "parent": "SYS-CHS-01-01",
                "asil": "ASIL D",
                "swc": "EscReferenceModel_SWC",
                "period": "10 ms",
                "wcet": "1.2 ms",
                "activation": "Executed cyclically every 10 ms.",
                "algorithm": "Computes nominal steady-state yaw rate: Psi_dot_ref = (v_x / (L + K_us * v_x^2)) * delta_w. Saturates Psi_dot_ref by physical tire road friction limit: |Psi_dot_ref| <= (mu * g / v_x).",
                "safety_mechanism": "Friction adaptation: mu estimated continuously from longitudinal slip stiffness.",
                "failure_reaction": "If velocity v_x < 5 km/h, set target yaw rate to 0.0 rad/s.",
                "inputs": "Steering_Angle_Deg, Longitudinal_Velocity_Mps, Estimated_Mu",
                "outputs": "Target_Yaw_Rate_RadS (float32)",
                "verification": "Unit test verifying steady-state cornering gain across speeds 10 to 200 km/h."
            },
            {
                "id": "SWR-CHS-01-02",
                "title": "Extended Kalman Filter Body Sideslip Angle (Beta) Observer",
                "parent": "SYS-CHS-01-01",
                "asil": "ASIL D",
                "swc": "EscSideslipObserver_SWC",
                "period": "10 ms",
                "wcet": "2.4 ms",
                "activation": "Executed every 10 ms.",
                "algorithm": "Integrates kinematics equation: dBeta/dt = (a_y / v_x) - yaw_rate. Uses tire lateral force models to update Kalman covariance, correcting drift during prolonged cornering.",
                "safety_mechanism": "Integration drift limiter: Decays Beta towards zero during straight-line driving.",
                "failure_reaction": "Flag sideslip estimation invalid if lateral accelerometer reports saturation.",
                "inputs": "IMU_Lat_Accel_Mps2, IMU_Yaw_Rate_RadS, Longitudinal_Velocity_Mps",
                "outputs": "Estimated_Sideslip_Beta_Rad (float32), Observer_Confidence",
                "verification": "SIL verification on high-speed lane change maneuvers against CarSim ground truth."
            },
            {
                "id": "SWR-CHS-01-03",
                "title": "Oversteer/Understeer Phase-Plane Restoring Moment Controller",
                "parent": "SYS-CHS-01-02",
                "asil": "ASIL D",
                "swc": "EscYawMomentController_SWC",
                "period": "5 ms",
                "wcet": "1.5 ms",
                "activation": "Executed every 5 ms.",
                "algorithm": "Calculates restoring yaw moment: M_z = C_psi * (Yaw_Rate_Meas - Target_Yaw_Rate) + C_beta * Beta. Phase plane classifier determines intervention wheel: Oversteer -> Outer Front Wheel; Understeer -> Inner Rear Wheel.",
                "safety_mechanism": "Pressure gradient limiter: Rate of pressure increase clamped to <= 1000 bar/s.",
                "failure_reaction": "Inhibit intervention if driver counter-steering aligns with vehicle slide.",
                "inputs": "Yaw_Rate_Meas, Target_Yaw_Rate, Estimated_Sideslip_Beta_Rad",
                "outputs": "Delta_Pressure_FL, FR, RL, RR (float32 in bar)",
                "verification": "Phase-plane stability boundary unit test."
            },
            {
                "id": "SWR-CHS-01-04",
                "title": "VCU Fast Torque Clamping Dispatcher with E2E CRC",
                "parent": "SYS-CHS-01-02",
                "asil": "ASIL D",
                "swc": "EscTorqueReduction_SWC",
                "period": "10 ms",
                "wcet": "0.6 ms",
                "activation": "Executed during ESC intervention.",
                "algorithm": "Calculates maximum allowable engine/motor torque: T_max_allowed = F(M_z, Lateral_Slip). Transmits ESC_Torque_Clamp_PDU over chassis CAN-FD with 8-bit alive rolling counter and CRC-8.",
                "safety_mechanism": "Message transmission confirmed via VCU mirror acknowledgment frame.",
                "failure_reaction": "If VCU fails to clamp torque, escalate brake caliper pressures to compensate.",
                "inputs": "M_z, Current_Engine_Torque_Nm",
                "outputs": "ESC_Torque_Clamp_PDU (CAN-FD buffer)",
                "verification": "E2E communication protocol conformance and packet loss injection testing."
            }
        ]
    },
    {
        "id": "FEAT-CHS-02",
        "name": "Steer-by-Wire Handwheel & Rack Control (SbW)",
        "slug": "SbW",
        "domain": "Vehicle Motion & Chassis Control",
        "asil": "ASIL D",
        "summary": "Decoupled steering system replacing mechanical steering column with dual-redundant roadwheel rack actuators and a force-feedback handwheel actuator.",
        "activation_logic": {
            "preconditions": "Dual independent 12V/48V power supplies healthy, dual microcontrollers synchronized, rack resolvers calibrated.",
            "entry_conditions": "Vehicle power-up; handwheel homing completed; both redundant actuator channels reporting operational readiness.",
            "states": ["INITIALIZING", "CALIBRATED_ACTIVE", "VARIABLE_RATIO_TRACKING", "SINGLE_CHANNEL_DEGRADED", "FORCE_FEEDBACK_LIMP", "CRITICAL_LOCKOUT"],
            "deactivation_conditions": "Power shutdown or irrecoverable mechanical rack jam.",
            "override_behavior": "Driver physical handwheel torque is continuously tracked and converted to roadwheel angle; force-feedback motor provides synthesized road feel."
        },
        "safety_concept": {
            "safety_goal": "SG-SBW-01: Guarantee fail-operational lateral directional control; zero uncommanded steering motion; fail-operational redundancy upon any single electrical fault.",
            "ftti": "15 ms",
            "safe_state": "Secondary redundant motor takes over 100% rack steering control without interruption; limit maximum vehicle speed to 80 km/h.",
            "warning_escalation": "Immediate red steering wheel warning chime on cluster; prompt 'Steering System Fault - Drive to Service'."
        },
        "failure_behaviors": {
            "primary_motor_open_circuit": "Dual-inverter bridge detects open phase in < 2 ms; secondary winding motor takes over 100% rack force in <= 5 ms.",
            "handwheel_sensor_mismatch": "Triple-redundant sensor voting isolates corrupted channel; remaining two channels maintain control."
        },
        "sys_reqs": [
            {
                "id": "SYS-CHS-02-01",
                "title": "Triple-Redundant Handwheel Angle Acquisition & 2oo3 Voting",
                "asil": "ASIL D",
                "statement": "The System SHALL sample handwheel angle across three galvanic isolated sensors (< 0.05 deg resolution) and perform 2-out-of-3 voting at <= 2 ms period, isolating any faulty sensor in <= 4 ms.",
                "activation": "Active at all times when vehicle is powered.",
                "ftti": "10 ms",
                "safe_state": "Transition to 2-channel degraded mode if 1 sensor fails; lock steering position if 2 sensors fail.",
                "failure_reaction": "If sensor channel deviates by > 0.5 deg from other two, latch DEM event and isolate channel.",
                "inputs": "Handwheel_Angle_Sensor_1, Sensor_2, Sensor_3 (SPI / SENT interfaces)",
                "outputs": "Voted_Handwheel_Angle_Deg (float32), Sensor_Quorum_Health_Bits",
                "verification": "Sensor short-circuit, open-circuit, and noise injection HIL bench testing.",
                "downstream": ["SWR-CHS-02-01", "SWR-CHS-02-02"]
            },
            {
                "id": "SYS-CHS-02-02",
                "title": "Dual-Winding Roadwheel Rack Actuator Closed-Loop Servocontrol",
                "asil": "ASIL D",
                "statement": "The System SHALL drive dual-winding brushless steering rack motors to track requested roadwheel angle with < 0.2 deg dynamic lag and closed-loop bandwidth >= 15 Hz, distributing torque equally across channels.",
                "activation": "Active in CALIBRATED_ACTIVE and VARIABLE_RATIO_TRACKING states.",
                "ftti": "15 ms",
                "safe_state": "Single-channel 100% power takeover within 5 ms upon alternate channel fault.",
                "failure_reaction": "If rack position resolver fails, switch to motor sensorless back-EMF observer.",
                "inputs": "Voted_Handwheel_Angle_Deg, Vehicle_Speed_Kmph, Dual_Rack_Resolvers",
                "outputs": "Motor_1_Inverter_PWM, Motor_2_Inverter_PWM, Rack_Force_Feedback_Nm",
                "verification": "Dynamic steering rack loading test rig measuring step response and torque ripple.",
                "downstream": ["SWR-CHS-02-03", "SWR-CHS-02-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-CHS-02-01",
                "title": "2-out-of-3 (2oo3) Triple Modular Redundancy Voting Algorithm",
                "parent": "SYS-CHS-02-01",
                "asil": "ASIL D",
                "swc": "SbwHandwheelVoter_SWC",
                "period": "2 ms",
                "wcet": "0.3 ms",
                "activation": "Executed cyclically every 2 ms.",
                "algorithm": "Computes pairwise differences: D12 = |S1 - S2|, D23 = |S2 - S3|, D31 = |S3 - S1|. If all <= 0.5 deg, output = median(S1, S2, S3). If one channel deviates > 0.5 deg, discard outlier and average remaining two.",
                "safety_mechanism": "Deadband check: Rejects micro-glitches < 0.05 deg.",
                "failure_reaction": "If all pairwise differences exceed threshold, trigger emergency fail-safe lock.",
                "inputs": "Sensor_1_Angle, Sensor_2_Angle, Sensor_3_Angle",
                "outputs": "Voted_Handwheel_Angle_Deg (float32), Outlier_Channel_ID (uint8)",
                "verification": "100% MC/DC unit test covering all voting permutations."
            },
            {
                "id": "SWR-CHS-02-02",
                "title": "Handwheel Force-Feedback Synthetic Road Feel Synthesizer",
                "parent": "SYS-CHS-02-01",
                "asil": "ASIL B",
                "swc": "SbwFeelSynthesizer_SWC",
                "period": "2 ms",
                "wcet": "0.7 ms",
                "activation": "Executed every 2 ms.",
                "algorithm": "Synthesizes driver tactile feedback torque: Tau_feel = K_align(v_ego) * Rack_Force + D_h * dTheta/dt + Friction_Comp. Simulates natural self-centering steering wheel behavior.",
                "safety_mechanism": "Torque command bounded to maximum 7.0 Nm to avoid straining driver wrists.",
                "failure_reaction": "If feedback sensor fails, provide synthetic centering spring torque based purely on vehicle speed.",
                "inputs": "Rack_Force_Estimate_Nm, Handwheel_Angular_Velocity, Vehicle_Speed",
                "outputs": "Handwheel_Feedback_Torque_Cmd_Nm",
                "verification": "Driver-in-the-loop steering simulator subjective tuning tests."
            },
            {
                "id": "SWR-CHS-02-03",
                "title": "Speed-Sensitive Variable Steering Ratio (VSR) Calculator",
                "parent": "SYS-CHS-02-02",
                "asil": "ASIL D",
                "swc": "SbwRatioManager_SWC",
                "period": "5 ms",
                "wcet": "0.4 ms",
                "activation": "Executed every 5 ms.",
                "algorithm": "Computes dynamic steering ratio: R(v_ego) varies smoothly from 9.5:1 at parking speeds (0-15 km/h, full lock in 1.1 turns) to 16.5:1 at highway speeds (> 120 km/h) to maintain straight-line stability.",
                "safety_mechanism": "Rate of ratio change strictly limited: |dR/dt| <= 1.0 / sec to prevent sudden vehicle lurch.",
                "failure_reaction": "Lock steering ratio to fixed default 14.0:1 if vehicle speed sensor faults.",
                "inputs": "Voted_Handwheel_Angle_Deg, Vehicle_Speed_Kmph",
                "outputs": "Target_Roadwheel_Angle_Deg (float32)",
                "verification": "Unit test verifying monotonicity and continuity of ratio mapping curves."
            },
            {
                "id": "SWR-CHS-02-04",
                "title": "Dual-Inverter Cascaded Servoloop & Load Sharing Controller",
                "parent": "SYS-CHS-02-02",
                "asil": "ASIL D",
                "swc": "SbwRackServo_SWC",
                "period": "1 ms",
                "wcet": "0.35 ms",
                "activation": "Executed at 1000 Hz PWM interrupt.",
                "algorithm": "Executes cascaded position-velocity-current PID loop. Generates total rack force request F_rack. Distributes F_rack 50%/50% across Inverter 1 and Inverter 2. If Inverter 1 reports fault, Inverter 2 steps up to 100% in <= 5 ms.",
                "safety_mechanism": "Cross-channel current monitoring: Inverters verify each other's torque output via dual SPI.",
                "failure_reaction": "Immediately isolate shorted inverter bridge and ramp remaining motor to full power.",
                "inputs": "Target_Roadwheel_Angle_Deg, Resolver_1_Position, Resolver_2_Position, Channel_1_Status",
                "outputs": "PWM_Motor_1_Duty, PWM_Motor_2_Duty, Load_Share_Ratio",
                "verification": "Hardware dynamometer failover testing under full 12 kN steering rack load."
            }
        ]
    },
    {
        "id": "FEAT-CHS-03",
        "name": "Electro-Hydraulic Brake-by-Wire Deceleration (BbW)",
        "slug": "BbW",
        "domain": "Vehicle Motion & Chassis Control",
        "asil": "ASIL D",
        "summary": "Decoupled integrated brake-by-wire system (One-Box / Two-Box) providing pedal feel emulation and ultra-fast active brake pressure buildup (< 150 ms to 100 bar).",
        "activation_logic": {
            "preconditions": "Dual hydraulic circuits pressurized, dual ECU power domains healthy, fluid reservoir level normal.",
            "entry_conditions": "Driver applies brake pedal OR autonomous ADAS function (AEB/ACC) requests deceleration.",
            "states": ["MONITORING", "PEDAL_TRACKING", "AUTONOMOUS_PRESSURE_BUILD", "ABS_PRESSURE_MODULATION", "FALLBACK_PUSH_THROUGH", "FAULT_LOCKOUT"],
            "deactivation_conditions": "Pedal released, autonomous request zero, pressure vented to reservoir.",
            "override_behavior": "Complete electrical power failure opens mechanical push-through valves, enabling direct driver leg-power hydraulic braking adhering to ECE R13H."
        },
        "safety_concept": {
            "safety_goal": "SG-BBW-01: Guarantee vehicle stopping capability under any single electrical or hydraulic failure; maintain pedal deceleration feel.",
            "ftti": "20 ms",
            "safe_state": "Open mechanical push-through isolation valve; allow driver mechanical pedal pressure to reach front calipers directly.",
            "warning_escalation": "Brake red warning lamp on instrument cluster; continuous audible alarm."
        },
        "failure_behaviors": {
            "booster_motor_fault": "If electric brushless motor drive fails, open hydraulic separation valve in < 15 ms to engage direct hydraulic push-through.",
            "fluid_leak": "If pressure sensor in circuit 1 fails to build pressure, isolate circuit 1 via solenoid valve; maintain 100% braking on circuit 2."
        },
        "sys_reqs": [
            {
                "id": "SYS-CHS-03-01",
                "title": "Brake Pedal Stroke Emulation & Deceleration Intent Mapping",
                "asil": "ASIL D",
                "statement": "The System SHALL measure brake pedal travel stroke (< 0.1 mm resolution) and pedal force via dual redundant sensors at <= 2 ms period, mapping driver input into target vehicle deceleration (up to -1.0 g) with < 10 ms latency.",
                "activation": "Active at all times when vehicle is energized.",
                "ftti": "20 ms",
                "safe_state": "Revert to hydraulic push-through backup mode.",
                "failure_reaction": "If travel sensor channels disagree by > 2.0 mm, switch to pedal force hydraulic pressure backup sensor.",
                "inputs": "Dual_Pedal_Stroke_Sensors, Dual_Pedal_Force_Sensors",
                "outputs": "Target_Vehicle_Deceleration_Mps2, Driver_Braking_Active_Flag",
                "verification": "Pedal robot test stand measuring pedal travel vs. deceleration consistency.",
                "downstream": ["SWR-CHS-03-01", "SWR-CHS-03-02"]
            },
            {
                "id": "SYS-CHS-03-02",
                "title": "Electric Plunger High-Speed Hydraulic Pressure Regulation",
                "asil": "ASIL D",
                "statement": "The System SHALL drive a brushless electric plunger pump to generate hydraulic pressure from 0 to 100 bar in <= 150 ms with +-1.5 bar steady-state precision, distributing pressure to four calipers.",
                "activation": "Active during all braking events.",
                "ftti": "20 ms",
                "safe_state": "De-energize plunger motor; open push-through backup valves.",
                "failure_reaction": "If plunger jams, trigger secondary electronic brake booster channel.",
                "inputs": "Target_Vehicle_Deceleration_Mps2, Wheel_Speeds, Caliper_Pressure_Sensors[4]",
                "outputs": "Plunger_Motor_PWM_Cmd, Solenoid_Valve_PWM_Cmds[8]",
                "verification": "High-pressure hydraulic test rig verifying pressure rise time and acoustic noise.",
                "downstream": ["SWR-CHS-03-03", "SWR-CHS-03-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-CHS-03-01",
                "title": "Brake Pedal Dual-Sensor Cross-Check & Nonlinear Stroke Mapping",
                "parent": "SYS-CHS-03-01",
                "asil": "ASIL D",
                "swc": "BbwPedalDecoder_SWC",
                "period": "2 ms",
                "wcet": "0.4 ms",
                "activation": "Executed cyclically every 2 ms.",
                "algorithm": "Samples Stroke 1 and Stroke 2. Checks delta = |S1 - S2| <= 2.0 mm. Maps stroke through progressive 2-stage curve: Initial soft pedal bite (0-15 mm: 0 to -0.15g), firm deceleration (15-45 mm: -0.15g to -1.0g).",
                "safety_mechanism": "Cross-check against hydraulic master cylinder pressure sensor echo.",
                "failure_reaction": "If stroke sensors fail, compute deceleration purely from hydraulic pressure sensor.",
                "inputs": "ADC_Stroke_Sensor_1, ADC_Stroke_Sensor_2, Pressure_Sensor_Bar",
                "outputs": "Validated_Pedal_Decel_Cmd_Mps2 (float32)",
                "verification": "Unit test across entire 0 to 60 mm brake pedal stroke travel."
            },
            {
                "id": "SWR-CHS-03-02",
                "title": "Pedal Feel Simulator Hydraulic Chamber Isolation Supervisor",
                "parent": "SYS-CHS-03-01",
                "asil": "ASIL D",
                "swc": "BbwSimulatorManager_SWC",
                "period": "5 ms",
                "wcet": "0.3 ms",
                "activation": "Executed during normal brake-by-wire operation.",
                "algorithm": "Maintains Simulator Valve CLOSED during normal drive to route driver fluid into mechanical spring-loaded simulator chamber. Upon system fault, opens Simulator Valve and opens Separation Valve in < 15 ms.",
                "safety_mechanism": "Normally-open mechanical separation valve ensures safe unpowered push-through.",
                "failure_reaction": "De-energize solenoid coils to physically drop into mechanical backup mode.",
                "inputs": "System_Health_Status_Enum, Ignition_Power_Good_Flag",
                "outputs": "Simulator_Valve_Driver_Pin, Separation_Valve_Driver_Pin",
                "verification": "Power-loss test evaluating separation valve transition timing."
            },
            {
                "id": "SWR-CHS-03-03",
                "title": "Brushless Electric Plunger Pressure Closed-Loop Servoloop",
                "parent": "SYS-CHS-03-02",
                "asil": "ASIL D",
                "swc": "BbwPressureController_SWC",
                "period": "1 ms",
                "wcet": "0.35 ms",
                "activation": "Executed at 1000 Hz.",
                "algorithm": "Implements gain-scheduled PID with feedforward: PWM_plunger = K_p * e_p + K_i * int(e_p) + K_d * de_p/dt + F_ff(P_target). Compares target pressure against high-pressure sensor feedback.",
                "safety_mechanism": "Overpressure protection: Plunger motor current cut if pressure exceeds 180 bar.",
                "failure_reaction": "If pressure fails to reach target within 200 ms, report plunger motor stall.",
                "inputs": "Target_Pressure_Bar, Measured_Pressure_Bar, Plunger_Position_Mm",
                "outputs": "Plunger_Motor_PWM_Duty (float32)",
                "verification": "Pressure rise-time and step-response verification in HIL environment."
            },
            {
                "id": "SWR-CHS-03-04",
                "title": "Independent Four-Corner Caliper Pressure Proportioning",
                "parent": "SYS-CHS-03-02",
                "asil": "ASIL D",
                "swc": "BbwPressureDistributor_SWC",
                "period": "2 ms",
                "wcet": "0.6 ms",
                "activation": "Executed every 2 ms on plunger pressure output.",
                "algorithm": "Applies Dynamic Rear Proportioning (EBD) to prevent rear wheel lockup: P_rear = min(P_front, F_ebd(v_ego, a_x)). Modulates high-speed inlet and outlet valves for each wheel caliper.",
                "safety_mechanism": "Rear brake pressure capped by dynamic load transfer curve based on longitudinal deceleration.",
                "failure_reaction": "If one wheel valve fails, lock valve open and regulate pressure via plunger.",
                "inputs": "Target_Plunger_Pressure, Vehicle_Decel_Mps2, Individual_Wheel_Slip[4]",
                "outputs": "Valve_PWM_FL, FR, RL, RR (uint16 array)",
                "verification": "Automated EBD braking test on high and low friction surfaces."
            }
        ]
    },
    {
        "id": "FEAT-CHS-04",
        "name": "Electronic Continuous Damping Control & Active Suspension (EDC)",
        "slug": "EDC",
        "domain": "Vehicle Motion & Chassis Control",
        "asil": "ASIL C",
        "summary": "Continuously adjusts semi-active damper solenoid valve currents at 100 Hz to isolate road vibrations (Skyhook algorithm) and eliminate pitch and roll body motions.",
        "activation_logic": {
            "preconditions": "12V power supply healthy, 4 wheel displacement sensors calibrated, vehicle moving.",
            "entry_conditions": "Vehicle speed > 2 km/h; driver selects drive mode (Comfort, Normal, Sport).",
            "states": ["MONITORING", "COMFORT_SKYHOOK", "SPORT_GROUNDHOOK", "ROLL_STABILIZATION", "ROUGH_ROAD_PROTECTION", "FAILSAFE_DEFAULT_DAMPING"],
            "deactivation_conditions": "Vehicle parked in PARK with ignition OFF.",
            "override_behavior": "Sudden aggressive steering input (> 100 deg/s) instantly forces dampers to maximum firm setting in < 15 ms to suppress body roll."
        },
        "safety_concept": {
            "safety_goal": "SG-EDC-01: Maintain tire-to-road contact; prevent suspension bottoming out or unstable body roll oscillations.",
            "ftti": "50 ms",
            "safe_state": "De-energize all damper solenoids to passive mid-firm default damping setting.",
            "warning_escalation": "Yellow suspension warning light on instrument cluster."
        },
        "failure_behaviors": {
            "displacement_sensor_failure": "If 1 corner sensor fails, extrapolate corner motion from remaining 3 sensors using chassis planar model.",
            "solenoid_open_circuit": "If front-left damper solenoid coil opens, set front-right damper to passive baseline to maintain axle symmetry."
        },
        "sys_reqs": [
            {
                "id": "SYS-CHS-04-01",
                "title": "Chassis Body Acceleration & Wheel Kinematic Acquisition",
                "asil": "ASIL C",
                "statement": "The System SHALL sample 3 vertical body accelerometers and 4 corner suspension height sensors at >= 100 Hz, calculating chassis heave, pitch, and roll rates at <= 10 ms period.",
                "activation": "Active when vehicle is moving.",
                "ftti": "50 ms",
                "safe_state": "Zero body motion velocity estimates; suspend Skyhook control.",
                "failure_reaction": "If vertical accelerometer saturates, clamp reading to physical bump-stop limit.",
                "inputs": "3x_Body_Accelerometers, 4x_Height_Sensors, Steering_Wheel_Angle, Vehicle_Speed",
                "outputs": "Chassis_Heave_Rate_Mps, Chassis_Pitch_Rate_RadS, Chassis_Roll_Rate_RadS",
                "verification": "4-poster suspension shaker rig testing across road roughness profiles.",
                "downstream": ["SWR-CHS-04-01", "SWR-CHS-04-02"]
            },
            {
                "id": "SYS-CHS-04-02",
                "title": "Skyhook/Groundhook Damping Current Modulation",
                "asil": "ASIL C",
                "statement": "The System SHALL modulate PWM current (0.2A to 1.8A) through four continuously variable proportional damper valves in <= 15 ms, altering damping force between 500 N and 5000 N per corner.",
                "activation": "Active during driving.",
                "ftti": "30 ms",
                "safe_state": "Set valve current to 0.0 A (mechanical default fail-safe damping).",
                "failure_reaction": "If solenoid driver reports thermal overload, reduce current by 30%.",
                "inputs": "Heave_Rate, Pitch_Rate, Roll_Rate, Relative_Damper_Velocities[4]",
                "outputs": "Damper_Solenoid_Current_FL/FR/RL/RR (Amps)",
                "verification": "Damper dynamometer characterization over velocity range -1.5 m/s to +1.5 m/s.",
                "downstream": ["SWR-CHS-04-03", "SWR-CHS-04-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-CHS-04-01",
                "title": "Chassis Rigid-Body 3D Kinematics Reconstruction",
                "parent": "SYS-CHS-04-01",
                "asil": "ASIL C",
                "swc": "EdcKinematics_SWC",
                "period": "10 ms",
                "wcet": "1.1 ms",
                "activation": "Executed cyclically every 10 ms.",
                "algorithm": "Integrates vertical accelerometer signals. Transforms corner height sensor derivatives into rigid-body modal coordinates: Heave z_cg, Pitch theta, and Roll phi using vehicle geometry transformation matrix.",
                "safety_mechanism": "High-pass washout filter (f_c = 0.2 Hz) removes integration drift and DC bias.",
                "failure_reaction": "If sensor values disagree with planar geometry, report sensor rationality error.",
                "inputs": "Accel_FL_Z, Accel_FR_Z, Accel_Rear_Z, Height_FL, Height_FR, Height_RL, Height_RR",
                "outputs": "Modal_Heave_Vel, Modal_Pitch_Rate, Modal_Roll_Rate",
                "verification": "Mathematical unit test verifying modal coordinate transformation."
            },
            {
                "id": "SWR-CHS-04-02",
                "title": "Lookahead Road Surface Camera Preview Filter",
                "parent": "SYS-CHS-04-01",
                "asil": "ASIL B",
                "swc": "EdcRoadPreview_SWC",
                "period": "20 ms",
                "wcet": "2.2 ms",
                "activation": "Executed when front stereo camera road elevation profile is valid.",
                "algorithm": "Parses road height map 5 to 15 m ahead. Detects speed bumps and potholes. Calculates wheel arrival time t_arrival = d / v_ego. Pre-softens dampers 50 ms before bump impact to absorb shock.",
                "safety_mechanism": "Preview disabled if vehicle speed < 15 km/h or camera confidence < 70%.",
                "failure_reaction": "Silently disable road preview without interrupting baseline Skyhook control.",
                "inputs": "Camera_Road_Elevation_Profile, Vehicle_Speed_Mps",
                "outputs": "Preview_Damper_Adjustment_Offset_Amps",
                "verification": "Road bump driving tests measuring chassis peak vertical acceleration."
            },
            {
                "id": "SWR-CHS-04-03",
                "title": "Continuous Skyhook Damping Control Law",
                "parent": "SYS-CHS-04-02",
                "asil": "ASIL C",
                "swc": "EdcSkyhookController_SWC",
                "period": "5 ms",
                "wcet": "1.4 ms",
                "activation": "Executed every 5 ms.",
                "algorithm": "Implements Skyhook algorithm: F_sky = -C_sky * V_body. If V_body * V_rel > 0 (compression while body moves up): F_damper = max(F_min, min(F_max, F_sky)). Otherwise: F_damper = F_min.",
                "safety_mechanism": "Ensures semi-active passivity constraint is strictly obeyed at all times.",
                "failure_reaction": "If relative velocity sensor indicates zero motion, hold current at mid-setting.",
                "inputs": "Modal_Heave_Vel, Relative_Suspension_Velocity[4], Drive_Mode_Enum",
                "outputs": "Demanded_Damping_Force_N[4]",
                "verification": "Frequency-response SIL simulation across wheel hop and body bounce frequencies."
            },
            {
                "id": "SWR-CHS-04-04",
                "title": "Proportional Damper Solenoid Current H-Bridge Controller",
                "parent": "SYS-CHS-04-02",
                "asil": "ASIL C",
                "swc": "EdcCurrentDriver_SWC",
                "period": "1 ms",
                "wcet": "0.3 ms",
                "activation": "Executed at 1000 Hz.",
                "algorithm": "Converts demanded force to target solenoid current I_target = f(F_demanded, V_rel). Closes PI current loop on 20 kHz PWM driver: PWM = K_p * (I_target - I_meas) + K_i * int(e).",
                "safety_mechanism": "Dither injection: Injects 100 Hz micro-dither current to eliminate mechanical valve hysteresis.",
                "failure_reaction": "If open circuit detected on coil, report DTC C1041.",
                "inputs": "Demanded_Damping_Force_N[4], Shunt_Current_Feedback_A[4]",
                "outputs": "Damper_PWM_Duty[4] (uint16)",
                "verification": "Bench testing of current control loop rise time and steady-state ripple."
            }
        ]
    },
    {
        "id": "FEAT-CHS-05",
        "name": "Electronic Torque Vectoring & All-Wheel Drive (e-AWD)",
        "slug": "eAWD",
        "domain": "Vehicle Motion & Chassis Control",
        "asil": "ASIL D",
        "summary": "Coordinates dual/tri-motor electric drivetrains to distribute independent drive/regen torque between front and rear axles and left/right wheels to optimize agility and traction.",
        "activation_logic": {
            "preconditions": "Both front and rear inverters operational, high-voltage battery ready, steering and yaw sensors healthy.",
            "entry_conditions": "Vehicle moving in D or R mode.",
            "states": ["EFFICIENCY_FWD_OR_RWD", "DYNAMIC_AWD_SPLIT", "ACTIVE_YAW_VECTORING", "OFFROAD_TRACTION_LOCK", "LOW_MU_SLIP_CONTROL", "FAILSAFE_SINGLE_AXLE"],
            "deactivation_conditions": "Transmission shifted to P or N, or critical failure on both axles.",
            "override_behavior": "ESC stability intervention overrides torque vectoring, prioritizing yaw stabilization over cornering agility."
        },
        "safety_concept": {
            "safety_goal": "SG-AWD-01: Prevent unintended yaw moment generation; ensure torque vectoring cannot induce vehicle spin-out.",
            "ftti": "40 ms",
            "safe_state": "Equalize left/right wheel torques; fallback to symmetric front/rear axle torque distribution.",
            "warning_escalation": "Display 'AWD System Degraded - 2WD Only' banner on driver instrument cluster."
        },
        "failure_behaviors": {
            "rear_inverter_loss": "If rear motor inverter trips, instantaneously transfer 100% propulsion torque to front motor in <= 10 ms.",
            "differential_speed_spike": "If one wheel experiences sudden traction breakaway (ice patch), cut torque to slipping wheel within 15 ms."
        },
        "sys_reqs": [
            {
                "id": "SYS-CHS-05-01",
                "title": "Front-to-Rear Dynamic Axle Torque Allocation",
                "asil": "ASIL D",
                "statement": "The System SHALL dynamically split total driver torque between front and rear axles (from 100:0 to 0:100) based on dynamic axle load transfer, wheel slip, and drive mode at <= 10 ms period.",
                "activation": "Active at all times in DRIVE mode.",
                "ftti": "50 ms",
                "safe_state": "Default to fixed 50:50 torque split or single-axle propulsion.",
                "failure_reaction": "If rear motor overtemperature trips, command 100% torque to front axle.",
                "inputs": "Total_Driver_Torque_Demand_Nm, Vehicle_Accel_Ax, 4x_Wheel_Speeds, Drive_Mode",
                "outputs": "Front_Axle_Torque_Cmd_Nm, Rear_Axle_Torque_Cmd_Nm",
                "verification": "Chassis 4WD dynamometer acceleration and hill-climb testing.",
                "downstream": ["SWR-CHS-05-01", "SWR-CHS-05-02"]
            },
            {
                "id": "SYS-CHS-05-02",
                "title": "Lateral Left-Right Direct Yaw Moment Vectoring",
                "asil": "ASIL D",
                "statement": "The System SHALL apply differential torque (up to +-1200 Nm delta between left and right wheels) during cornering to generate active yaw moment, reducing understeer while verifying stability.",
                "activation": "Active during cornering when vehicle speed > 20 km/h and steering angle > 10 deg.",
                "ftti": "40 ms",
                "safe_state": "Zero delta torque between left and right wheels (T_left = T_right).",
                "failure_reaction": "If yaw rate error deviates from linear stability limit, terminate torque vectoring.",
                "inputs": "Steering_Angle_Deg, Yaw_Rate_RadS, Lateral_Accel_Mps2, Total_Rear_Torque_Nm",
                "outputs": "Rear_Left_Motor_Torque_Nm, Rear_Right_Motor_Torque_Nm",
                "verification": "Handling track lap-time and slalom skid-pad evaluation.",
                "downstream": ["SWR-CHS-05-03", "SWR-CHS-05-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-CHS-05-01",
                "title": "Dynamic Axle Weight Transfer & Slip-Based AWD Splitter",
                "parent": "SYS-CHS-05-01",
                "asil": "ASIL D",
                "swc": "AwdAxleSplitter_SWC",
                "period": "10 ms",
                "wcet": "1.2 ms",
                "activation": "Executed cyclically every 10 ms.",
                "algorithm": "Calculates dynamic vertical loads: Fz_front = Fz_static_front - m*h/L * a_x; Fz_rear = Fz_static_rear + m*h/L * a_x. Distributes torque proportionally to vertical tire capacity to maximize traction without slip.",
                "safety_mechanism": "Torque clamp: Front and rear commands sum exactly to total driver demanded torque.",
                "failure_reaction": "Revert to fixed 50/50 split if longitudinal accelerometer fails.",
                "inputs": "Total_Demanded_Torque_Nm, Longitudinal_Accel_Ax, Wheel_Slip_Ratios[4]",
                "outputs": "Raw_Front_Torque_Nm, Raw_Rear_Torque_Nm",
                "verification": "SIL vehicle acceleration model test on low-mu surfaces."
            },
            {
                "id": "SWR-CHS-05-02",
                "title": "High-Efficiency Single-Axle Decoupling & Disconnect Coordinator",
                "parent": "SYS-CHS-05-01",
                "asil": "ASIL B",
                "swc": "AwdEfficiencyDisconnect_SWC",
                "period": "50 ms",
                "wcet": "0.6 ms",
                "activation": "Executed during highway cruise in ECO mode.",
                "algorithm": "When cruising at constant speed on dry highway, transitions front induction motor into zero-field idle mode (or opens mechanical disconnect clutch) to eliminate drag, reducing consumption by up to 8%.",
                "safety_mechanism": "Rapid re-engagement: Re-energizes front motor within < 50 ms upon accelerator tip-in.",
                "failure_reaction": "Keep both axles permanently coupled if disconnect actuator status is uncertain.",
                "inputs": "Vehicle_Speed_Kmph, Accelerator_Rate_PctS, Road_Grade_Pct, ECO_Mode_Active",
                "outputs": "Front_Axle_Disconnect_Cmd (boolean), Axle_Efficiency_Mode_Enum",
                "verification": "WLTP cycle range test validating energy savings."
            },
            {
                "id": "SWR-CHS-05-03",
                "title": "Active Agility Direct Yaw Moment (DYC) Controller",
                "parent": "SYS-CHS-05-02",
                "asil": "ASIL D",
                "swc": "TorqueVectoringController_SWC",
                "period": "5 ms",
                "wcet": "1.4 ms",
                "activation": "Executed every 5 ms during cornering.",
                "algorithm": "Computes desired agility yaw moment: M_z_des = K_tv * Steering_Angle * v_ego. Splits rear axle torque: T_RL = T_rear/2 - Delta_T; T_RR = T_rear/2 + Delta_T, where Delta_T = (M_z_des * r_wheel) / Track_width.",
                "safety_mechanism": "Stability envelope boundary: Suppresses Delta_T if vehicle sideslip angle exceeds 3.0 deg.",
                "failure_reaction": "Force Delta_T = 0 Nm if ESC requests active intervention.",
                "inputs": "Steering_Angle_Deg, Vehicle_Speed_Mps, Raw_Rear_Torque_Nm, Sideslip_Beta",
                "outputs": "Target_Torque_RL_Nm, Target_Torque_RR_Nm",
                "verification": "Slalom cone course telemetry analysis measuring yaw agility."
            },
            {
                "id": "SWR-CHS-05-04",
                "title": "Low-Mu Traction Lock & Electronic Limited Slip Emulation",
                "parent": "SYS-CHS-05-02",
                "asil": "ASIL D",
                "swc": "AwdTractionLock_SWC",
                "period": "5 ms",
                "wcet": "0.8 ms",
                "activation": "Executed when wheel slip difference exceeds 10%.",
                "algorithm": "If abs(omega_RL - omega_RR) > threshold, transfers drive torque from spinning wheel to high-traction wheel. Mimics mechanical locking differential without hardware clutch pack.",
                "safety_mechanism": "Thermal limit protection: Prevents excessive motor heating during prolonged mud/snow recovery.",
                "failure_reaction": "If motor thermistor exceeds 140°C, ramp down torque transfer.",
                "inputs": "Wheel_Speed_RL, Wheel_Speed_RR, Motor_Temperatures",
                "outputs": "Traction_Compensated_Torque_RL, Traction_Compensated_Torque_RR",
                "verification": "Roller bench split-mu traction test (one wheel on rollers, one on asphalt)."
            }
        ]
    }
]

print(f"Loaded all {len(chs_features)} Chassis features successfully.")

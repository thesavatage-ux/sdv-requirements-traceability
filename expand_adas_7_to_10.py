# expand_adas_7_to_10.py
import features_adas_full

old_feats = {f["id"]: f for f in features_adas_full.adas_features}

# Retain 1 to 6
all_feats = [
    old_feats["FEAT-ADAS-01"],
    old_feats["FEAT-ADAS-02"],
    old_feats["FEAT-ADAS-03"],
    old_feats["FEAT-ADAS-04"],
    old_feats["FEAT-ADAS-05"],
    old_feats["FEAT-ADAS-06"]
]

# FEAT-ADAS-07: APA (Expanded to 4 sys reqs, 8 sw reqs)
f7 = old_feats["FEAT-ADAS-07"]
f7["sys_reqs"].extend([
    {
        "id": "SYS-ADAS-07-03",
        "title": "Multi-Move Path Shifting & Automated Transmission Direction Coordinator",
        "asil": "ASIL B",
        "statement": "The System SHALL coordinate automated multi-turn maneuvers (up to 5 gear shifts between DRIVE and REVERSE) to park in tight spaces, holding vehicle with foundation brakes during shift transition (< 800 ms).",
        "activation": "Active when multi-move parking trajectory is required.",
        "ftti": "80 ms",
        "safe_state": "Hold vehicle stopped in current gear; request driver manual intervention.",
        "failure_reaction": "If shift actuator times out > 1200 ms, abort parking maneuver and apply EPB.",
        "inputs": "Trajectory_Maneuver_Step_Index, Current_Gear_PRND, Vehicle_Speed_Mps",
        "outputs": "Target_Gear_Command_PRND, Shift_Brake_Hold_Req, Maneuver_Step_Complete_Flag",
        "verification": "Multi-turn tight parallel parking slot test (car length + 0.8 m).",
        "downstream": ["SWR-ADAS-07-05", "SWR-ADAS-07-06"]
    },
    {
        "id": "SYS-ADAS-07-04",
        "title": "Remote Smartphone Continuous Touch Dead-Man Switch Supervisor",
        "asil": "ASIL B",
        "statement": "The System SHALL supervise Bluetooth Low Energy (BLE) remote smartphone touch input: Vehicle motion SHALL occur ONLY while user continuously holds finger on smartphone screen button, stopping in <= 200 ms upon touch release or BLE disconnect (> 6 m distance).",
        "activation": "Active in Remote Parking Assist (RPA) mode.",
        "ftti": "100 ms",
        "safe_state": "Execute immediate stop; apply hydraulic service brakes.",
        "failure_reaction": "If BLE packet loss exceeds 2 consecutive packets (100 ms), halt vehicle instantly.",
        "inputs": "BLE_Continuous_Touch_Token, BLE_RSSI_Distance_Estimate_M, Deadman_Switch_State",
        "outputs": "Remote_Motion_Permit_Flag (boolean), BLE_Connection_Status_Enum",
        "verification": "Smartphone screen release latency and RF packet drop injection tests.",
        "downstream": ["SWR-ADAS-07-07", "SWR-ADAS-07-08"]
    }
])
f7["sw_reqs"].extend([
    {
        "id": "SWR-ADAS-07-05",
        "title": "Shift-by-Wire Automated PRND Transmission Sequencer",
        "parent": "SYS-ADAS-07-03",
        "asil": "ASIL B",
        "swc": "ApaShiftSequencer_SWC",
        "period": "20 ms",
        "wcc": "0.5 ms",
        "wcet": "0.5 ms",
        "activation": "Active at maneuver directional change points.",
        "algorithm": "Applies hydraulic brakes until wheel speed == 0.0 m/s for 200 ms. Commands transmission shift (e.g. D -> R). Verifies transmission status byte matches target before releasing brake pressure to ramp up creep torque.",
        "safety_mechanism": "Shift interlock: Zero motor torque commanded while transmission gear is in intermediate neutral transition.",
        "failure_reaction": "Latch DTC P0700 if transmission fails to engage commanded gear.",
        "inputs": "Maneuver_Direction_Demand_PRND, Transmission_Actual_Gear, Wheel_Speed_Ticks",
        "outputs": "Shift_By_Wire_CAN_PDU, Brake_Hold_Active_Flag",
        "verification": "Automated transmission cycling test across 500 multi-move park maneuvers."
    },
    {
        "id": "SWR-ADAS-07-06",
        "title": "Kerbstone Height & Wheel Rim Scuff Protective Observer",
        "parent": "SYS-ADAS-07-03",
        "asil": "ASIL B",
        "swc": "ApaKerbstoneGuard_SWC",
        "period": "10 ms",
        "wcet": "0.4 ms",
        "activation": "Active when parking adjacent to curbs.",
        "algorithm": "Fuses ultrasonic side sensors and surround camera edge detection: Classifies curb height. If curb > 8 cm, offsets target trajectory by +12 cm away from curb to protect alloy wheels from scuff damage.",
        "safety_mechanism": "Curb collision avoidance: Stops vehicle if wheel tire sidewall approaches within 5 cm of high stone curb.",
        "failure_reaction": "Inhibit parking if curb height exceeds vehicle ground clearance (15 cm).",
        "inputs": "Side_Ultrasonic_Echo_Profiles[4], Camera_Curber_Points[16]",
        "outputs": "Curb_Offset_Correction_Cm, High_Curb_Warning_Flag",
        "verification": "Real curb parking test measuring wheel rim clearance distance."
    },
    {
        "id": "SWR-ADAS-07-07",
        "title": "BLE Dead-Man Touch Heartbeat Packet Parser & Range Poller",
        "parent": "SYS-ADAS-07-04",
        "asil": "ASIL B",
        "swc": "ApaBleSupervisor_SWC",
        "period": "20 ms",
        "wcet": "0.3 ms",
        "activation": "Active during remote parking operation.",
        "algorithm": "Parses encrypted BLE heartbeat packet received every 50 ms. Verifies rolling counter and dynamic touch hold status. Evaluates BLE signal RSSI: Computes distance d_user. If d_user > 6.0 m, clears Motion_Permit.",
        "safety_mechanism": "Timeout monitor: Missing heartbeat packet for > 100 ms clears motion permit unconditionally.",
        "failure_reaction": "Stop vehicle and apply EPB upon BLE connection loss.",
        "inputs": "Raw_BLE_Packet_Payload[32], BLE_RSSI_Dbm, Vehicle_Speed_Mps",
        "outputs": "DeadMan_Touch_Confirmed_Flag (boolean), User_Proximity_Distance_M",
        "verification": "Smartphone app screen release response latency measurements."
    },
    {
        "id": "SWR-ADAS-07-08",
        "title": "Remote Parking Fast Deceleration Interrupter & Brake Clamper",
        "parent": "SYS-ADAS-07-04",
        "asil": "ASIL B",
        "swc": "ApaRemoteBrake_SWC",
        "period": "10 ms",
        "wcet": "0.3 ms",
        "activation": "Supervises remote motion.",
        "algorithm": "If DeadMan_Touch_Confirmed drops to FALSE, immediately commands service brake pressure to 40 bar in <= 150 ms, bringing vehicle to immediate stop from parking crawl speed.",
        "safety_mechanism": "EPB secondary clamp: Engages mechanical EPB if vehicle remains stopped for > 3.0 seconds.",
        "failure_reaction": "Report fault to smartphone app if hydraulic pressure cannot be maintained.",
        "inputs": "DeadMan_Touch_Confirmed_Flag, Vehicle_Speed_Mps",
        "outputs": "Emergency_Brake_Pressure_Bar, Remote_Park_Halt_State",
        "verification": "Stop latency test from fingertip release to zero vehicle velocity."
    }
])
all_feats.append(f7)

# FEAT-ADAS-08: BSD-LCA (Expanded to 4 sys reqs, 8 sw reqs)
f8 = old_feats["FEAT-ADAS-08"]
f8["sys_reqs"].extend([
    {
        "id": "SYS-ADAS-08-03",
        "title": "Side Mirror Dual-Stage LED Warning & Acoustic Chime Trigger",
        "asil": "ASIL B",
        "statement": "The System SHALL command side mirror triangular amber LED indicators: Stage 1 (Continuous ON) when vehicle is in blind zone; Stage 2 (Flashing 4.0 Hz + 800 Hz chime) if driver activates turn indicator towards occupied zone.",
        "activation": "Active at speeds > 15 km/h.",
        "ftti": "60 ms",
        "safe_state": "Extinguish warning LEDs; prompt driver via cluster text.",
        "failure_reaction": "If LED driver reports open circuit, log DTC B15C2 and display cluster alert.",
        "inputs": "Blind_Zone_Occupied_Left, Blind_Zone_Occupied_Right, Turn_Signal_Stalk_State",
        "outputs": "Mirror_LED_Left_Cmd, Mirror_LED_Right_Cmd, BSD_Warning_Chime_Req",
        "verification": "Photometric mirror LED flash frequency and luminance testing.",
        "downstream": ["SWR-ADAS-08-05", "SWR-ADAS-08-06"]
    },
    {
        "id": "SYS-ADAS-08-04",
        "title": "Active Steering Resistance Overlay to Oppose Collision Lane Change",
        "asil": "ASIL B",
        "statement": "The System SHALL command EPS steering torque resistance (up to +3.0 Nm opposing driver turn) if driver begins steering across lane line into an approaching vehicle (TTC <= 2.5s) to prevent sideswipe collision.",
        "activation": "Active when lane change collision is predicted.",
        "ftti": "40 ms",
        "safe_state": "Zero opposing torque; restore free manual steering.",
        "failure_reaction": "Inhibit steering resistance if driver applies > 5.0 Nm intentional force.",
        "inputs": "Closing_Vehicle_TTC_Sec, Steering_Wheel_Angle_Deg, Lane_Line_Crossing_Flag",
        "outputs": "EPS_Opposing_Torque_Nm, Sideswipe_Intervention_Active_Flag",
        "verification": "ISO 17387 lane change collision avoidance dynamic track test.",
        "downstream": ["SWR-ADAS-08-07", "SWR-ADAS-08-08"]
    }
])
f8["sw_reqs"].extend([
    {
        "id": "SWR-ADAS-08-05",
        "title": "Side Mirror Warning LED Pulse-Width Modulator & Dimmer",
        "parent": "SYS-ADAS-08-03",
        "asil": "ASIL B",
        "swc": "BsdMirrorLed_SWC",
        "period": "20 ms",
        "wcet": "0.3 ms",
        "activation": "Cyclic 20 ms task.",
        "algorithm": "Modulates LED brightness based on ambient light sensor (bright daytime: 100% PWM; nighttime: 30% PWM to prevent glare). Generates 4.0 Hz square wave flashing when turn signal matches occupied side.",
        "safety_mechanism": "Driver feedback diagnostic: Reads shunt resistor voltage to verify LED current draw (15-25 mA).",
        "failure_reaction": "Report LED_Circuit_Fault if shunt current is zero.",
        "inputs": "Threat_Level_Side_Enum, Ambient_Lux_Sensor, Turn_Signal_Active_Side",
        "outputs": "LED_PWM_Duty_Cycle_Left, LED_PWM_Duty_Cycle_Right",
        "verification": "Illuminance meter test across ambient lighting from 1 lux to 100,000 lux."
    },
    {
        "id": "SWR-ADAS-08-06",
        "title": "Blind Spot Audio Alert Chime Escalation Coordinator",
        "parent": "SYS-ADAS-08-03",
        "asil": "ASIL B",
        "swc": "BsdAudioAlert_SWC",
        "period": "20 ms",
        "wcet": "0.3 ms",
        "activation": "Active on Stage 2 alert.",
        "algorithm": "Sends chime request to cockpit audio DSP over CAN-FD: Requests directional double-chirp tone (800 Hz, 75 dB(A)) routed through door speaker on the threatened side to orient driver attention.",
        "safety_mechanism": "Chime mute guard: Does not suppress audio if driver is on emergency phone call.",
        "failure_reaction": "Direct chime to cluster hardware buzzer if audio DSP fails.",
        "inputs": "Stage2_Alert_Left_Flag, Stage2_Alert_Right_Flag",
        "outputs": "Directional_Chime_Command_Payload, Chime_Speaker_Select_Enum",
        "verification": "Directional sound localization acoustic testing in vehicle interior."
    },
    {
        "id": "SWR-ADAS-08-07",
        "title": "Sideswipe Collision Trajectory Predictor & Kinematic Risk Gate",
        "parent": "SYS-ADAS-08-04",
        "asil": "ASIL B",
        "swc": "BsdSideswipePredictor_SWC",
        "period": "10 ms",
        "wcet": "0.8 ms",
        "activation": "Active when vehicle begins drifting towards adjacent lane.",
        "algorithm": "Predicts lateral distance between ego flank and target vehicle: d_flank(t) = d_lateral_0 - (v_lat_ego + v_lat_target) * t. If d_flank reaches 0.0 m within t < 2.5 seconds, triggers active steering resistance.",
        "safety_mechanism": "Sanity check: Rejects target tracks with negative longitudinal closing speed.",
        "failure_reaction": "Inhibit steering intervention if target confidence < 70%.",
        "inputs": "Target_Relative_Pos_X_Y, Target_Relative_Vel_X_Y, Ego_Lateral_Velocity_Mps",
        "outputs": "Sideswipe_Collision_Risk_Flag, Time_To_Sideswipe_Sec",
        "verification": "High-speed highway passing scenario simulation with closing speed up to 70 km/h."
    },
    {
        "id": "SWR-ADAS-08-08",
        "title": "Active EPS Steering Resistance Haptic Virtual Barrier Generator",
        "parent": "SYS-ADAS-08-04",
        "asil": "ASIL B",
        "swc": "BsdSteeringResistance_SWC",
        "period": "5 ms",
        "wcet": "0.4 ms",
        "activation": "Triggered on Sideswipe_Collision_Risk_Flag.",
        "algorithm": "Commands EPS to synthesize virtual elastic resistance barrier: T_barrier = K_barrier * (Lateral_Displacement_Past_Line). Maximum opposing torque capped to +3.0 Nm. Feels like stiff virtual spring pushing steering wheel back.",
        "safety_mechanism": "Driver override dominance: Driver can easily overcome resistance with 4.5 Nm handwheel torque.",
        "failure_reaction": "Zero torque output if steering torque sensor confidence degrades.",
        "inputs": "Sideswipe_Collision_Risk_Flag, Lateral_Lane_Position_M, Driver_Handwheel_Torque_Nm",
        "outputs": "EPS_Barrier_Torque_Cmd_Nm, Intervention_Duration_Timer_Sec",
        "verification": "HIL steering robot test measuring opposing torque gradient and driver override threshold."
    }
])
all_feats.append(f8)

# FEAT-ADAS-09: RCTA-RCTB (Expanded to 4 sys reqs, 8 sw reqs)
f9 = old_feats["FEAT-ADAS-09"]
f9["sys_reqs"].extend([
    {
        "id": "SYS-ADAS-09-03",
        "title": "Reversing Camera Dynamic Trajectory Overlay & Guidance Bounding Box",
        "asil": "ASIL B",
        "statement": "The System SHALL render dynamic curved trajectory guide lines overlaid on reversing camera video display at 30 fps, highlighting approaching cross-traffic targets with flashing red bounding boxes and directional arrows.",
        "activation": "Active whenever reverse gear is engaged.",
        "ftti": "80 ms",
        "safe_state": "Display raw camera video stream without overlay graphics.",
        "failure_reaction": "If graphics overlay processor crashes, display static guidelines from camera firmware.",
        "inputs": "Rearview_Camera_Video_Stream, Steering_Wheel_Angle_Deg, Cross_Threat_Kinematics",
        "outputs": "Infotainment_Video_Display_Buffer, Cross_Threat_Bounding_Boxes[4]",
        "verification": "Camera frame latency and trajectory alignment testing according to FMVSS 111.",
        "downstream": ["SWR-ADAS-09-05", "SWR-ADAS-09-06"]
    },
    {
        "id": "SYS-ADAS-09-04",
        "title": "Low-Height Obstacle & Bolted Bollard Proximity Clamper",
        "asil": "ASIL B",
        "statement": "The System SHALL detect low-height stationary obstacles (parking bollards, concrete stops, fire hydrants) behind bumper (< 1.5 m) using 4 rear ultrasonic sensors, automatically braking to prevent vehicle bumper damage.",
        "activation": "Active when reversing speed < 10 km/h.",
        "ftti": "50 ms",
        "safe_state": "Clamp brakes; sound continuous parking buzzer tone.",
        "failure_reaction": "Inhibit auto-braking if ultrasonic sensors are covered with snow/ice.",
        "inputs": "Rear_Ultrasonic_Distances_Cm[4], Ego_Reverse_Speed_Mps",
        "outputs": "Ultrasonic_Stop_Brake_Req, Obstacle_Distance_Zone_Enum",
        "verification": "Standard 75 mm low pipe obstacle reverse impact tests."
        ,"downstream": ["SWR-ADAS-09-07", "SWR-ADAS-09-08"]
    }
])
f9["sw_reqs"].extend([
    {
        "id": "SWR-ADAS-09-05",
        "title": "Reversing Dynamic Steering Angle Trajectory Curve Projector",
        "parent": "SYS-ADAS-09-03",
        "asil": "ASIL B",
        "swc": "RctaGuidelineProjector_SWC",
        "period": "33 ms",
        "wcet": "1.2 ms",
        "activation": "Executed on vertical video blanking interval (30 Hz).",
        "algorithm": "Projects vehicle body width W_car and rear axle path: Transforms steering wheel angle delta into instantaneous turning radius R = Wheelbase / tan(delta). Renders perspective-distorted color-coded trajectory lines (Green: > 2m, Yellow: 1-2m, Red: < 1m).",
        "safety_mechanism": "Frame freeze check: If steering angle changes but guidelines remain static for > 100 ms, blanks overlay.",
        "failure_reaction": "Display default straight guidelines if steering sensor is lost.",
        "inputs": "Steering_Wheel_Angle_Deg, Camera_Intrinsic_Calibration_Matrix",
        "outputs": "Overlay_Graphic_Primitives[32], Overlay_Render_Status",
        "verification": "FMVSS 111 rear visibility guideline ground projection grid calibration test."
    },
    {
        "id": "SWR-ADAS-09-06",
        "title": "Cross-Traffic Directional Warning Arrow & Threat Highlighting",
        "parent": "SYS-ADAS-09-03",
        "asil": "ASIL B",
        "swc": "RctaVisualWarning_SWC",
        "period": "20 ms",
        "wcet": "0.4 ms",
        "activation": "Active when lateral cross-traffic detected.",
        "algorithm": "Calculates 2D screen coordinate bounding box for approaching cross-traffic target: Renders flashing red directional indicator arrow pointing left or right, accompanied by pulsing yellow bounding box around threatening vehicle.",
        "safety_mechanism": "Latency budget check: Ensures warning graphic appears on screen within 60 ms of radar target track creation.",
        "failure_reaction": "Suppress arrow if target track disappears.",
        "inputs": "RCTA_Cross_Threat_Left, RCTA_Cross_Threat_Right, Threat_Distance_Meters",
        "outputs": "Screen_Warning_Arrow_State_Enum, Flashing_Alert_Active (boolean)",
        "verification": "User response testing measuring cognitive reaction time to directional visual warnings."
    },
    {
        "id": "SWR-ADAS-09-07",
        "title": "Ultrasonic Echo Time-of-Flight Obstacle Distance Triangulator",
        "parent": "SYS-ADAS-09-04",
        "asil": "ASIL B",
        "swc": "RctaUltrasonicTriangulator_SWC",
        "period": "25 ms",
        "wcet": "0.8 ms",
        "activation": "Cyclic 40 Hz ultrasonic ping task.",
        "algorithm": "Emits 48 kHz ultrasonic chirp pulses across 4 rear bumper transducers. Measures Time-of-Flight (ToF) echoes: Triangulates 2D (x, y) coordinates of stationary objects within 1.8 m. Applies temperature compensation: c_sound = 331.3 * sqrt(1 + T/273.15).",
        "safety_mechanism": "Ground clutter filter: Rejects ground bounce reflections based on echo decay envelope.",
        "failure_reaction": "Flag sensor blind if acoustic reverberation ring-down time exceeds 1.5 ms (indicating mud coating).",
        "inputs": "Ultrasonic_Raw_ToF_Array[4], Ambient_Temperature_DegC",
        "outputs": "Rear_Obstacle_Coordinates_X_Y[4], Closest_Rear_Obstacle_Dist_Cm",
        "verification": "Ultrasonic distance accuracy test across -40°C to +85°C."
    },
    {
        "id": "SWR-ADAS-09-08",
        "title": "Bollard Low-Speed Parking Collision Autonomous Decelerator",
        "parent": "SYS-ADAS-09-04",
        "asil": "ASIL B",
        "swc": "RctaBollardBrake_SWC",
        "period": "10 ms",
        "wcet": "0.4 ms",
        "activation": "Active when reversing towards close obstacle.",
        "algorithm": "Evaluates: If Closest_Rear_Obstacle_Dist_Cm <= 35 cm and Ego_Reverse_Speed > 0.3 km/h, commands immediate full brake deceleration request (-5.0 m/s²), stopping vehicle with 15 cm safety buffer before contact.",
        "safety_mechanism": "Holds brake pressure for 2.0 seconds after stopping, then transfers to EPB park brake.",
        "failure_reaction": "Release brake if driver shifts gear out of REVERSE.",
        "inputs": "Closest_Rear_Obstacle_Dist_Cm, Ego_Reverse_Speed_Mps, Driver_Throttle_Travel_Pct",
        "outputs": "Bollard_Brake_Clamp_Req (boolean), Reversing_Buzzer_Continuous_Tone",
        "verification": "Standard test with steel post bollards and concrete parking curbs."
    }
])
all_feats.append(f9)

# FEAT-ADAS-10: ISA-TSR (Expanded to 4 sys reqs, 8 sw reqs)
f10 = old_feats["FEAT-ADAS-10"]
f10["sys_reqs"].extend([
    {
        "id": "SYS-ADAS-10-03",
        "title": "Electronic Horizon Map Speed Limit Fusion & Conditional Signs",
        "asil": "ASIL A",
        "statement": "The System SHALL fuse optical TSR speed signs with electronic navigation horizon digital map data, correctly resolving conditional speed limits (e.g. 'In Rain', 'Time of Day', 'School Zone', 'Exit 40 km/h') based on vehicle sensors.",
        "activation": "Active whenever vehicle is traveling on mapped public roads.",
        "ftti": "250 ms",
        "safe_state": "Default to general road class speed limit.",
        "failure_reaction": "If conditional condition cannot be verified (e.g. rain sensor uncertain), display both limits on cluster.",
        "inputs": "Camera_Conditional_SubSign_Enum, Rain_Sensor_Status, Clock_Time_OfDay, Navigation_Road_Type",
        "outputs": "Resolved_Active_Speed_Limit_Kmph, Conditional_Sign_Active_Flag",
        "verification": "Euro NCAP Speed Assist Systems conditional sign test catalog.",
        "downstream": ["SWR-ADAS-10-05", "SWR-ADAS-10-06"]
    },
    {
        "id": "SYS-ADAS-10-04",
        "title": "Autonomous Speed Adaptation & Powertrain Torque Soft-Clamping",
        "asil": "ASIL A / EU 2019/2144",
        "statement": "The System SHALL support driver-selectable Intelligent Speed Limiter mode: Automatically restricting maximum powertrain propulsion torque to prevent vehicle speed from exceeding active posted speed limit + tolerance (+-0 to +5 km/h).",
        "activation": "Active when driver enables 'Intelligent Speed Limiter' mode.",
        "ftti": "200 ms",
        "safe_state": "Release torque restriction; allow driver 100% standard accelerator pedal control.",
        "failure_reaction": "Driver accelerator kickdown (> 80% pedal travel) immediately overrides limiter.",
        "inputs": "Resolved_Active_Speed_Limit_Kmph, Driver_Throttle_Pedal_Pct, Actual_Vehicle_Speed_Kmph",
        "outputs": "VCU_Max_Allowable_Torque_Nm, Speed_Limiter_Active_Flag",
        "verification": "EU General Safety Regulation (EU 2019/2144) ISA vehicle type-approval testing.",
        "downstream": ["SWR-ADAS-10-07", "SWR-ADAS-10-08"]
    }
])
f10["sw_reqs"].extend([
    {
        "id": "SWR-ADAS-10-05",
        "title": "Multi-Source Optical & Navigation Map Speed Limit Arbiter",
        "parent": "SYS-ADAS-10-03",
        "asil": "ASIL A",
        "swc": "IsaSpeedArbiter_SWC",
        "period": "100 ms",
        "wcet": "0.8 ms",
        "activation": "Cyclic 100 ms task.",
        "algorithm": "Compares optical camera detected speed V_cam with navigation e-horizon speed V_map: If V_cam detected within past 300 m, V_cam takes priority. If V_cam aged > 1000 m without new signs, seamlessly fades to V_map. Confirms country code speed units (km/h vs mph).",
        "safety_mechanism": "Unit sanity check: Converts mph to km/h when crossing UK/EU borders based on GPS location.",
        "failure_reaction": "Display '---' if neither camera nor map provides valid speed limit.",
        "inputs": "Camera_Speed_Limit_Kmph, Camera_Sign_Age_Meters, Map_Speed_Limit_Kmph, GPS_Country_Code",
        "outputs": "Arbitrated_Speed_Limit_Kmph, Speed_Unit_Enum (kmh/mph)",
        "verification": "Cross-border international road test tracking speed unit transitions."
    },
    {
        "id": "SWR-ADAS-10-06",
        "title": "Weather & Time-Dependent Conditional Sub-Sign Evaluator",
        "parent": "SYS-ADAS-10-03",
        "asil": "ASIL A",
        "swc": "IsaConditionalParser_SWC",
        "period": "200 ms",
        "wcet": "0.6 ms",
        "activation": "Active when supplemental sign plate detected.",
        "algorithm": "Evaluates conditional plate types: 1) 'In Rain' / 'Wet': If wipers ON > 10s, adopts lower limit; 2) 'Time Window' (e.g. 06:00-20:00): Compares with vehicle RTC clock; 3) 'Towing' / 'HGV': Checks trailer hitch connected status.",
        "safety_mechanism": "Failsafe default: In dry weather, displays base speed limit while showing conditional icon in cluster corner.",
        "failure_reaction": "Ignore conditional plate if OCR confidence < 70%.",
        "inputs": "Supplemental_Sign_Type_Enum, Wiper_Active_Flag, RTC_Hour_Minute, Trailer_Attached_Bit",
        "outputs": "Conditional_Limit_Applicable_Flag (boolean), Enforced_Speed_Limit_Kmph",
        "verification": "Euro NCAP wet weather and time-of-day conditional sign test tracks."
    },
    {
        "id": "SWR-ADAS-10-07",
        "title": "Powertrain Propulsion Torque Soft-Limiter Governor",
        "parent": "SYS-ADAS-10-04",
        "asil": "ASIL A",
        "swc": "IsaTorqueLimiter_SWC",
        "period": "10 ms",
        "wcet": "0.5 ms",
        "activation": "Active when Intelligent Speed Limiter mode is engaged.",
        "algorithm": "Monitors vehicle velocity v_ego against speed limit v_limit: When v_ego approaches v_limit - 2 km/h, smoothly ramps down allowable motor torque T_max = T_driver * max(0.0, 1.0 - (v_ego - (v_limit - 2.0)) / 2.0). Prevents vehicle from exceeding limit under engine power.",
        "safety_mechanism": "Downhill braking exclusion: Soft-limiter regulates powertrain propulsion only; does not violently brake downhill unless specified.",
        "failure_reaction": "Release torque cap immediately upon driver kickdown switch.",
        "inputs": "Actual_Vehicle_Speed_Kmph, Enforced_Speed_Limit_Kmph, Driver_Requested_Torque_Nm",
        "outputs": "VCU_Clamped_Torque_Demand_Nm, Torque_Limiting_Active_Flag",
        "verification": "Type-approval test verifying smooth vehicle speed limiting conforming to EU 2019/2144."
    },
    {
        "id": "SWR-ADAS-10-08",
        "title": "Driver Kickdown Override Detector & Limiter Handover",
        "parent": "SYS-ADAS-04-04", # will update to SYS-ADAS-10-04
        "asil": "ASIL A",
        "swc": "IsaKickdownOverride_SWC",
        "period": "10 ms",
        "wcet": "0.3 ms",
        "activation": "Supervises driver throttle pedal.",
        "algorithm": "Detects emergency overtaking intent: If accelerator pedal travel > 85% OR pedal depression rate d(pedal)/dt > 150 %/s, immediately cancels torque clamp in <= 20 ms, releasing 100% full motor power to driver.",
        "safety_mechanism": "Provides brief acoustic chime informing driver that speed limiter has been bypassed.",
        "failure_reaction": "Zero torque restriction if accelerator pedal sensor status is degraded.",
        "inputs": "Accelerator_Pedal_Travel_Pct, Pedal_Rate_Of_Change_Pct_S",
        "outputs": "Kickdown_Override_Active_Flag (boolean), ISA_Suppressed_State",
        "verification": "Emergency highway overtake kickdown response time bench testing."
    }
])
# Fix parent of SWR-ADAS-10-08
f10["sw_reqs"][-1]["parent"] = "SYS-ADAS-10-04"
all_feats.append(f10)

print(f"Total ADAS features compiled: {len(all_feats)}")
total_sys = sum(len(f['sys_reqs']) for f in all_feats)
total_sw = sum(len(f['sw_reqs']) for f in all_feats)
print(f"Total ADAS SysReqs: {total_sys}, Total ADAS SwReqs: {total_sw}")

# Write to features_adas_full.py
code = "# Complete ADAS & Autonomous Driving Domain Features (10 Features)\n\n"
code += "adas_features = " + repr(all_feats) + "\n"
code += 'print(f"Loaded all {len(adas_features)} comprehensive ADAS features.")\n'

with open("features_adas_full.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated features_adas_full.py successfully with all 10 expanded ADAS features!")

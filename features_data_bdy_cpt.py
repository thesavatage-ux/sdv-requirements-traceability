# Body, Lighting, Safety Restraints & Cockpit Sensing Features (Features 18 to 22)

bdy_cpt_features = [
    {
        "id": "FEAT-BDY-01",
        "name": "Passive Entry Passive Start & Digital Key (PEPS)",
        "slug": "PEPS",
        "domain": "Body, Lighting & Restraints",
        "asil": "ASIL B / ISO 21434",
        "summary": "Authenticates smartphone fobs and keyfobs via Bluetooth Low Energy (BLE) and Ultra-Wideband (UWB) IEEE 802.15.4z secure ranging to enable hands-free entry and driveaway authorization.",
        "activation_logic": {
            "preconditions": "12V vehicle battery voltage >= 11.5V, UWB anchor transceiver network synchronized, BCM active.",
            "entry_conditions": "Authorized smartphone or keyfob enters exterior BLE advertising zone (< 15 m) and initiates UWB secure ranging (< 6 m).",
            "states": ["SLEEP_POLLING", "BLE_DISCOVERY", "UWB_RANGING_ACTIVE", "WELCOME_ZONE_UNLOCKED", "CABIN_INTERIOR_CONFIRMED", "IMMOBILIZER_AUTHENTICATED", "WALK_AWAY_LOCKED", "SECURITY_ATTACK_LOCKOUT"],
            "deactivation_conditions": "Key moves outside 2.5 m perimeter for > 2.0s (walk-away lock), or vehicle start button pressed with key validated.",
            "override_behavior": "Physical mechanical emergency key blade in driver door handle unlocks door mechanically in case of dead battery."
        },
        "safety_concept": {
            "safety_goal": "SG-PEPS-01: Prevent unauthorized vehicle unlock or motor startup; protect against relay station attacks.",
            "ftti": "200 ms for entry ranging; 50 ms for start button authorization.",
            "safe_state": "Lock doors; refuse start authorization token to powertrain VCU; lock electronic steering column.",
            "warning_escalation": "Display 'Key Not Detected in Vehicle' on instrument cluster; exterior horn chirp if key is locked inside."
        },
        "failure_behaviors": {
            "relay_attack_detected": "If UWB Time-of-Flight timestamp sequence fails Scrambled Timestamp Sequence (STS) cryptographic integrity, trigger security alert and lockout.",
            "uwb_anchor_failure": "If 1 of 4 exterior UWB anchors fails, continue with 3-anchor trilateration with degraded 25 cm spatial accuracy."
        },
        "sys_reqs": [
            {
                "id": "SYS-BDY-01-01",
                "title": "IEEE 802.15.4z UWB Secure Time-of-Flight Multilateration",
                "asil": "ASIL B / ISO 21434",
                "statement": "The System SHALL compute keyfob 3D Cartesian coordinates relative to vehicle center with < 10 cm spatial accuracy using at least 4 UWB anchor transceivers at <= 50 ms period, verifying cryptographic STS tokens to prevent relay attacks.",
                "activation": "Active when keyfob is within BLE discovery range (< 10 m).",
                "ftti": "100 ms",
                "safe_state": "Invalidate distance estimate; refuse unlock sequence.",
                "failure_reaction": "If distance measurement exhibits negative phase velocity (relay spoofing indicator), trip security lockout.",
                "inputs": "4x_UWB_Transceiver_Packets (SPI), BLE_RSSI_Metrics, STS_Crypto_Noncelist",
                "outputs": "Key_Position_X_Y_Z_Cm, Distance_Integrity_Verified (boolean)",
                "verification": "Anechoic RF chamber relay attack injection test suite.",
                "downstream": ["SWR-BDY-01-01", "SWR-BDY-01-02"]
            },
            {
                "id": "SYS-BDY-01-02",
                "title": "Zone State Automation & Cryptographic Immobilizer Handshake",
                "asil": "ASIL B",
                "statement": "The System SHALL command welcome puddle lights at < 3.0 m, door unlocking at < 1.5 m, walk-away lock at > 2.5 m, and execute an AES-128 challenge-response session to authorize vehicle powertrain start within <= 50 ms of Start Button press.",
                "activation": "Active during vehicle ingress and startup.",
                "ftti": "50 ms",
                "safe_state": "Withhold start authorization token from VCU; maintain immobilizer lock.",
                "failure_reaction": "If challenge-response token mismatch occurs, lock start button for 5.0 seconds.",
                "inputs": "Key_Position_X_Y_Z_Cm, Door_Capacitive_Touch_Sensors, Start_Button_Switch_State",
                "outputs": "BCM_Door_Lock_Motors_PDU, VCU_Start_Authorize_Token",
                "verification": "Vehicle ingress user-experience validation and immobilizer penetration testing.",
                "downstream": ["SWR-BDY-01-03", "SWR-BDY-01-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-BDY-01-01",
                "title": "UWB ToF Spherical Multilateration & Ranging Solver",
                "parent": "SYS-BDY-01-01",
                "asil": "ASIL B",
                "swc": "PepsRanging_SWC",
                "period": "50 ms",
                "wcet": "3.2 ms",
                "activation": "Executed cyclically every 50 ms.",
                "algorithm": "Solves nonlinear least-squares sphere intersection: (x - x_i)^2 + (y - y_i)^2 + (z - z_i)^2 = d_i^2 for i = 1..4 anchors. Computes coordinate residual error; filters position via alpha-beta filter.",
                "safety_mechanism": "Residual error check: If residual norm > 20 cm, discard solution as multipath reflection.",
                "failure_reaction": "Fallback to nearest-anchor RSSI proximity zone if multilateration fails.",
                "inputs": "Anchor_Distance_Mm[4], Anchor_Locations[4]",
                "outputs": "Key_Coordinates_Cm (struct Point3D_t), Position_Confidence_Pct",
                "verification": "Unit test across 500 spatial coordinates surrounding vehicle perimeter."
            },
            {
                "id": "SWR-BDY-01-02",
                "title": "STS Cryptographic Timestamp Random Sequence Verifier",
                "parent": "SYS-BDY-01-01",
                "asil": "ASIL B / ISO 21434",
                "swc": "PepsCryptoSts_SWC",
                "period": "50 ms",
                "wcet": "1.4 ms",
                "activation": "Executed on every incoming UWB pulse frame.",
                "algorithm": "Verifies hardware Scrambled Timestamp Sequence (STS) generated via AES-128 DRBG with shared session key. Validates pulse arrival timestamps matching expected pseudo-random sequence.",
                "safety_mechanism": "Replay prevention: Nonce rolled over every ranging round; timestamp window +-5 ns.",
                "failure_reaction": "Increment security attack counter and log intrusion event upon STS error.",
                "inputs": "STS_Pulse_Data_Buffer, Expected_Session_Key_Handle",
                "outputs": "STS_Authentication_Passed (boolean)",
                "verification": "Cryptographic test with delayed and injected spoofed RF pulses."
            },
            {
                "id": "SWR-BDY-01-03",
                "title": "Geofence Proximity Boundary Finite State Machine",
                "parent": "SYS-BDY-01-02",
                "asil": "QM",
                "swc": "PepsZoneManager_SWC",
                "period": "50 ms",
                "wcet": "0.8 ms",
                "activation": "Executed every 50 ms on key coordinates.",
                "algorithm": "Evaluates Euclidean distance d = sqrt(x^2 + y^2). If d <= 3.0 m: Set Welcome_Lighting = ON. If d <= 1.5 m and Door_Handle_Touched == TRUE: Command Door_Unlock. If d >= 2.5 m for > 2.0s: Command Walk_Away_Lock.",
                "safety_mechanism": "Hysteresis window of 30 cm between lock and unlock thresholds prevents chatter.",
                "failure_reaction": "Inhibit walk-away lock if key coordinates are verified INSIDE vehicle interior.",
                "inputs": "Key_Coordinates_Cm, Door_Handle_Capacitive_State",
                "outputs": "Unlock_Doors_Command (boolean), Lock_Doors_Command (boolean)",
                "verification": "State machine transition test suite."
            },
            {
                "id": "SWR-BDY-01-04",
                "title": "AES-128 Challenge-Response Immobilizer Token Exchanger",
                "parent": "SYS-BDY-01-02",
                "asil": "ASIL B",
                "swc": "PepsImmobilizer_SWC",
                "period": "20 ms",
                "wcet": "4.5 ms",
                "activation": "Executed when Start_Stop_Button is pressed.",
                "algorithm": "Verifies key coordinates fall strictly within cabin polygon bounds. Generates 128-bit random nonce R_car. Keyfob returns Enc_K(R_car). Upon match, transmits Start_Authorize_Token to VCU over SecOC CAN-FD.",
                "safety_mechanism": "Cabin boundary verification prevents vehicle drive-away if key is held by person outside window.",
                "failure_reaction": "Block start authorization if key is located outside interior perimeter.",
                "inputs": "Start_Button_Pressed, Key_Coordinates_Cm, Inbound_Crypto_Token",
                "outputs": "VCU_Start_Authorize_PDU (CAN-FD buffer)",
                "verification": "Boundary penetration tests verifying key detection at window perimeter."
            }
        ]
    },
    {
        "id": "FEAT-BDY-02",
        "name": "Adaptive Driving Beam Matrix Headlights (ADB)",
        "slug": "ADB",
        "domain": "Body, Lighting & Restraints",
        "asil": "ASIL B",
        "summary": "Dynamically carves out glare-free shadow masks around oncoming and leading vehicles using 84 to 1024 LED matrix pixels while maintaining high-beam road illumination elsewhere.",
        "activation_logic": {
            "preconditions": "Vehicle light switch in AUTO, vehicle speed > 30 km/h, ambient light level < 300 lux (night-time).",
            "entry_conditions": "High-beam auto mode activated; forward camera detects target vehicles on road ahead.",
            "states": ["DAYTIME_OFF", "LOW_BEAM_ACTIVE", "FULL_HIGH_BEAM", "MATRIX_SHADOW_CARVING", "URBAN_SPEED_SUPPRESSION", "FAILSAFE_LOW_BEAM"],
            "deactivation_conditions": "Vehicle slows to < 20 km/h, high ambient street lighting detected (> 500 lux), or driver manually switches to low-beam.",
            "override_behavior": "Driver flashing high-beam lever unconditionally commands 100% full high beam illumination."
        },
        "safety_concept": {
            "safety_goal": "SG-ADB-01: Prevent glare to other road users (illuminance at opposing driver eye point <= 1.0 lux) while maximizing driver night visibility.",
            "ftti": "100 ms",
            "safe_state": "Immediately switch all LED pixels to standard low-beam pattern.",
            "warning_escalation": "Display blue high-beam icon with auto 'A' symbol; display yellow lighting fault icon if matrix driver fails."
        },
        "failure_behaviors": {
            "camera_lighting_packet_timeout": "If camera vehicle target stream halts for > 60 ms, drop from matrix mode to standard low beam within 100 ms.",
            "matrix_led_string_short": "If open/short detected on LED string, extinguish affected sector and compensate with adjacent pixels."
        },
        "sys_reqs": [
            {
                "id": "SYS-BDY-02-01",
                "title": "Camera Object Azimuth Angle & Angular Width Tracking",
                "asil": "ASIL B",
                "statement": "The System SHALL compute the horizontal azimuth angle (+-30 deg) and angular bounding box width of all oncoming and leading vehicles with 0.2 deg precision at >= 30 Hz.",
                "activation": "Active at night-time when vehicle speed > 25 km/h.",
                "ftti": "80 ms",
                "safe_state": "Enforce standard low beam cut-off line.",
                "failure_reaction": "If target range is ambiguous, expand shadow mask width by +3.0 degrees safety buffer.",
                "inputs": "Camera_Target_Tracks (Ethernet, 30 Hz), Steering_Wheel_Angle, Vehicle_Speed",
                "outputs": "Shadow_Cutout_Angles[8] (struct Cutout_t), Target_Count",
                "verification": "Night-time photometric glare measurement with goniometer on test track.",
                "downstream": ["SWR-BDY-02-01", "SWR-BDY-02-02"]
            },
            {
                "id": "SYS-BDY-02-02",
                "title": "Individual LED Matrix Pixel PWM Duty Modulation & Slew Limiting",
                "asil": "ASIL B",
                "statement": "The System SHALL modulate current duty cycles across matrix LED pixels (84 to 1024 pixels per headlamp) without visible flicker (PWM frequency >= 1 kHz), transitioning pixels in <= 30 ms.",
                "activation": "Active when matrix high beam is enabled.",
                "ftti": "50 ms",
                "safe_state": "Turn off high-beam matrix LED banks; retain standard low-beam projector.",
                "failure_reaction": "If matrix driver reports over-temperature (> 125°C), derate overall LED current by 40%.",
                "inputs": "Shadow_Cutout_Angles[8], Ambient_Light_Lux, Headlamp_Leveling_Angle",
                "outputs": "Left_Matrix_LED_Duty_Array, Right_Matrix_LED_Duty_Array",
                "verification": "High-speed photometric camera evaluation adhering to SAE J3069 / ECE R123.",
                "downstream": ["SWR-BDY-02-03", "SWR-BDY-02-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-BDY-02-01",
                "title": "Azimuth Angle to LED Pixel Address Grid Transformation",
                "parent": "SYS-BDY-02-01",
                "asil": "ASIL B",
                "swc": "AdbMatrixMapper_SWC",
                "period": "20 ms",
                "wcet": "1.2 ms",
                "activation": "Executed cyclically every 20 ms.",
                "algorithm": "Converts object azimuth angles theta_az into headlamp pixel columns col = f(theta_az, optical_distortion). Adds a +1.5 deg lateral safety margin on both left and right edges to account for vehicle pitching.",
                "safety_mechanism": "Dynamic pitch compensation: Adjusts vertical row cutoff using suspension pitch angle.",
                "failure_reaction": "Expand shadow mask if vehicle traverses road crest or dip.",
                "inputs": "Target_Azimuth_Angles[8], Target_Angular_Widths[8], Suspension_Pitch_Deg",
                "outputs": "Pixel_Mask_Bitmap_Left[32], Pixel_Mask_Bitmap_Right[32]",
                "verification": "Mathematical unit test verifying coordinate transformation matrices."
            },
            {
                "id": "SWR-BDY-02-02",
                "title": "Curvature Swivel & Bending Light Angle Calculator",
                "parent": "SYS-BDY-02-01",
                "asil": "QM",
                "swc": "AdbBendingLight_SWC",
                "period": "20 ms",
                "wcet": "0.6 ms",
                "activation": "Executed every 20 ms.",
                "algorithm": "Computes dynamic curve lighting offset: Theta_swivel = arctan(L_wheelbase * kappa) * K_speed(v_ego). Shifts high-beam illumination center into the inside of highway bends.",
                "safety_mechanism": "Swivel angle limited to maximum +-15 degrees.",
                "failure_reaction": "Center swivel angle to 0 degrees if steering sensor signal is lost.",
                "inputs": "Steering_Angle_Deg, Vehicle_Speed_Mps, Road_Curvature",
                "outputs": "Swivel_Offset_Angle_Deg (float32)",
                "verification": "SIL vehicle dynamics trajectory testing through tight curves."
            },
            {
                "id": "SWR-BDY-02-03",
                "title": "Individual Matrix Pixel Low-Pass Smoothing & Anti-Flicker Filter",
                "parent": "SYS-BDY-02-02",
                "asil": "ASIL B",
                "swc": "AdbLedDriver_SWC",
                "period": "20 ms",
                "wcet": "1.4 ms",
                "activation": "Executed every 20 ms on Pixel_Mask_Bitmaps.",
                "algorithm": "Interpolates 8-bit pixel brightness values. Applies exponential low-pass filter: Duty[k] = Duty[k-1] + alpha * (Target_Duty - Duty[k-1]) with tau = 20 ms to provide smooth, organic light dimming.",
                "safety_mechanism": "Ensures extinguishing pixels dim faster (tau = 10 ms) than illuminating pixels (tau = 30 ms) to avoid glare.",
                "failure_reaction": "Force immediate zero duty on affected pixels if glare flag is set.",
                "inputs": "Pixel_Mask_Bitmap_Left, Pixel_Mask_Bitmap_Right",
                "outputs": "LED_Duty_Cycles_Left[128], LED_Duty_Cycles_Right[128]",
                "verification": "Photometric high-speed camera flicker test."
            },
            {
                "id": "SWR-BDY-02-04",
                "title": "Matrix Driver SPI Frame Serializer & Open-Load Diagnostic",
                "parent": "SYS-BDY-02-02",
                "asil": "ASIL B",
                "swc": "AdbHardwareInterface_SWC",
                "period": "10 ms",
                "wcet": "0.8 ms",
                "activation": "Executed at 100 Hz.",
                "algorithm": "Formats serial data frames over high-speed CAN-FD / SPI to headlamp matrix LED drivers. Reads back open-load and short-circuit diagnostic status bytes. Inverts pixel duty if thermal limit reached.",
                "safety_mechanism": "Parity bit and checksum protection on serial communication lines.",
                "failure_reaction": "Report DTC B1452 if open circuit detected on matrix string.",
                "inputs": "LED_Duty_Cycles_Left, LED_Duty_Cycles_Right, Diagnostic_Feedback_Bytes",
                "outputs": "Headlamp_SPI_Tx_Buffer, Headlamp_Diagnostic_Status_Enum",
                "verification": "Electrical harness fault injection testing on headlamp bench."
            }
        ]
    },
    {
        "id": "FEAT-BDY-03",
        "name": "Supplemental Restraint System & Airbag Deployment (SRS)",
        "slug": "SRS",
        "domain": "Body, Lighting & Restraints",
        "asil": "ASIL D",
        "summary": "Processes high-G crash accelerometers and pressure sensors to trigger squib deployment of frontal airbags, side curtains, pretensioners, and high-voltage pyrofuses in <= 15 ms.",
        "activation_logic": {
            "preconditions": "Ignition in RUN, airbag capacitor energy reserve charged (> 25V), occupant classification sensors healthy.",
            "entry_conditions": "Crash deceleration impulse delta_v exceeds calibrated deployment threshold.",
            "states": ["SELF_TEST_HEALTHY", "PRE_CRASH_ARMED", "STAGE_1_BELT_TENSION", "STAGE_2_AIRBAG_FIRE", "CRASH_RECORD_STORED", "FAULT_LOCKED"],
            "deactivation_conditions": "Deployment squibs fired (permanent state) or power down.",
            "override_behavior": "Passenger airbag manual disable switch (or baby seat detected) suppresses passenger frontal airbag deployment."
        },
        "safety_concept": {
            "safety_goal": "SG-SRS-01: Guarantee airbag squib deployment within 15 ms during severe crash; absolutely prevent inadvertent deployment during normal driving or pothole impacts.",
            "ftti": "5 ms",
            "safe_state": "Hardware arming safing sensor prevents firing unless independent mechanical/MEMS safing sensor confirms crash.",
            "warning_escalation": "Airbag red warning lamp permanently illuminated if any squib loop has open or short circuit."
        },
        "failure_behaviors": {
            "inadvertent_fire_prevention": "Hardware dual-switched squibs (High-Side Switch + Low-Side Switch) require BOTH software microcontroller AND independent hardware safing sensor to conduct simultaneously.",
            "power_loss_during_crash": "Internal reservoir capacitors maintain sufficient electrical energy to deploy all squibs for at least 150 ms following 12V battery severing."
        },
        "sys_reqs": [
            {
                "id": "SYS-BDY-03-01",
                "title": "Dual-Axis Crash Pulse Integration & Velocity Change (Delta-V) Calculation",
                "asil": "ASIL D",
                "statement": "The System SHALL sample crash accelerometers (+-100g front, +-50g lateral, door cavity pressure) at 4 kHz (<= 0.25 ms), integrating deceleration into crash velocity change (Delta-V) and crash severity index within <= 10 ms.",
                "activation": "Active at all times while vehicle is powered.",
                "ftti": "2 ms",
                "safe_state": "Do not fire squibs; assert airbag warning lamp.",
                "failure_reaction": "If one crash sensor fails self-test, fallback to redundant centralized tunnel sensor.",
                "inputs": "2x_Front_Crash_Sensors, 2x_Side_Pressure_Sensors, Central_High_G_IMU",
                "outputs": "Crash_Delta_V_Mps, Crash_Severity_Index (uint8), Crash_Type_Enum",
                "verification": "Crash barrier barrier-impact sled testing across FMVSS 208 and 214 protocols.",
                "downstream": ["SWR-BDY-03-01", "SWR-BDY-03-02"]
            },
            {
                "id": "SYS-BDY-03-02",
                "title": "Hardware Safing Interlock & Multi-Stage Squib Deployment",
                "asil": "ASIL D",
                "statement": "The System SHALL fire squib loops (driver/passenger frontal, curtain, knee, seatbelt pretensioners, HV pyrofuse) with firing current >= 1.75 A for >= 2.0 ms only when hardware safing sensor AND software algorithm agree within <= 2 ms.",
                "activation": "Active upon crash threshold exceedance.",
                "ftti": "2 ms",
                "safe_state": "Keep high-side squib drivers open.",
                "failure_reaction": "If squib loop resistance deviates outside [1.8, 2.5] ohms during self-test, report squib loop fault.",
                "inputs": "Crash_Severity_Index, Hardware_Safing_Sensor_State, Occupant_Classification_Weight",
                "outputs": "Squib_Firing_Lines[16], HV_Battery_Pyrofuse_Trigger, ECall_Activation_PDU",
                "verification": "Hardware squib fire timing bench testing with dummy pyrotechnic loads.",
                "downstream": ["SWR-BDY-03-03", "SWR-BDY-03-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-BDY-03-01",
                "title": "4 kHz Crash Acceleration Integration & Delta-V Computation",
                "parent": "SYS-BDY-03-01",
                "asil": "ASIL D",
                "swc": "SrsCrashDiscrimination_SWC",
                "period": "1 ms",
                "wcet": "0.25 ms",
                "activation": "Executed in high-speed timer interrupt.",
                "algorithm": "Samples high-G acceleration a(t). Integrates velocity delta: Delta_V(t) = int(a(t) - a_bias dt). Computes displacement: s(t) = int(Delta_V dt). Evaluates against calibration velocity-displacement fire boundary curves.",
                "safety_mechanism": "Rough road / curb strike discriminator rejects high-frequency non-crash shocks.",
                "failure_reaction": "If raw acceleration exceeds 120g without velocity impulse, flag sensor clipping.",
                "inputs": "Raw_HighG_Accel_X, Raw_HighG_Accel_Y, Lateral_Pressure_Sensor",
                "outputs": "Integrated_Delta_V_Mps (float32), Fire_Algorithm_Decision (boolean)",
                "verification": "Crash pulse playback unit test across 250 real-world crash logs."
            },
            {
                "id": "SWR-BDY-03-02",
                "title": "Occupant Classification & Child Seat Suppression Filter",
                "parent": "SYS-BDY-03-01",
                "asil": "ASIL D",
                "swc": "SrsOccupantClassifier_SWC",
                "period": "100 ms",
                "wcet": "0.8 ms",
                "activation": "Executed every 100 ms.",
                "algorithm": "Reads passenger seat strain-gauge weight sensor. If weight < 15 kg (child seat detected) OR Passenger_Airbag_Manual_Sw == OFF: Passenger_Front_Airbag_Suppressed = TRUE.",
                "safety_mechanism": "Hysteresis weight filtering prevents seat movement while driving from toggling state.",
                "failure_reaction": "Default to AIRBAG ENABLED if weight sensor communication is lost.",
                "inputs": "Seat_Weight_Sensor_Kg, Manual_Airbag_Switch_State",
                "outputs": "Passenger_Airbag_Suppressed_Flag (boolean)",
                "verification": "Occupant weight sensor calibration and suppression test suite."
            },
            {
                "id": "SWR-BDY-03-03",
                "title": "Hardware Safing Logic AND-Gate Software Supervision",
                "parent": "SYS-BDY-03-02",
                "asil": "ASIL D",
                "swc": "SrsSafingMonitor_SWC",
                "period": "1 ms",
                "wcet": "0.15 ms",
                "activation": "Executed in crash interrupt routine.",
                "algorithm": "Reads independent hardware safing sensor line. Computes: Squib_Arm_Permit = (Fire_Algorithm_Decision == TRUE) && (Hardware_Safing_Line == CLOSED). High-side drivers cannot close without this condition.",
                "safety_mechanism": "Complete electrical isolation between MCU software trigger and safing sensor hardware path.",
                "failure_reaction": "Immediately de-assert squib drivers if safing sensor line goes OPEN.",
                "inputs": "Fire_Algorithm_Decision, Hardware_Safing_Sensor_State",
                "outputs": "Squib_Arm_Permit (boolean)",
                "verification": "Fault injection testing proving zero fire output when either signal is missing."
            },
            {
                "id": "SWR-BDY-03-04",
                "title": "Squib Firing Pulse Sequencer & Crash Record Non-Volatile Freeze",
                "parent": "SYS-BDY-03-02",
                "asil": "ASIL D",
                "swc": "SrsSquibSequencer_SWC",
                "period": "1 ms",
                "wcet": "0.3 ms",
                "activation": "Executed upon confirmed fire trigger.",
                "algorithm": "Sequences firing pulses: t=0ms (Belt Pretensioners & Pyrofuse); t=5ms (Stage 1 Front Airbags & Curtains); t=15ms (Stage 2 Front Airbags). Writes crash event recording to locked non-volatile flash (EDR).",
                "safety_mechanism": "Hardware one-way programmable lock prevents overwriting Event Data Recorder (EDR) crash data.",
                "failure_reaction": "Broadcast emergency high-priority crash broadcast over CAN-FD and dispatch eCall.",
                "inputs": "Squib_Arm_Permit, Crash_Severity_Index",
                "outputs": "Squib_Output_Drivers[16], EDR_Flash_Write_Trigger, Crash_CAN_Broadcast_PDU",
                "verification": "EDR compliance verification against 49 CFR Part 563."
            }
        ]
    },
    {
        "id": "FEAT-CPT-01",
        "name": "Driver Monitoring & Cabin Sensing (DMS/OMS)",
        "slug": "DMS",
        "domain": "Digital Cockpit, HMI & Cabin Sensing",
        "asil": "ASIL B",
        "summary": "Monitors driver gaze, eye closure (PERCLOS), head orientation, and cabin occupant presence (child left behind detection) using near-infrared cameras and 60 GHz radar.",
        "activation_logic": {
            "preconditions": "12V system active, cabin NIR camera stream running at 30 fps, cockpit domain controller healthy.",
            "entry_conditions": "Vehicle ignition in RUN, or vehicle parked with doors locked (for Occupant Child Left Behind detection).",
            "states": ["CABIN_SCANNING", "ATTENTIVE_DRIVING", "DISTRACTED_LEVEL_1", "DISTRACTED_LEVEL_2", "DROWSINESS_ALERT", "CHILD_LEFT_BEHIND_ALARM", "CAMERA_OCCLUSION"],
            "deactivation_conditions": "Driver monitoring inactive when ignition is completely OFF and vehicle unlocked.",
            "override_behavior": "Driver gaze return to road forward cone for > 1.5s immediately clears distraction warning state."
        },
        "safety_concept": {
            "safety_goal": "SG-DMS-01: Detect driver microsleep or eyes-off-road inattention within 2.5 seconds; detect unattended child in parked vehicle.",
            "ftti": "500 ms",
            "safe_state": "Report DMS_Status = DEGRADED to ADAS; disallow Level 2/3 hands-free automated driving modes.",
            "warning_escalation": "Visual prompt on Cluster -> Audio chime -> Haptic seat vibration -> ADAS brake tap."
        },
        "failure_behaviors": {
            "camera_lens_blocked": "If driver covers lens or heavy dirt accumulates, detect occlusion in < 5s and prompt 'Clean Driver Camera'.",
            "sunglasses_occlusion": "If polarized infrared-blocking sunglasses worn, fallback from pupil gaze tracking to 3D head pose orientation."
        },
        "sys_reqs": [
            {
                "id": "SYS-CPT-01-01",
                "title": "3D Head Pose & Eyelid Closure (PERCLOS) Real-Time Inference",
                "asil": "ASIL B",
                "statement": "The System SHALL track driver eye gaze vector (+-10 deg accuracy), head pose (pitch, yaw, roll +-5 deg), and compute PERCLOS metric at >= 30 fps under day, night, and sunglasses conditions.",
                "activation": "Active while vehicle speed > 15 km/h.",
                "ftti": "250 ms",
                "safe_state": "Set Driver_Attentive_Flag = FALSE; alert ADAS.",
                "failure_reaction": "If facial landmarks lost for > 2.0 seconds, trigger driver attentiveness check.",
                "inputs": "NIR_Camera_Video_Feed (MIPI-CSI, 30 fps, 1080p), NIR_LED_Illuminator_Status",
                "outputs": "Driver_Gaze_Vector_XYZ, Head_Pose_Pitch_Yaw_Roll, PERCLOS_Drowsiness_Score",
                "verification": "Euro NCAP Driver Monitoring Assessment protocol test dataset.",
                "downstream": ["SWR-CPT-01-01", "SWR-CPT-01-02"]
            },
            {
                "id": "SYS-CPT-01-02",
                "title": "Parked Vehicle Child Presence Detection & Alarm Escalation",
                "asil": "ASIL B",
                "statement": "The System SHALL scan passenger cabin using 60 GHz in-cabin radar and camera within 60 seconds of vehicle locking to detect sub-millimeter chest movements of sleeping infants, escalating honk and cellular alerts.",
                "activation": "Active after driver exits, locks vehicle, and walks away.",
                "ftti": "5000 ms",
                "safe_state": "Crack open power windows by 3 cm; activate maximum blower fan; notify owner smartphone.",
                "failure_reaction": "If radar sensor self-test fails, notify owner via mobile app of cabin sensor failure.",
                "inputs": "Cabin_Radar_MicroDoppler_Stream, Door_Lock_Confirmation, Cabin_Temp_C",
                "outputs": "Child_Detected_Flag (boolean), Cellular_Emergency_Alert_Req, Alarm_Horn_Chirp_Cmd",
                "verification": "Euro NCAP Child Presence Detection (CPD) testing with breathing mannequin.",
                "downstream": ["SWR-CPT-01-03", "SWR-CPT-01-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-CPT-01-01",
                "title": "Facial Landmark & Eye Aspect Ratio (EAR) Neural Network Pipeline",
                "parent": "SYS-CPT-01-01",
                "asil": "ASIL B",
                "swc": "DmsFaceTracker_SWC",
                "period": "33 ms",
                "wcet": "16.5 ms (NPU)",
                "activation": "Executed on every incoming NIR frame.",
                "algorithm": "Detects 68 3D facial landmarks using MobileNet-backbone CNN. Computes Eye Aspect Ratio: EAR = (||p2 - p6|| + ||p3 - p5||)/(2 * ||p1 - p4||). EAR < 0.21 indicates closed eyelid. Integrates eye closure over 60s window for PERCLOS.",
                "safety_mechanism": "Confidence score filtering: Landmark updates rejected if bounding box score < 0.70.",
                "failure_reaction": "Fallback to head pose orientation if eyes obscured by dark lenses.",
                "inputs": "NIR_Video_Frame_Buffer",
                "outputs": "Driver_EAR_Score, Driver_PERCLOS_Score, Facial_Tracking_Confidence",
                "verification": "Benchmark testing against 100,000 annotated driver facial video sequences."
            },
            {
                "id": "SWR-CPT-01-02",
                "title": "Attention Cone & Drowsiness Multi-Stage Escalation Supervisor",
                "parent": "SYS-CPT-01-01",
                "asil": "ASIL B",
                "swc": "DmsDistractionSupervisor_SWC",
                "period": "50 ms",
                "wcet": "0.9 ms",
                "activation": "Executed every 50 ms.",
                "algorithm": "Maps gaze vector to forward road cone (yaw in [-15, +15] deg, pitch in [-10, +10] deg). Distraction Timer increments when gaze outside cone. At 2.5s: Trigger Level 1 chime. At 4.0s: Trigger Level 2 haptic alert and ADAS warning.",
                "safety_mechanism": "Speed dependency: Escalation thresholds tightened by 30% if vehicle speed > 100 km/h.",
                "failure_reaction": "If camera blinded, prompt driver to wipe interior camera lens.",
                "inputs": "Driver_Gaze_Vector_XYZ, Driver_PERCLOS_Score, Vehicle_Speed_Kmph",
                "outputs": "DMS_Distraction_Alert_Level (uint8), DMS_Drowsiness_Alert_Level (uint8)",
                "verification": "Driver simulator subjective distraction test suite."
            },
            {
                "id": "SWR-CPT-01-03",
                "title": "60 GHz FMCW In-Cabin Micro-Doppler Respiration Detector",
                "parent": "SYS-CPT-01-02",
                "asil": "ASIL B",
                "swc": "OmsRadarBreathing_SWC",
                "period": "100 ms",
                "wcet": "4.2 ms",
                "activation": "Executed when vehicle is locked and parked.",
                "algorithm": "Processes 60 GHz radar Range-Doppler matrices. Extracts phase variation corresponding to sub-millimeter chest wall movements in 0.2 to 0.7 Hz range (12 to 42 breaths per minute).",
                "safety_mechanism": "Motion discrimination: Distinguishes living breathing infant from inanimate swaying object.",
                "failure_reaction": "If radar signal noisy, cross-reference cabin PIR motion sensor.",
                "inputs": "Radar_Range_Doppler_FFT_Buffer",
                "outputs": "Respiration_Rate_Bpm (float32), Living_Subject_Detected (boolean)",
                "verification": "Medical test bench with calibrated mechanical infant lung simulator."
            },
            {
                "id": "SWR-CPT-01-04",
                "title": "Child Left Behind Hot-Cabin Alarm & Window Vent Dispatcher",
                "parent": "SYS-CPT-01-02",
                "asil": "ASIL B",
                "swc": "OmsChildAlertManager_SWC",
                "period": "500 ms",
                "wcet": "0.8 ms",
                "activation": "Executed when Living_Subject_Detected == TRUE in parked vehicle.",
                "algorithm": "If child detected for > 60s: Dispatches push notification to owner phone. If cabin temperature > 32°C: Commands power windows open by 3 cm, sounds vehicle horn alarm, and dials emergency telematics.",
                "safety_mechanism": "Window vent height restricted to 3 cm to prevent unauthorized exterior reach-in.",
                "failure_reaction": "Escalate to continuous alarm if temperature exceeds 38°C.",
                "inputs": "Living_Subject_Detected, Cabin_Temperature_C, Vehicle_Lock_State",
                "outputs": "Telematics_Child_Alarm_Req, BCM_Window_Vent_Cmd, Horn_Alarm_Cmd",
                "verification": "Test chamber heat-up scenario evaluating emergency alert latency."
            }
        ]
    },
    {
        "id": "FEAT-CPT-02",
        "name": "Augmented Reality Head-Up Display (AR-HUD)",
        "slug": "HUD",
        "domain": "Digital Cockpit, HMI & Cabin Sensing",
        "asil": "ASIL B",
        "summary": "Projects conformal optical graphics (navigation arrows, ADAS target boxes, lane boundaries) onto windshield at 10-meter virtual focal distance.",
        "activation_logic": {
            "preconditions": "12V system healthy, HUD optical picture generating unit (PGU) temperature normal, windshield projection mirror calibrated.",
            "entry_conditions": "Ignition in RUN; driver enables HUD in cockpit display settings.",
            "states": ["OFF", "HOMING_ALIGNMENT", "ACTIVE_PROJECTION", "BRIGHTNESS_ADAPTING", "THERMAL_DERATING", "FAULT_SHUTDOWN"],
            "deactivation_conditions": "Driver toggles HUD OFF or ignition powered down.",
            "override_behavior": "Driver can adjust virtual image height and rotation via steering wheel buttons."
        },
        "safety_concept": {
            "safety_goal": "SG-HUD-01: Prevent visual obstruction of driver forward road view; ensure graphics align accurately with real-world objects (< 1.0 deg error).",
            "ftti": "100 ms",
            "safe_state": "Immediately turn off PGU laser/TFT backlight to extinguish projected image.",
            "warning_escalation": "Display 'Head-Up Display Unavailable' message on primary instrument cluster."
        },
        "failure_behaviors": {
            "pgu_overtemperature": "If PGU optical engine temp > 85°C, reduce backlight brightness by 50%; if > 95°C, shut off projection.",
            "misalignment": "If camera ego-pose estimation diverges, disable AR conformal overlays and revert to static 2D speed digits."
        },
        "sys_reqs": [
            {
                "id": "SYS-CPT-02-01",
                "title": "Low-Latency Ego-Motion Graphic Conformal Alignment",
                "asil": "ASIL B",
                "statement": "The System SHALL render navigation arrows and ADAS hazard bounding boxes conformally aligned with real-world geometry (< 0.5 deg alignment error) with motion-to-photon latency <= 30 ms at 60 fps.",
                "activation": "Active during driving.",
                "ftti": "60 ms",
                "safe_state": "Blank optical display if graphic lag exceeds 50 ms.",
                "failure_reaction": "Revert to simple static numeric speed display if AR pose tracker faults.",
                "inputs": "Camera_Lane_Polynomials, ADAS_Target_Boxes, Navigation_Maneuver_Point, IMU_HighRate",
                "outputs": "HUD_Video_Stream (DisplayPort / FPD-Link III, 60 fps, 1920x1080)",
                "verification": "Motion-to-photon optical high-speed camera latency bench test.",
                "downstream": ["SWR-CPT-02-01", "SWR-CPT-02-02"]
            },
            {
                "id": "SYS-CPT-02-02",
                "title": "Ambient Light Ambient Adaptation & Solar Thermal Protection",
                "asil": "ASIL B",
                "statement": "The System SHALL adjust HUD projection luminance from 100 nits (night) to 15,000 nits (direct snow sunlight) in <= 200 ms, while monitoring cold-mirror thermal sensor to prevent sun-burn damage to TFT panel.",
                "activation": "Active whenever HUD is projecting.",
                "ftti": "200 ms",
                "safe_state": "Close motorized optical glare trap shutter if solar thermal risk detected.",
                "failure_reaction": "If ambient lux sensor fails, set brightness to safe default 3,000 nits.",
                "inputs": "Forward_Facing_Lux_Sensor, PGU_Thermal_Thermistor_C, Windshield_Solar_Angle",
                "outputs": "HUD_Backlight_Current_Cmd, Shutter_Solenoid_Cmd",
                "verification": "Solar radiation simulation chamber test evaluating thermal resistance.",
                "downstream": ["SWR-CPT-02-03", "SWR-CPT-02-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-CPT-02-01",
                "title": "Low-Latency Pose Extrapolation & Windshield Optical Distortion Shader",
                "parent": "SYS-CPT-02-01",
                "asil": "ASIL B",
                "swc": "HudRenderEngine_SWC",
                "period": "16 ms",
                "wcet": "8.5 ms (GPU)",
                "activation": "Executed at 60 Hz frame synchronization interrupt.",
                "algorithm": "Predicts vehicle pose at photon display timestamp t_photon = t_now + 25ms using high-rate IMU integration. Applies 3D vertex mesh warp correcting windshield curved glass optical distortion.",
                "safety_mechanism": "Frame freeze detector: Checks heartbeat counter in rendered buffer; blanks display if GPU hangs.",
                "failure_reaction": "Blank AR overlay layer if frame rendering time exceeds 16.6 ms.",
                "inputs": "IMU_Angular_Rates, Projected_Vehicle_Pose, AR_World_Coordinates",
                "outputs": "Distortion_Corrected_Frame_Buffer",
                "verification": "Optical grid distortion test on curved automotive windshield fixture."
            },
            {
                "id": "SWR-CPT-02-02",
                "title": "Eye-Box Driver Pupil Height Dynamic Tracking Adjustment",
                "parent": "SYS-CPT-02-01",
                "asil": "QM",
                "swc": "HudEyeboxManager_SWC",
                "period": "50 ms",
                "wcet": "0.7 ms",
                "activation": "Executed every 50 ms.",
                "algorithm": "Receives driver eye coordinates from DMS camera. Drives motorized aspheric mirror stepper motor to shift HUD optical eye-box (+-30 mm vertical) so virtual image is perfectly visible to driver.",
                "safety_mechanism": "Stepper motor limits bounded to prevent optical mechanism gear stripping.",
                "failure_reaction": "Hold mirror in last known good position if eye tracking data is lost.",
                "inputs": "Driver_Eye_Height_Mm (from DMS), Manual_HUD_Height_Offset",
                "outputs": "HUD_Mirror_Stepper_Motor_Steps (int16)",
                "verification": "Anthropometric driver eye-box alignment testing."
            },
            {
                "id": "SWR-CPT-02-03",
                "title": "High-Dynamic-Range (HDR) Ambient Light Dimming Curve",
                "parent": "SYS-CPT-02-02",
                "asil": "QM",
                "swc": "HudBrightness_SWC",
                "period": "50 ms",
                "wcet": "0.4 ms",
                "activation": "Executed every 50 ms.",
                "algorithm": "Interpolates target luminance L_target = f(Ambient_Lux) across 5 decades of dynamic range (1 to 100,000 lux). Applies logarithmic human eye response filter to prevent glare when entering tunnels.",
                "safety_mechanism": "Maximum brightness clamped in tunnel/night mode to prevent blinding driver night vision.",
                "failure_reaction": "Default to 3,000 nits if ambient sensor disconnected.",
                "inputs": "Ambient_Light_Lux, Tunnel_Detection_Flag",
                "outputs": "PGU_Backlight_PWM_Duty (uint16)",
                "verification": "Tunnel entrance and exit dynamic lighting response test."
            },
            {
                "id": "SWR-CPT-02-04",
                "title": "Solar Burn Concentration Thermistor & Trap Shutter Guard",
                "parent": "SYS-CPT-02-02",
                "asil": "ASIL B",
                "swc": "HudThermalGuard_SWC",
                "period": "100 ms",
                "wcet": "0.3 ms",
                "activation": "Executed every 100 ms.",
                "algorithm": "Monitors internal cold mirror temperature. If direct solar focus concentrates > 1.2 kW/m² optical power on display engine, sets Shutter_Close_Req = TRUE to deploy physical solar shield.",
                "safety_mechanism": "Mechanical spring-return shutter closes automatically on power loss.",
                "failure_reaction": "Report DTC B1891 if internal mirror thermistor exceeds 95°C.",
                "inputs": "PGU_Mirror_Temp_C, Solar_Elevation_Angle_Deg",
                "outputs": "Shutter_Close_Req (boolean), Overheat_Derate_State",
                "verification": "Solar concentrator thermal stress testing on PGU display panel."
            }
        ]
    }
]

print(f"Loaded all {len(bdy_cpt_features)} Body & Cockpit features successfully.")

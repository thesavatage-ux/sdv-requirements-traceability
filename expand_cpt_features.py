# expand_cpt_features.py
import features_cpt_full

old_feats = {f["id"]: f for f in features_cpt_full.full_cpt_features}

# FEAT-CPT-01: DMS/OMS (Expanded to 5 sys reqs, 10 sw reqs)
f1 = old_feats["FEAT-CPT-01"]
f1["sys_reqs"].extend([
    {
        "id": "SYS-CPT-01-03",
        "title": "Cabin 60 GHz Millimeter-Wave Radar Child Presence Detection (CPD)",
        "asil": "ASIL B / Euro NCAP",
        "statement": "The System SHALL sample cabin roof-mounted 60 GHz FMCW radar at 20 Hz, detecting micro-movements of breathing (sub-millimeter chest displacement 0.2 to 0.5 Hz) to detect unattended infants/children covered under blankets in <= 10 seconds of vehicle key-off.",
        "activation": "Active upon driver leaving vehicle and locking doors.",
        "ftti": "2000 ms",
        "safe_state": "Lower windows 2 cm; trigger external horn chirp; send emergency smartphone push notification.",
        "failure_reaction": "If radar sensor reports RF fault, fallback to interior ultrasonic intrusion sensor.",
        "inputs": "Cabin_60GHz_Radar_Range_Doppler_Map, All_Doors_Locked_Bit, Ambient_Cabin_Temp_DegC",
        "outputs": "Child_Presence_Detected_Flag, Infant_Breathing_Rate_BPM, CPD_Alarm_Trigger_Req",
        "verification": "Euro NCAP Child Presence Detection protocol tests with pediatric breathing simulator mannequins.",
        "downstream": ["SWR-CPT-01-05", "SWR-CPT-01-06"]
    },
    {
        "id": "SYS-CPT-01-04",
        "title": "Driver Cognitive Distraction & Handheld Mobile Phone Usage Classifier",
        "asil": "ASIL A",
        "statement": "The System SHALL track driver hand pose and facial gaze vectors: If driver is holding mobile phone to ear or texting while vehicle speed > 10 km/h for > 2.5 seconds, system SHALL trigger Level 1 visual and Level 2 acoustic distraction warnings.",
        "activation": "Active at all vehicle driving speeds.",
        "ftti": "500 ms",
        "safe_state": "Display amber distraction prompt on instrument cluster.",
        "failure_reaction": "Suppress false alarms if driver is wearing sunglasses by relying on hand-to-ear skeletal pose.",
        "inputs": "Camera_Skeleton_Hand_Keypoints, Gaze_Direction_Yaw_Pitch, Phone_Object_Bounding_Box",
        "outputs": "Driver_Phone_Distraction_Flag, Distraction_Duration_Sec, Cluster_Distraction_Alert_Cmd",
        "verification": "Driver naturalistic driving distraction video benchmark tests.",
        "downstream": ["SWR-CPT-01-07", "SWR-CPT-01-08"]
    },
    {
        "id": "SYS-CPT-01-05",
        "title": "Driver Medical Incapacitation & Emergency Safe Stop Coordinator",
        "asil": "ASIL D",
        "statement": "The System SHALL continuously monitor driver responsiveness: If driver head slumps forward (pitch < -40 deg) with eyes closed for > 4.0 seconds and zero hands on steering wheel, system SHALL declare Driver_Incapacitated, initiating autonomous in-lane stop and emergency hazard beacon.",
        "activation": "Active during all driving modes.",
        "ftti": "200 ms",
        "safe_state": "Bring vehicle to controlled stop; unlock doors; initiate eCall medical alert.",
        "failure_reaction": "Cancel emergency stop immediately if driver lifts head and steers wheel.",
        "inputs": "Head_Pose_Pitch_Roll_Yaw, Eye_Closure_Duration_Sec, Capacitive_Steering_Hands_On_Flag",
        "outputs": "Driver_Incapacitation_Confirmed_Flag, Emergency_Stop_Maneuver_Trigger",
        "verification": "Medical emergency simulated driver collapse evaluations on test track.",
        "downstream": ["SWR-CPT-01-09", "SWR-CPT-01-10"]
    }
])
f1["sw_reqs"].extend([
    {
        "id": "SWR-CPT-01-05",
        "title": "60 GHz FMCW Radar Micro-Doppler Vital Signs Extractor",
        "parent": "SYS-CPT-01-03",
        "asil": "ASIL B",
        "swc": "CpdRadarVitalSigns_SWC",
        "period": "50 ms",
        "wcet": "2.2 ms",
        "activation": "Executed when vehicle is locked.",
        "algorithm": "Applies 2D-FFT on raw FMCW beat signal: Extracts range-Doppler map. Performs Phase Unwrap on target range bins: Detects micro-motion phase shift Delta_phi = 4*pi*Delta_r / lambda. Bandpass filters between 0.15 Hz and 0.8 Hz to isolate pediatric respiration.",
        "safety_mechanism": "Rejects false motion (swaying air fresheners or wind drafts) via Doppler energy dispersion.",
        "failure_reaction": "Retry scan across all rear seating zones if initial sweep is inconclusive.",
        "inputs": "Raw_FMCW_Chirp_IQ_Samples[1024], Cabin_Temperature_DegC",
        "outputs": "Respiratory_Rate_BPM, Target_Chest_Displacement_Mm, Infant_Detected_Probability",
        "verification": "Pediatric medical mannequin breathing simulation tests under heavy blankets."
    },
    {
        "id": "SWR-CPT-01-06",
        "title": "Child Presence Detection Multi-Tier Escalation Coordinator",
        "parent": "SYS-CPT-01-03",
        "asil": "ASIL B",
        "swc": "CpdAlarmCoordinator_SWC",
        "period": "100 ms",
        "wcet": "0.4 ms",
        "activation": "Active on Infant_Detected_Probability > 85%.",
        "algorithm": "Executes staged emergency response: Stage 1 (0-15s): Sends urgent push notification and SMS to user smartphone; Stage 2 (15-45s): Flashes vehicle hazard lamps and chirps exterior horn; Stage 3 (> 45s or cabin temp > 35°C): Cracks open all windows by 25 mm, turns on HVAC blower fan, and dispatches telematics emergency alert.",
        "safety_mechanism": "Cabin heatstroke prevention: Accelerates escalation directly to Stage 3 if interior temperature exceeds 35°C.",
        "failure_reaction": "Engage maximum alarm horn if cellular network is unavailable.",
        "inputs": "Infant_Detected_Probability, Cabin_Temperature_DegC, Alarm_Timer_Sec",
        "outputs": "BCM_Window_Vent_Cmd, BCM_Horn_Alarm_Pattern, Telematics_CPD_Emergency_Call",
        "verification": "Hot car thermal chamber deployment test validating window venting and alarm trigger."
    },
    {
        "id": "SWR-CPT-01-07",
        "title": "Handheld Mobile Phone Object Detection & Keypoint Saliency Net",
        "parent": "SYS-CPT-01-04",
        "asil": "ASIL A",
        "swc": "DmsPhoneDetector_SWC",
        "period": "50 ms",
        "wcet": "3.5 ms",
        "activation": "Cyclic 50 ms vision task.",
        "algorithm": "Runs lightweight convolutional neural network detecting rectangular mobile devices in cabin. Computes spatial Euclidean distance between detected phone bounding box and driver head/ear keypoints. If distance < 12 cm for > 2.0s, flags Handheld_Call_Detected.",
        "safety_mechanism": "Confidence threshold check: Requires detector confidence > 80% to avoid nuisance warnings.",
        "failure_reaction": "Suppress alert if handsfree Bluetooth call is currently active.",
        "inputs": "IR_Cabin_Camera_Greyscale_Image, Driver_Head_Keypoints[5], Bluetooth_Call_Active_Flag",
        "outputs": "Handheld_Call_Detected_Flag, Texting_At_Wheel_Detected_Flag",
        "verification": "Detection benchmark across 50 mobile phone models and hand grip variations."
    },
    {
        "id": "SWR-CPT-01-08",
        "title": "Driver Distraction Visual Prompt & Audio Chime Suppressor",
        "parent": "SYS-CPT-01-04",
        "asil": "ASIL A",
        "swc": "DmsDistractionHmi_SWC",
        "period": "50 ms",
        "wcet": "0.3 ms",
        "activation": "Active upon distraction detection.",
        "algorithm": "Displays amber 'Pay Attention to Road' icon on Instrument Cluster and Head-Up Display. Sounds gentle 600 Hz reminder chime if distraction persists > 3.5 seconds. Automatically extinguishes warning within 500 ms when driver returns gaze to forward road.",
        "safety_mechanism": "Nuisance prevention filter: Distraction warnings muted below 10 km/h (traffic light stop).",
        "failure_reaction": "Display static warning icon if chime amplifier is muted.",
        "inputs": "Handheld_Call_Detected_Flag, Gaze_On_Road_Confirmed_Flag, Vehicle_Speed_Kmph",
        "outputs": "Cluster_Distraction_Icon_Cmd, HUD_Distraction_Prompt_Cmd, Chime_Request_Code",
        "verification": "HMI user study evaluating distraction alert efficacy and annoyance rating."
    },
    {
        "id": "SWR-CPT-01-09",
        "title": "Head Slump & Cardiac Incapacitation Multi-Sensor Classifier",
        "parent": "SYS-CPT-01-05",
        "asil": "ASIL D",
        "swc": "DmsIncapacitationDetector_SWC",
        "period": "20 ms",
        "wcet": "0.8 ms",
        "activation": "Continuous safety task.",
        "algorithm": "Detects acute medical incapacitation: 1) Head pitch angle < -40 deg (chin on chest) for > 3.0s; 2) Eyelid PERCLOS == 100% (eyes closed); 3) Hands-Off steering wheel == TRUE. Fuses with driver seat ECG/ballistocardiogram heart rate sensor: Flags Acute_Incapacitation if heart rate drops to zero or ventricular fibrillation detected.",
        "safety_mechanism": "Triple-sensor quorum check to avoid false tripping during driver head stretch.",
        "failure_reaction": "Initiate emergency stop sequence immediately upon positive quorum confirmation.",
        "inputs": "Head_Pose_Euler_Angles[3], PERCLOS_Score_Pct, Hands_On_Steering_Flag, Seat_Heart_Rate_BPM",
        "outputs": "Driver_Incapacitation_Confirmed_Flag (boolean), Incapacitation_Severity_Enum",
        "verification": "Medical simulator testing of driver cardiac arrest and stroke scenarios."
    },
    {
        "id": "SWR-CPT-01-10",
        "title": "Autonomous Safe Pull-Over & Emergency Medical Dispatcher",
        "parent": "SYS-CPT-01-05",
        "asil": "ASIL D",
        "swc": "DmsEmergencyPullOver_SWC",
        "period": "20 ms",
        "wcet": "0.6 ms",
        "activation": "Triggered on Driver_Incapacitation_Confirmed_Flag.",
        "algorithm": "Coordinates emergency stop: Decelerates vehicle at -2.0 m/s², steers to maintain center of lane (or pulls over to road shoulder if safe), flashes exterior hazard lamps, brings vehicle to complete stop, applies EPB, unlocks doors, and transmits automatic eCall with 'Driver Medical Emergency' priority code.",
        "safety_mechanism": "Driver manual abort: Driver grasping steering wheel with > 3 Nm torque cancels maneuver instantly.",
        "failure_reaction": "Continue automated stop in lane if road shoulder is blocked.",
        "inputs": "Driver_Incapacitation_Confirmed_Flag, Driver_Handwheel_Torque_Nm, Current_Speed_Mps",
        "outputs": "Emergency_Decel_Cmd_Mps2, Lane_Centering_Assist_Force_Active, Emergency_Medical_eCall_Req",
        "verification": "Closed proving ground track validation of autonomous medical emergency stop."
    }
])

# FEAT-CPT-02: AR-HUD (Expanded to 4 sys reqs, 8 sw reqs)
f2 = old_feats["FEAT-CPT-02"]
f2["sys_reqs"].extend([
    {
        "id": "SYS-CPT-02-03",
        "title": "Real-Time World-Grounding Parallax & Eye-Box Pupil Tracking",
        "asil": "ASIL B",
        "statement": "The System SHALL sample driver pupil 3D coordinates via DMS camera at 60 Hz, adjusting AR projection ray matrix in <= 16 ms to eliminate motion parallax and keep virtual navigation arrows anchored to physical road lanes within +-0.5 degrees optical accuracy.",
        "activation": "Active whenever AR-HUD display is enabled.",
        "ftti": "30 ms",
        "safe_state": "Switch AR graphics to static non-conformal 2D HUD projection.",
        "failure_reaction": "If driver eyes are obscured by sunglasses, default to average 50th percentile eye-box center.",
        "inputs": "Driver_Pupil_3D_Coordinates_Mm, Chassis_Suspension_Pitch_Roll_Deg, Ego_Vehicle_Speed_Mps",
        "outputs": "EyeBox_Parallax_Correction_Matrix[4x4], Optical_Ray_Angle_Offsets",
        "verification": "Optical bench camera tracking test with motorized eye-box motion simulator."
        ,"downstream": ["SWR-CPT-02-05", "SWR-CPT-02-06"]
    },
    {
        "id": "SYS-CPT-02-04",
        "title": "Optical DLP Laser Picture Generation Unit (PGU) Thermal Protector",
        "asil": "ASIL A",
        "statement": "The System SHALL monitor Digital Light Processing (DLP) RGB laser diode temperatures, dynamically scaling laser power (0 to 100% luminance up to 15,000 nits) to preserve daytime visibility under direct sunlight while preventing laser thermal burnout (> 75°C).",
        "activation": "Continuous optical engine operation.",
        "ftti": "200 ms",
        "safe_state": "Dim laser power to 20% baseline luminance.",
        "failure_reaction": "Shut off laser diode driver if PGU internal temperature exceeds 85°C.",
        "inputs": "Laser_Diode_Temperature_Array[3], Forward_Ambient_Illuminance_Lux, Windshield_Solar_Flux_W_M2",
        "outputs": "Laser_Drive_Current_RGB_mA, PGU_Cooling_Fan_Duty_PWM",
        "verification": "Direct solar simulator thermal soak test (1000 W/m²) on windshield HUD combiner."
        ,"downstream": ["SWR-CPT-02-07", "SWR-CPT-02-08"]
    }
])
f2["sw_reqs"].extend([
    {
        "id": "SWR-CPT-02-05",
        "title": "High-Speed Eye-Box 60 Hz Coordinate Transformation Engine",
        "parent": "SYS-CPT-02-03",
        "asil": "ASIL B",
        "swc": "ArHudEyeBoxTransformer_SWC",
        "period": "16 ms",
        "wcet": "1.8 ms",
        "activation": "Executed on 60 Hz display refresh vertical sync.",
        "algorithm": "Ingests pupil coordinates (x_eye, y_eye, z_eye) from DMS: Recomputes 4x4 perspective view-projection matrix: P_eye = P_nominal * T_pupil_offset. Compensates for chassis suspension pitch vibrations: theta_pitch_comp = theta_imu * K_viscous. Ensures virtual carpet lines remain locked to physical road asphalt.",
        "safety_mechanism": "Jitter filter: Low-pass filters eye position at 12 Hz cutoff to eliminate pupil microsaccade shake.",
        "failure_reaction": "Freeze eye-box matrix if DMS frame is dropped.",
        "inputs": "Pupil_Position_X_Y_Z_Mm, Chassis_Pitch_Angle_Rad, Chassis_Roll_Angle_Rad",
        "outputs": "View_Projection_Matrix_Float[16], Virtual_Anchor_Displacement_Px",
        "verification": "Dynamic road shaker rig optical image stability testing."
    },
    {
        "id": "SWR-CPT-02-06",
        "title": "Virtual Navigation Carpet Mesh Spline Ground Warper",
        "parent": "SYS-CPT-02-03",
        "asil": "ASIL B",
        "swc": "ArHudMeshWarper_SWC",
        "period": "16 ms",
        "wcet": "2.2 ms",
        "activation": "Executed in GPU shader graphics pipeline.",
        "algorithm": "Renders 3D textured navigation turn carpet: Warps 3D mesh vertices to align with forward roadway elevation profile z(x). Renders directional chevron pulses sweeping forward in turn direction. Clips virtual mesh behind lead vehicles to avoid floating graphics over other cars.",
        "safety_mechanism": "Occlusion culling: Depth-buffers virtual chevrons against radar lead vehicle distance.",
        "failure_reaction": "Render simple 2D overhead arrow upon shader pipeline error.",
        "inputs": "Navigation_Turn_Waypoint_Spline, Lead_Vehicle_Distance_M, Road_Elevation_Profile",
        "outputs": "GPU_Draw_Command_Buffer, Depth_Occlusion_Culling_Mask",
        "verification": "Night and day driving validation assessing driver visual cognitive load."
    },
    {
        "id": "SWR-CPT-02-07",
        "title": "RGB Laser Diode 15,000-Nit Ambient Light Closed-Loop Governor",
        "parent": "SYS-CPT-02-04",
        "asil": "ASIL A",
        "swc": "ArHudLuminanceGovernor_SWC",
        "period": "50 ms",
        "wcet": "0.4 ms",
        "activation": "Cyclic 50 ms task.",
        "algorithm": "Computes required optical luminance: L_target = K_lux * Ambient_Lux^0.6. Maps target luminance to RGB laser diode current: Red I_r, Green I_g, Blue I_b maintaining constant D65 white balance (6500K color temperature). Clamps maximum luminance to 15,000 nits on bright snow.",
        "safety_mechanism": "Eye safety compliance: Enforces IEC 60825-1 Class 1 laser safety limits under all optical conditions.",
        "failure_reaction": "Dim laser to 500 nits if ambient light sensor reports saturated open circuit.",
        "inputs": "Forward_Ambient_Lux_Sensor, Windshield_Reflectance_Factor, Target_Color_Temp_K",
        "outputs": "Laser_Current_DAC_Red_mA, Laser_Current_DAC_Green_mA, Laser_Current_DAC_Blue_mA",
        "verification": "Photometer luminance and chromaticity measurement across 10 to 100,000 lux."
    },
    {
        "id": "SWR-CPT-02-08",
        "title": "DLP Mirror Array & Laser Thermal Derating Cut-Off Manager",
        "parent": "SYS-CPT-02-04",
        "asil": "ASIL A",
        "swc": "ArHudThermalManager_SWC",
        "period": "100 ms",
        "wcet": "0.3 ms",
        "activation": "Continuous thermal task.",
        "algorithm": "Monitors DLP optical engine thermistors: If Laser_Temp > 70°C, scales maximum luminance down by 3% per °C. If Laser_Temp > 82°C, completely shuts off laser diode current to prevent semiconductor crystal degradation.",
        "safety_mechanism": "PWM brushless fan speed governor: Ramps cooling blower fan to 100% when temperature exceeds 65°C.",
        "failure_reaction": "Set DEM DTC B1803 (HUD Picture Generation Unit Overtemperature).",
        "inputs": "DLP_Laser_Thermistor_DegC, Ambient_Cabin_Temp_DegC",
        "outputs": "Laser_Thermal_Derate_Scalar, HUD_Cooling_Fan_PWM_Duty",
        "verification": "High-temperature wind tunnel environmental soak test at +50°C ambient."
    }
])

all_cpt = [f1, f2, old_feats["FEAT-CPT-03"], old_feats["FEAT-CPT-04"]]

print(f"Total Cockpit features compiled: {len(all_cpt)}")
total_sys = sum(len(f['sys_reqs']) for f in all_cpt)
total_sw = sum(len(f['sw_reqs']) for f in all_cpt)
print(f"Total Cockpit SysReqs: {total_sys}, Total Cockpit SwReqs: {total_sw}")

code = "# Complete Cockpit Electronics & Acoustic Safety Features (4 Features)\n\n"
code += "full_cpt_features = " + repr(all_cpt) + "\n"
code += 'print(f"Loaded all {len(full_cpt_features)} Cockpit features successfully.")\n'

with open("features_cpt_full.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated features_cpt_full.py successfully!")

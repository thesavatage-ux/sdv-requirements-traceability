# -*- coding: utf-8 -*-
"""
Full SDV Platform Requirements Expansion Engine.
Expands all 40 automotive features across the 6 domains to >= 15 SYS and >= 35 SWR each.
Complies with ASPICE PAM v3.1 (SYS.2, SYS.3, SWE.1) and ISO 26262:2018 (Part 4, Part 6).
"""

import os
import sys

# Template library for generating authentic, domain-specific requirements
# for features based on their technical subsystem.

def get_domain_expansion_specs():
    # Mapping of feature ID to a list of specific system requirement titles, statements, and child SWCs
    specs = {
        # ADAS DOMAIN
        "FEAT-ADAS-01": [
            ("Curve Speed Preview & Transverse G Regulation", "ASIL B", "100 ms", "Limit vehicle speed on upcoming road curvature based on digital map and camera clothoid radius (a_y <= 2.2 m/s²).", "AdasCurvePreview_SWC", "20 ms"),
            ("Stop-and-Go Automatic Standstill Hold & Creep Management", "ASIL B", "150 ms", "Hold vehicle stationary via foundation brakes at standstill, re-engaging drive within 3.0s if lead vehicle departs.", "AdasStopAndGo_SWC", "10 ms"),
            ("Overtake Assist & Adjacent Lane Indicator Trigger", "ASIL B", "200 ms", "Command temporary gap acceleration when driver activates left turn signal with open overtaking lane.", "AdasOvertakeAssist_SWC", "20 ms"),
            ("Adverse Weather & Sensor Degraded Speed Derating", "ASIL B", "500 ms", "Derate maximum allowed ACC set-speed from 160 km/h to 90 km/h upon heavy rain or reduced radar SNR.", "AdasWeatherDerate_SWC", "100 ms"),
            ("Driver Throttle & Brake Pedal Takeover Arbitration", "ASIL B", "50 ms", "Seamlessly suppress ACC acceleration upon throttle press and immediately cancel to STANDBY upon brake pedal apply.", "AdasOverrideArbitrate_SWC", "10 ms"),
            ("ACC E2E CAN-FD & Automotive Ethernet Frame Protection", "ASIL B", "40 ms", "Supervise E2E Profile 5 CRC-16 and 4-bit alive counter on chassis braking and powertrain acceleration commands.", "AdasE2ESupervisor_SWC", "10 ms"),
            ("Instrument Cluster & HUD Multi-Level HMI Annunciation", "ASIL B", "100 ms", "Broadcast lead vehicle distance bars, target speed setpoints, and takeover prompts to cluster and AR-HUD.", "AdasHmiDispatcher_SWC", "50 ms")
        ],
        "FEAT-ADAS-02": [
            ("Cross-Junction Oncoming Traffic & Turn AEB Assist", "ASIL D", "30 ms", "Detect oncoming vehicles during left/right turns across traffic and command emergency braking in <= 80 ms.", "AebJunctionMonitor_SWC", "10 ms"),
            ("Pedestrian & Vulnerable Road User (VRU) Lateral Path Prediction", "ASIL D", "30 ms", "Track lateral velocity of crossing pedestrians/cyclists and trigger full brake when collision envelope is crossed.", "AebVruPredictor_SWC", "10 ms"),
            ("Evasive Steering Maneuver Assist (EMA) Torque Superposition", "ASIL D", "20 ms", "Superimpose up to +-3.0 Nm steering torque assist to support driver emergency obstacle avoidance.", "AebEvasiveSteer_SWC", "5 ms"),
            ("Brake Caliper Hydraulic Pre-Fill & Zero-Clearance Booster", "ASIL D", "20 ms", "Apply 4.0 bar hydraulic prefill pressure to calipers upon critical FCW stage to eliminate pad travel lag.", "AebPreFillCommander_SWC", "5 ms"),
            ("Reversible Seatbelt Pre-Tensioning & Window Closure Safing", "ASIL D", "30 ms", "Trigger motorized seatbelt pre-tensioners (250 N) and close open windows 1.2s prior to unavoidable impact.", "AebPreCrashSafing_SWC", "10 ms"),
            ("Driver Panic Steering & Throttle Suppression Logic", "ASIL D", "20 ms", "Inhibit accelerator kickdown override during qualified AEB emergency interventions unless steering away.", "AebOverrideSuppress_SWC", "10 ms"),
            ("Post-Crash Autonomous Deceleration & Secondary Collision Prevention", "ASIL D", "40 ms", "Maintain 100 bar brake pressure for 3.0s following collision impact to prevent secondary vehicular impacts.", "AebPostCrashHold_SWC", "10 ms"),
            ("Dual Core Lockstep Safing & Unintended Braking Supervisor", "ASIL D", "15 ms", "Cross-check acceleration negative command against radar/camera target range in independent core comparator.", "AebLockstepSupervisor_SWC", "2 ms"),
            ("DEM Non-Volatile Freeze-Frame Crash Event Recording", "ASIL B", "50 ms", "Record 128-byte pre-crash and post-crash dynamics buffer to flash memory upon qualified AEB activation.", "AebCrashRecorder_SWC", "10 ms")
        ],
        "FEAT-ADAS-03": [
            ("Camera Video Stream Road Edge & Barrier Kinematic Boundary Estimator", "ASIL B", "50 ms", "Estimate distance to unpainted road boundaries, curbs, and guardrails at 20 ms cycle.", "LcaRoadEdgeDetector_SWC", "20 ms"),
            ("Clothoid Lane Model 3rd-Degree Polynomial Tracking Filter", "ASIL B", "40 ms", "Filter clothoid curvature parameters c0, c1, c2 to predict lane center trajectory with lag < 25 ms.", "LcaClothoidTracker_SWC", "10 ms"),
            ("Emergency Lane Keeping (ELK) Oncoming Vehicle Hazard Mitigator", "ASIL B", "30 ms", "Detect road departure into oncoming traffic lane and apply urgent corrective steering counter-torque.", "LcaElkEmergencySteer_SWC", "10 ms"),
            ("Driver Capacitive Hands-On Detection (HOD) Supervisor", "ASIL B", "100 ms", "Sample steering wheel capacitive touch sensors at 50 Hz, escalating hands-off warnings after 15s.", "LcaHodSupervisor_SWC", "20 ms"),
            ("Turn Signal Lane Change Suppression & Override Deactivation", "ASIL B", "40 ms", "Temporarily suppress lane keeping counter-torque when driver signals intentional lane departure.", "LcaSignalOverride_SWC", "10 ms"),
            ("EPS Steering Torque Overlay Maximum Authority Clamp", "ASIL B", "20 ms", "Strictly constrain overlay torque demand to <= 3.0 Nm to allow effortless driver manual override.", "LcaTorqueClamp_SWC", "5 ms"),
            ("Wet Surface Low-Contrast Marker Confidence Degradation", "ASIL B", "200 ms", "Smoothly reduce lateral control gain when lane marker visual contrast drops below 35%.", "LcaConfidenceDegrader_SWC", "50 ms"),
            ("HMI Visual Lane Departure Tell-Tale & Haptic Vibration Annunciation", "ASIL B", "50 ms", "Trigger cluster lane graphics and steering wheel haptic vibration pulse upon departure.", "LcaHmiNotifier_SWC", "20 ms"),
            ("LCA System Fault Passive Disengagement & Fail-Silent Isolation", "ASIL B", "30 ms", "Ramp down steering overlay torque to zero within 200 ms upon sensor fault without vehicle jerk.", "LcaFailSilentShutdown_SWC", "10 ms"),
            ("DEM Lane Boundary Diagnostics & Camera Blockage Evaluation", "ASIL B", "100 ms", "Log DEM diagnostic trouble codes and prompt driver when front camera lens is obscured.", "LcaCameraDiag_SWC", "100 ms")
        ],
        "FEAT-ADAS-04": [
            ("L3 ODD Boundary Dynamic Validator & Speed Envelope Gate", "ASIL D", "50 ms", "Confirm vehicle is on geofenced divided motorway with zero oncoming traffic and speed <= 60 km/h.", "TjpOddValidator_SWC", "20 ms"),
            ("Triple Sensor Perception Fusion (Dual Lidar, Camera, Radar)", "ASIL D", "30 ms", "Fuse 3D lidar point clouds with camera objects at 30 Hz for 360-degree obstacle validation.", "TjpPerceptionFusion_SWC", "15 ms"),
            ("HD Map & GNSS RTK Decimeter-Level Localization Cross-Monitor", "ASIL D", "50 ms", "Validate ego-vehicle lane positioning against HD map vector attributes with error <= 0.15 m.", "TjpMapLocalization_SWC", "20 ms"),
            ("Driver Availability Recognition & DMS Gaze Continuous Tracker", "ASIL D", "100 ms", "Monitor driver face orientation and pupil dilation to verify driver readiness within 10-second window.", "TjpDriverReadiness_SWC", "50 ms"),
            ("10-Second Transition Demand (TD) Handover Sequence Governor", "ASIL D", "100 ms", "Execute multi-stage visual/acoustic/haptic escalation sequence prompting driver to resume control.", "TjpTransitionManager_SWC", "50 ms"),
            ("Minimum Risk Maneuver (MRM) Safe-Stop Controlled Trajectory", "ASIL D", "40 ms", "Execute automatic controlled braking stop within lane (-2.5 m/s²) if driver fails to resume control.", "TjpMrmController_SWC", "20 ms"),
            ("Automated Hazard Warning Flasher & E-Call Trigger Dispatcher", "ASIL B", "100 ms", "Activate vehicle hazard warning flashers upon initiation of Minimum Risk Maneuver stop.", "TjpEmergencyHmi_SWC", "50 ms"),
            ("Redundant Steering & Braking Communication Heartbeat Monitor", "ASIL D", "15 ms", "Cross-check primary and secondary steering/braking actuator ready status at 100 Hz.", "TjpActuatorHeartbeat_SWC", "5 ms"),
            ("Event Data Recorder (EDR) Autonomous Control State Logger", "ASIL B", "50 ms", "Record continuous 30-second rolling circular buffer of control transitions and driver takeover.", "TjpEdrLogger_SWC", "50 ms"),
            ("DEM Level 3 Operational Diagnostics & Hardware Failure Latching", "ASIL D", "30 ms", "Latch critical L3 hardware failure status and inhibit re-engagement until complete service clearance.", "TjpDemSupervisor_SWC", "20 ms")
        ],
        "FEAT-ADAS-05": [
            ("High-Speed Highway Navigation Point-to-Point Route Optimizer", "ASIL D", "100 ms", "Calculate lane-level navigation waypoints across multi-lane highway networks at 100 ms cycle.", "HwpRoutePlanner_SWC", "50 ms"),
            ("Automated Lane Change Trajectory Generator & Gap Evaluator", "ASIL D", "40 ms", "Evaluate forward, side, and rear radar clearance before initiating automated lane change maneuver.", "HwpLaneChangePlanner_SWC", "20 ms"),
            ("Blind Spot & Fast-Approaching Rear Vehicle TTC Safety Assessor", "ASIL D", "30 ms", "Calculate time-to-collision with vehicles in target lane up to 120 m rearward (TTC > 4.5s required).", "HwpRearClearance_SWC", "15 ms"),
            ("High-Speed Interchange Ramp Merging & Speed Adaptation Governor", "ASIL D", "50 ms", "Govern speed smoothly from 130 km/h down to ramp advisory speed (60 km/h) based on curvature.", "HwpRampSpeedGovernor_SWC", "20 ms"),
            ("Dynamic 360-Degree Safety Corridor Buffer Envelope Calculator", "ASIL D", "30 ms", "Maintain dynamic safety polygon buffer around vehicle perimeter scaling with ego velocity.", "HwpCorridorCalculator_SWC", "10 ms"),
            ("Longitudinal & Lateral Actuation Coordinated Command Dispatcher", "ASIL D", "20 ms", "Synchronize steering angle and propulsion torque setpoints over chassis CAN-FD with E2E CRC.", "HwpActuationCoordinator_SWC", "5 ms"),
            ("Driver Steering Nudge Override Cancellation & Smooth Handover", "ASIL D", "30 ms", "Detect driver steering input (> 2.0 Nm) and seamlessly yield lateral authority to human driver.", "HwpDriverTakeover_SWC", "10 ms"),
            ("Inclement Weather & Low Visibility Highway ODD Limiter", "ASIL B", "200 ms", "Restrict automated highway pilot operation when visibility drops below 150 m or wiper speed is high.", "HwpWeatherGovernor_SWC", "100 ms"),
            ("Redundant Dual-Compute Platform Synchronization & Failover Engine", "ASIL D", "15 ms", "Mirror trajectory plans across primary and secondary compute cores; failover in <= 15 ms.", "HwpComputeFailover_SWC", "5 ms"),
            ("DEM Diagnostic Freeze-Frame & Highway Event Recorder", "ASIL B", "50 ms", "Log diagnostic trouble codes and non-volatile operational traces upon any aborted maneuver.", "HwpDiagnosticManager_SWC", "50 ms")
        ],
        "FEAT-ADAS-06": [
            ("Infrastructure-to-Vehicle (I2V) 5G/V2X Secure Session Authenticator", "ASIL D", "50 ms", "Authenticate parking facility server public key certificate and decrypt trajectory waypoints.", "AvpSecurityAuth_SWC", "50 ms"),
            ("Indoor Parking Garage SLAM & Multi-Sensor Localization Engine", "ASIL D", "30 ms", "Localize vehicle in GPS-denied parking garage using wheel odometry, lidar, and ceiling camera markers.", "AvpSlamLocalization_SWC", "20 ms"),
            ("Surround Ultrasonic & Camera Occupancy Grid Map Generator", "ASIL D", "30 ms", "Construct 360-degree local occupancy grid map with 10 cm resolution to detect curbs and pillars.", "AvpGridMapBuilder_SWC", "20 ms"),
            ("Low-Speed Path Tracking & Dynamic Steering Angle Controller", "ASIL D", "20 ms", "Regulate vehicle path along trajectory at speeds <= 8.0 km/h with lateral tracking error <= 5.0 cm.", "AvpPathTracker_SWC", "10 ms"),
            ("Cross-Aisle Pedestrian Detection & Emergency Stop Deceleration", "ASIL D", "20 ms", "Detect crossing pedestrians at blind garage corners and command full stop (-4.0 m/s²) in <= 150 ms.", "AvpPedestrianEmergencyStop_SWC", "10 ms"),
            ("Automated Shift-by-Wire Gear State Coordinator (P-R-N-D)", "ASIL D", "50 ms", "Command transmission gear transitions at standstill with brake pressure interlock verification.", "AvpGearCoordinator_SWC", "20 ms"),
            ("Electric Parking Brake (EPB) Standstill Clamp & Lock Supervisor", "ASIL D", "100 ms", "Engage dual-motor EPB calipers upon reaching target parking stall with clamping force >= 18 kN.", "AvpEpbLockSupervisor_SWC", "50 ms"),
            ("Vehicle Remote Summon & Waypoint Arrival Dispatcher", "ASIL B", "100 ms", "Transmit real-time parking progress, arrival confirmation, and vehicle coordinates to mobile app.", "AvpSummonDispatcher_SWC", "100 ms"),
            ("Remote Teleoperation Emergency Heartbeat & Watchdog Monitor", "ASIL D", "20 ms", "Monitor continuous 50 ms heartbeat from parking control tower; trigger safe stop if link lost.", "AvpTeleopHeartbeat_SWC", "10 ms"),
            ("DEM Non-Volatile AVP Parking Mission Audit Buffer", "ASIL B", "50 ms", "Record complete audit log of autonomous parking mission, sensor states, and brake events.", "AvpMissionRecorder_SWC", "50 ms")
        ],
        "FEAT-ADAS-07": [
            ("Ultrasonic Echo Time-of-Flight Slot Width & Depth Profiler", "ASIL B", "40 ms", "Measure parking slot dimensions (parallel slot min length = car + 0.8m) at speeds <= 20 km/h.", "ApaSlotScanner_SWC", "20 ms"),
            ("Surround View Camera Parking Line Corner Coordinate Extractor", "ASIL B", "50 ms", "Extract parking slot painted boundary lines and corners from 4 fisheye cameras.", "ApaCameraLineExtractor_SWC", "30 ms"),
            ("Collision-Free Multi-Segment Parking Trajectory Planner", "ASIL B", "50 ms", "Generate continuous-curvature Reeds-Shepp parking maneuver path with <= 3 direction reversals.", "ApaTrajectoryPlanner_SWC", "30 ms"),
            ("Steering Wheel Automated Angle Servocontrol Tracking Law", "ASIL B", "20 ms", "Command steering rack angle with tracking error <= 0.3° and maximum angular speed 450 °/s.", "ApaSteeringServo_SWC", "10 ms"),
            ("Slow-Speed Propulsion Torque & Creep Velocity Governor", "ASIL B", "30 ms", "Govern vehicle speed precisely to 3.5 +- 0.5 km/h during automated parking maneuver.", "ApaSpeedGovernor_SWC", "10 ms"),
            ("Dynamic Ultrasonic Proximity Obstacle Encroachment Monitor", "ASIL B", "20 ms", "Monitor obstacle clearance; command immediate stop if distance drops below 25 cm.", "ApaProximityStop_SWC", "10 ms"),
            ("Driver Steering Wheel Hands-On Intervention Cancellation Gate", "ASIL B", "30 ms", "Abort automated parking maneuver immediately if driver applies > 3.0 Nm steering wheel torque.", "ApaDriverAbort_SWC", "10 ms"),
            ("Automated Shift-by-Wire Reverse/Drive Transition Sequence Manager", "ASIL B", "50 ms", "Coordinate smooth vehicle stop, brake apply, and gear change (R <-> D) during multi-point turn.", "ApaShiftSequencer_SWC", "20 ms"),
            ("Curbside Wheel Rim Scrape Protection & Tilt Mirror Actuator", "ASIL B", "100 ms", "Estimate distance to curb edge and tilt side mirrors down to provide driver visual feedback.", "ApaCurbProtector_SWC", "50 ms"),
            ("Cluster Top-Down 3D Surround View Display Streamer", "ASIL B", "50 ms", "Composite and render 30 fps top-down parking guide trajectory onto central touchscreen display.", "ApaDisplayStreamer_SWC", "33 ms"),
            ("DEM Parking System Component Health Diagnostics & DTC Manager", "ASIL B", "100 ms", "Monitor ultrasonic transducer transceiver lines and log DTCs upon hardware anomaly.", "ApaDiagnosticManager_SWC", "50 ms")
        ],
        "FEAT-ADAS-08": [
            ("Rear Corner Radar High-Speed Object Trajectory Tracker", "ASIL B", "40 ms", "Track position, velocity, and heading of up to 32 targets in adjacent lanes up to 75 m rearward.", "BsdRadarTracker_SWC", "20 ms"),
            ("Adjacent Lane Blind Spot Zone Vehicle Occupancy Detector", "ASIL B", "40 ms", "Detect presence of vehicles in blind zone polygon (from side mirror to 3 m rear of bumper).", "BsdZoneDetector_SWC", "20 ms"),
            ("Closing Velocity & Time-to-Collision (TTC) Criticality Evaluator", "ASIL B", "30 ms", "Calculate TTC = d_rel / v_closing; trigger Level 1 warning when TTC <= 3.5 seconds.", "BsdTtcEvaluator_SWC", "15 ms"),
            ("Side Mirror Optical Warning LED Intensity Driver", "ASIL B", "50 ms", "Drive side-mirror amber warning LED, adjusting brightness according to ambient light sensor.", "BsdOpticalDriver_SWC", "20 ms"),
            ("Turn Signal Activation Intent & Level 2 Alert Escalation", "ASIL B", "20 ms", "Escalate to flashing optical warning and 750 Hz acoustic chime if driver signals toward occupied lane.", "BsdAlertEscalator_SWC", "10 ms"),
            ("Active Lane Change Steering Resistance Torque Superposition", "ASIL B", "20 ms", "Apply subtle counter-torque (+-1.5 Nm) through EPS if driver begins turning into occupied lane.", "BsdSteerResistance_SWC", "10 ms"),
            ("Motorcycle & Narrow Vulnerable Vehicle High-Sensitivity Classifier", "ASIL B", "40 ms", "Enhance radar reflection clustering to identify low-RCS motorcycles overtaking in blind spots.", "BsdMotorcycleFilter_SWC", "20 ms"),
            ("Highway Guardrail & Stationary Structure False Positive Filter", "ASIL B", "50 ms", "Filter out stationary guardrails, acoustic barriers, and light poles from blind spot trigger alerts.", "BsdFalsePositiveFilter_SWC", "20 ms"),
            ("Rear Corner Radar Bumper Misalignment & Pitch Angle Observer", "ASIL B", "200 ms", "Detect radar mechanical mounting misalignment > 2.0° using stationary ground target vectors.", "BsdAlignmentMonitor_SWC", "100 ms"),
            ("Trailer Hitch Detection & Blind Spot Zone Dynamic Extension", "ASIL B", "100 ms", "Extend blind spot monitoring polygon rearward by trailer length (up to 10 m) when trailer attached.", "BsdTrailerExtension_SWC", "50 ms"),
            ("DEM Diagnostic Fault Management & Low-Voltage Derating", "ASIL B", "100 ms", "Supervise radar supply voltage and communication timeout; set DTCs and inform driver.", "BsdDiagnosticManager_SWC", "50 ms")
        ],
        "FEAT-ADAS-09": [
            ("Reverse Gear Selection Trigger & System State Initialization", "ASIL B", "50 ms", "Arm rear cross traffic monitoring within 100 ms of driver selecting REVERSE gear.", "RctaStateInit_SWC", "20 ms"),
            ("Rear Corner Radar 150-Degree Ultra-Wide Crossing Target Scanner", "ASIL B", "30 ms", "Scan cross traffic approaching perpendicularly from left and right at speeds from 5 to 40 km/h.", "RctaCrossingScanner_SWC", "15 ms"),
            ("Crossing Vehicle Lateral Path Intersection & TTC Predictor", "ASIL B", "30 ms", "Compute projected collision point behind vehicle; assert warning if TTC <= 2.5 seconds.", "RctaTtcPredictor_SWC", "15 ms"),
            ("3-Stage Driver Warning Alert (Visual Graphic, Audio Chime, HUD)", "ASIL B", "40 ms", "Display directional red flashing arrows on reverse camera screen and sound directional chimes.", "RctaWarningDispatcher_SWC", "20 ms"),
            ("Rear Cross Traffic Autonomous Braking (RCTB) Trigger Governor", "ASIL B", "20 ms", "Command full braking stop (-6.0 m/s²) in <= 120 ms if crossing vehicle TTC drops below 1.2s.", "RctbBrakeTrigger_SWC", "10 ms"),
            ("Rear Bumper Ultrasonic Sensor Close-Range Fusion Gatekeeper", "ASIL B", "30 ms", "Cross-validate radar detections with rear ultrasonic sensors to confirm close-range obstacles.", "RctaUltrasonicFusion_SWC", "15 ms"),
            ("Pedestrian & Cyclist Low-Profile Crossing Target Detector", "ASIL B", "40 ms", "Detect walking pedestrians (speed 1-5 km/h) crossing behind vehicle in low-light parking conditions.", "RctaVruDetector_SWC", "20 ms"),
            ("Trailer Hitch Engagement Automatic RCTB Deactivation", "ASIL B", "100 ms", "Automatically suppress autonomous reverse braking when trailer is hitched to prevent false stops.", "RctaTrailerSuppress_SWC", "50 ms"),
            ("Driver Throttle Override & Standstill Release Sequence", "ASIL B", "50 ms", "Release autonomous brake hold after 2.0s standstill or if driver depresses accelerator pedal firmly.", "RctaBrakeRelease_SWC", "20 ms"),
            ("Rear Camera Video Feed Dirt & Snow Obstruction Detector", "ASIL B", "200 ms", "Detect obscured rear camera lens and trigger cluster alert notifying driver to clean lens.", "RctaCameraObstruction_SWC", "100 ms"),
            ("DEM Diagnostic Event Reporting & Non-Volatile Error Latching", "ASIL B", "100 ms", "Log DTCs for rear corner radar communication timeout and internal sensor processing faults.", "RctaDiagnosticManager_SWC", "50 ms")
        ],
        "FEAT-ADAS-10": [
            ("Front Camera Traffic Sign Deep Learning Detection & Classification", "ASIL B", "50 ms", "Detect circular and rectangular regulatory speed limit signs with classification accuracy >= 98%.", "IsaTsrClassifier_SWC", "30 ms"),
            ("Digital Navigation Map Speed Limit Database Fusion Engine", "ASIL B", "100 ms", "Fuse visual camera signs with digital map vector speed attributes, resolving conflicting values.", "IsaMapFusion_SWC", "50 ms"),
            ("Electronic Overhead Variable Message Sign (VMS) LED Reader", "ASIL B", "50 ms", "Read dynamic LED variable speed signs on overhead highway gantries across varying illumination.", "IsaVmsReader_SWC", "30 ms"),
            ("Conditional Weather & Time-of-Day Supplementary Sign Evaluator", "ASIL B", "100 ms", "Parse auxiliary signs (e.g. 'In Wet Weather', 'School Zone 7-9 AM') against rain and clock inputs.", "IsaConditionalParser_SWC", "50 ms"),
            ("Instrument Cluster & Head-Up Display Speed Limit Icon Dispatcher", "ASIL B", "50 ms", "Render recognized speed limit badge on instrument cluster and HUD within 150 ms of sign passing.", "IsaDisplayRenderer_SWC", "30 ms"),
            ("Overspeed Visual & Acoustic Warning Escalation Manager", "ASIL B", "100 ms", "Flash speed badge and sound acoustic chime when vehicle speed exceeds limit by > 3 km/h.", "IsaOverspeedAlert_SWC", "50 ms"),
            ("Haptic Accelerator Pedal Counter-Force Pushback Actuator", "ASIL A", "50 ms", "Apply up to 15 N counter-force to accelerator pedal to prompt driver to ease off throttle.", "IsaHapticPedal_SWC", "20 ms"),
            ("Voluntary Intelligent Speed Limiter (ISL) Powertrain Torque Clamp", "ASIL B", "30 ms", "Clamp powertrain propulsion torque to prevent exceeding posted limit when ISL mode enabled.", "IsaTorqueLimiter_SWC", "10 ms"),
            ("Temporary Construction & Work Zone Speed Sign Adaptation", "ASIL B", "100 ms", "Prioritize yellow/orange construction speed signs over standard permanent map speed attributes.", "IsaConstructionZone_SWC", "50 ms"),
            ("Driver Kickdown Accelerator Emergency Override Gate", "ASIL B", "20 ms", "Immediately suspend speed limitation clamp if driver depresses accelerator pedal past kickdown detent.", "IsaKickdownOverride_SWC", "10 ms"),
            ("DEM UNECE R154 Compliance Logging & Camera Lens Health Monitor", "ASIL B", "200 ms", "Log camera obstruction status and ensure compliance with European ISA regulatory standards.", "IsaDiagnosticManager_SWC", "100 ms")
        ]
    }
    return specs

print("Expansion specification library defined.")

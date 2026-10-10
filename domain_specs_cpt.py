# -*- coding: utf-8 -*-
"""
Cockpit Domain expansion specifications library for FEAT-CPT-01 to FEAT-CPT-04.
"""

def get_cpt_expansion_specs():
    specs = {
        "FEAT-CPT-01": [
            ("Near-Infrared (NIR) 940nm LED Illumination Driver & Eye Exposure Safety", "ASIL B", "30 ms", "Modulate 940 nm NIR illumination strobes synchronized with camera shutter, conforming to IEC 62471 eye safety.", "DmsIlluminationDriver_SWC", "10 ms"),
            ("Driver Facial Landmark 68-Point Mesh Real-Time 3D Geometric Tracker", "ASIL B", "33 ms", "Track facial landmarks at 30 fps to reconstruct head pose orientation (pitch, yaw, roll +-1.5°).", "DmsFaceMeshTracker_SWC", "20 ms"),
            ("Eye Gaze Vector Estimation & Instrument Cluster / Windshield Zone Classifier", "ASIL B", "33 ms", "Determine driver visual fixation zone (Road Ahead, Cluster, Center Display, Phone, Mirrors) at 30 Hz.", "DmsGazeZoneClassifier_SWC", "20 ms"),
            ("PERCLOS Percentage Eye Closure Drowsiness Index Evaluator", "ASIL B", "100 ms", "Compute percentage of eye closure over 60-second sliding window: Trigger fatigue alert if PERCLOS > 12.0%.", "DmsPerclosEvaluator_SWC", "50 ms"),
            ("Visual Inattention & Extended Eye-Off-Road Distraction Time Tracker", "ASIL B", "50 ms", "Assert Level 1 audio/visual distraction alert if driver gaze looks away from road forward zone for > 2.0s.", "DmsDistractionTracker_SWC", "20 ms"),
            ("Micro-Sleep & Closed Eyelid Acute Incapacitation Emergency Escalation", "ASIL B", "30 ms", "Detect continuous eye closure > 1.5s while vehicle moving (> 20 km/h); sound urgent high-pitch alarm chime.", "DmsMicroSleepDetector_SWC", "10 ms"),
            ("Cabin Occupant Monitoring System (OMS) Rear Seat Passenger Presence Detector", "ASIL B", "200 ms", "Detect presence of adult, child, or pet in rear seating positions using wide-angle cabin camera.", "OmsOccupantDetector_SWC", "100 ms"),
            ("Child Left Behind In-Cabin Heatstroke Prevention Emergency Warning", "ASIL B", "1000 ms", "Detect forgotten child in locked vehicle: Sound horn, flash lights, and send smartphone app notification in <= 30s.", "OmsChildLeftBehind_SWC", "500 ms"),
            ("Driver Face Identity Biometric Authentication & User Profile Switcher", "ASIL A", "500 ms", "Authenticate registered driver face in <= 1.0s to automatically restore seat, mirror, and climate presets.", "DmsBiometricAuth_SWC", "200 ms"),
            ("Camera Lens Blockage, Sunglass Occlusion & Low Contrast Health Monitor", "ASIL B", "200 ms", "Detect hand covering camera lens or extreme specular reflection, alerting cluster if tracking degraded.", "DmsOcclusionMonitor_SWC", "100 ms")
        ],
        "FEAT-CPT-02": [
            ("Digital Micro-Mirror (DMD) Optical Projection Engine Sub-Pixel Color Renderer", "ASIL B", "16 ms", "Render 1280x720 RGB projection graphics at 60 fps with high contrast ratio (>= 1500:1).", "HudProjectionRenderer_SWC", "8 ms"),
            ("Augmented Reality Windshield Geometric Distortion & Curvature Warping Engine", "ASIL B", "16 ms", "Pre-warp graphic buffers to cancel out curved windshield optical distortion with latency < 10 ms.", "HudOpticalWarping_SWC", "8 ms"),
            ("Virtual Image Distance (VID) 7.5m / 10m Dual-Focal Plane Spatial Depth Aligner", "ASIL B", "20 ms", "Project near plane (speed, alerts at 3m) and far AR plane (navigation arrows, lanes at 10m virtual depth).", "HudDualPlaneAligner_SWC", "10 ms"),
            ("Vehicle 6-DOF Ego-Motion Pose Extrapolator & Eye-Box Jitter Canceler", "ASIL B", "10 ms", "Compensate for vehicle chassis pitch and roll road vibrations to lock AR arrows firmly onto physical road lanes.", "HudJitterCanceler_SWC", "5 ms"),
            ("High-Dynamic Range (HDR) Ambient Light Photodiode Brightness Auto-Adjuster", "ASIL B", "50 ms", "Regulate laser/LED backlight brightness from 20 nits (night) to 15,000 nits (direct noon sunlight).", "HudBrightnessAdjuster_SWC", "20 ms"),
            ("ADAS Target Highlighting Bounding Box Graphic Overlay Serializer", "ASIL B", "20 ms", "Render colored conformal bounding boxes around forward vehicles and pedestrians highlighted by ADAS.", "HudAdasHighlighter_SWC", "10 ms"),
            ("Navigation Turn-by-Turn Dynamic Floating Chevron Arrow Animator", "ASIL A", "33 ms", "Project animated 3D directional guide arrows floating above upcoming highway exit ramps and intersections.", "HudNavArrowAnimator_SWC", "16 ms"),
            ("Eyebox Motorized Mirror Tilt Position Driver Height Memory Storer", "ASIL A", "100 ms", "Position motorized HUD reflection mirror to align optical eyebox with driver eye coordinates from DMS.", "HudEyeboxPositioner_SWC", "50 ms"),
            ("Sunlight Trap & Thermal Mirror Heat Dissipation Overheat Guard", "ASIL B", "500 ms", "Detect thermal load from sunlight concentrated through combiner lens; activate protective cold shutter.", "HudThermalGuard_SWC", "200 ms"),
            ("Optical Engine Pixel Burnout & Frame Freeze Hardware Watchdog Safing", "ASIL B", "20 ms", "Hardware FPGA monitors video stream CRC: Blank HUD display in <= 40 ms if graphic processor freezes.", "HudWatchdogSafing_SWC", "10 ms"),
            ("DEM Head-Up Display Component Health Diagnostics & DTC Logger", "ASIL B", "100 ms", "Manage diagnostic trouble codes for mirror motor stall, backlight LED failure, and video serializer errors.", "HudDiagnosticManager_SWC", "50 ms")
        ],
        "FEAT-CPT-03": [
            ("Dual Microcontroller Core Architecture ASIL B Safety Island Hardware Core", "ASIL B", "10 ms", "Separate safety-critical tell-tales (brakes, airbag, steering) into isolated hardware domain from Linux UI.", "ClusterSafetyIsland_SWC", "2 ms"),
            ("Safety-Critical Optical Tell-Tale Lamp Display Controller & Pixel Echo Checker", "ASIL B", "10 ms", "Render brake, steering, and airbag warning icons, verifying framebuffer CRC via hardware pixel echo capture.", "ClusterPixelEcho_SWC", "2 ms"),
            ("Vehicle Speedometer Digital Needle Value Verification & Plausibility Monitor", "ASIL B", "20 ms", "Cross-check displayed digital speed value against raw wheel speed CAN-FD frame; trip fault if error > 2 km/h.", "ClusterSpeedPlausibility_SWC", "5 ms"),
            ("Gear Selector State (P-R-N-D) Redundant Display Transmission Governor", "ASIL B", "20 ms", "Display active transmission gear position with zero graphic glitch and latency <= 50 ms from shift lever.", "ClusterGearDisplay_SWC", "5 ms"),
            ("High-Speed CAN-FD / Automotive Ethernet Instrument Cluster Gateway Interface", "ASIL B", "10 ms", "Route safety messages from chassis CAN-FD to instrument cluster safety island with zero dropped packets.", "ClusterGatewayInterface_SWC", "2 ms"),
            ("Cluster LCD Backlight Dual-String LED Open/Short Hardware Supervisor", "ASIL B", "50 ms", "Monitor backlight LED strings: If primary string opens, boost secondary string to maintain cluster readability.", "ClusterBacklightSupervisor_SWC", "20 ms"),
            ("Graphic Processing Unit (GPU) Frame Rendering Freeze & Lockup Hardware Watchdog", "ASIL B", "20 ms", "External safety microcontroller trips GPU reset if rendering frame rate drops below 20 fps for > 200 ms.", "ClusterGpuWatchdog_SWC", "5 ms"),
            ("Acoustic Master Chime Loudspeaker Continuity & Amplifier Impedance Tester", "ASIL B", "100 ms", "Perform continuous silent impedance check on warning chime speaker: Flag DTC if voice coil is open.", "ClusterChimeImpedance_SWC", "50 ms"),
            ("Ambient Cabin Illuminance Display Dimming Curve Generator", "ASIL A", "200 ms", "Smoothly adjust cluster display brightness across 0.5 nits to 1000 nits based on dashboard ambient sensor.", "ClusterDimmingCurve_SWC", "100 ms"),
            ("Trip Computer Energy Consumption & Estimated Range Calculation Law", "ASIL A", "500 ms", "Compute average electrical consumption (kWh/100 km) and remaining battery driving range based on terrain.", "ClusterTripComputer_SWC", "200 ms"),
            ("High-Priority Master Warning Message Text Overlay Pop-Up Manager", "ASIL B", "50 ms", "Display full-screen prioritized text prompts (e.g. 'Pull Over Immediately') upon critical ASIL D system trip.", "ClusterPopUpManager_SWC", "20 ms"),
            ("DEM Instrument Cluster Diagnostic Trouble Code Qualification & Error Logger", "ASIL B", "100 ms", "Log diagnostic fault codes for display controller errors, CAN communication timeouts, and chime faults.", "ClusterDiagnosticManager_SWC", "50 ms"),
            ("Non-Volatile Cluster Odometer Cumulative Mileage Anti-Tamper Counter", "ASIL B", "1000 ms", "Store vehicle cumulative mileage in cryptographically signed redundant EEPROM sectors to prevent fraud.", "ClusterOdometerSecurity_SWC", "500 ms")
        ],
        "FEAT-CPT-04": [
            ("Acoustic Vehicle Alerting System (AVAS) UNECE R138 Minimum Sound Pressure Level Synthesizer", "ASIL B", "20 ms", "Synthesize external engine-like sound at speeds 0 to 20 km/h conforming to 56 to 75 dBA sound pressure limits.", "AvasR138Synthesizer_SWC", "10 ms"),
            ("Forward / Reverse Directional Sound Pitch Shift Frequency Modulator", "ASIL B", "20 ms", "Modulate acoustic sound pitch proportionally to vehicle speed (minimum 0.8% frequency shift per km/h).", "AvasPitchModulator_SWC", "10 ms"),
            ("Dual Exterior Weather-Sealed Loudspeaker Impedance & Continuity Diagnostics", "ASIL B", "50 ms", "Measure front and rear exterior loudspeaker coil impedance at 10 Hz; flag DTC B1412 if speaker disconnected.", "AvasSpeakerDiagnostics_SWC", "20 ms"),
            ("AVAS Sound Synthesis Temporary Driver Pause Switch Regulation (Restricted)", "ASIL B", "100 ms", "Inhibit temporary sound muting unless specifically permitted by local jurisdiction; re-arm at next key cycle.", "AvasPauseGovernor_SWC", "50 ms"),
            ("Active Road Noise Cancellation (RNC) 4-Corner Accelerometer Vibration Acquisition", "ASIL B", "1 ms", "Sample chassis suspension structural accelerometers at 4000 Hz to detect tire impact road noise.", "RncAccelAcquisition_SWC", "0.2 ms"),
            ("Cabin Interior Microphone Acoustic Noise Error Sensor Array Sampler", "ASIL B", "1 ms", "Sample 6 interior cabin roof microphones to capture low-frequency road rumble sound waves (40 to 300 Hz).", "RncMicArraySampler_SWC", "0.2 ms"),
            ("Filtered-X Least Mean Squares (FxLMS) Real-Time Adaptive Phase-Inversion DSP Engine", "ASIL B", "1 ms", "Compute 180-degree anti-noise audio waveforms using adaptive FIR filters to cancel cabin boom.", "RncFxlmsEngine_SWC", "0.4 ms"),
            ("Premium Audio System Multi-Channel Subwoofer Anti-Noise Superposition Driver", "ASIL B", "2 ms", "Superimpose anti-noise audio signals onto cabin audio speakers without distorting music playback.", "RncAudioSuperposition_SWC", "0.5 ms"),
            ("Vehicle Speed & Rough Road Surface RNC Control Gain Dynamic Scaler", "ASIL B", "100 ms", "Scale RNC attenuation gain dynamically: Suppress anti-noise generation if door or window is opened.", "RncGainScaler_SWC", "50 ms"),
            ("Audio Amplifier Thermal & High-Current Voltage Protection Supervisor", "ASIL B", "50 ms", "Derate anti-noise speaker drive amplitude if DSP power amplifier heat sink temperature exceeds 90 °C.", "RncAmplifierThermal_SWC", "20 ms"),
            ("DEM Acoustic System Diagnostic Event Manager & Speaker Fault Latcher", "ASIL B", "100 ms", "Log diagnostic trouble codes for exterior AVAS speaker short-circuit and interior microphone failures.", "AvasDiagnosticManager_SWC", "50 ms"),
            ("Cockpit Sound Signature Customization & Pedestrian Welcome Sound Selector", "ASIL A", "200 ms", "Allow user to select branded vehicle exterior acoustic sound signatures through infotainment settings.", "AvasSoundSignature_SWC", "100 ms"),
            ("Non-Volatile AVAS Active Operating Hours & Safety Sound Output Audit Logger", "ASIL B", "2000 ms", "Record lifetime acoustic sound generation hours and regulatory compliance tokens in secure memory.", "AvasAuditLogger_SWC", "1000 ms")
        ]
    }
    return specs

print("Cockpit expansion specifications library defined.")

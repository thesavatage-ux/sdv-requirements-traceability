# -*- coding: utf-8 -*-
"""
Body Domain expansion specifications library for FEAT-BDY-01 to FEAT-BDY-06.
"""

def get_bdy_expansion_specs():
    specs = {
        "FEAT-BDY-01": [
            ("Ultra-Wideband (UWB) Time-of-Flight Decimeter-Level Distance Ranging", "ASIL B", "50 ms", "Measure time-of-flight distance between vehicle transceivers and digital smartphone key with accuracy <= 10 cm.", "PepsUwbRanging_SWC", "20 ms"),
            ("Bluetooth Low Energy (BLE) RSSI Distance Proximity Channel Initiator", "ASIL B", "100 ms", "Detect approaching authorized smartphone key at 15 m distance to initiate wake-up lighting sequence.", "PepsBleProximity_SWC", "50 ms"),
            ("Cryptographic Challenge-Response Rolling Code Anti-Relay Attack Validator", "ASIL B", "20 ms", "Execute AES-128 cryptographic exchange with rolling counter: Invalidate key session if latency > 30 ms (relay attack).", "PepsCryptoValidator_SWC", "10 ms"),
            ("Interior vs Exterior Transceiver Key Spatial Localization Classifier", "ASIL B", "50 ms", "Distinguish whether authenticated key is inside or outside vehicle cabin to prevent uncommanded door lockouts.", "PepsSpatialClassifier_SWC", "20 ms"),
            ("Capacitive Door Handle Touch Sensor Approach & Grasp Debouncer", "ASIL B", "30 ms", "Sample door handle capacitive sensors: Unlock door latch within <= 150 ms of driver grasp detection.", "PepsTouchDebouncer_SWC", "10 ms"),
            ("Push-Button Start Ignition Relay Dual-Channel Interlock Supervisor", "ASIL B", "20 ms", "Verify authenticated key is inside cabin and brake pedal is depressed prior to closing starter/inverter relays.", "PepsIgnitionSupervisor_SWC", "10 ms"),
            ("Near-Field Communication (NFC) B-Pillar Backup Key Card Reader", "ASIL B", "50 ms", "Authenticate physical NFC smart card placed on B-pillar transceiver to allow vehicle ingress upon dead phone battery.", "PepsNfcReader_SWC", "20 ms"),
            ("Walk-Away Automatic Door Latch Locking & Perimeter Arming Governor", "ASIL B", "200 ms", "Lock all doors, fold side mirrors, and arm perimeter anti-theft alarm when key distance exceeds 2.5 m.", "PepsWalkAwayLock_SWC", "100 ms"),
            ("Keyless Entry Battery Low State-of-Charge HMI Warning Dispatcher", "ASIL A", "500 ms", "Detect low battery voltage in physical key fob transceiver and prompt cluster notification 'Replace Key Battery'.", "PepsKeyFobBattery_SWC", "200 ms"),
            ("DEM Digital Key Security Intrusion Diagnostics & Tamper Recorder", "ASIL B", "100 ms", "Log unauthorized access attempts, cryptographic replay attacks, and transceiver hardware faults to NVM.", "PepsDiagnosticManager_SWC", "50 ms"),
            ("Vehicle Anti-Theft Siren & Immobilizer High-Security Interlock", "ASIL B", "20 ms", "Trigger anti-theft alarm siren and inhibit powertrain start if unauthorized door entry is detected.", "PepsImmobilizer_SWC", "10 ms")
        ],
        "FEAT-BDY-02": [
            ("Matrix LED Headlamp 84-Pixel Array Independent Dimming Controller", "ASIL B", "20 ms", "Modulate PWM current to 84 independent micro-LED emitters to create dynamic shadow masks around vehicles.", "AdbMatrixDimmer_SWC", "10 ms"),
            ("Front Camera Oncoming & Preceding Vehicle Headlamp/Taillamp Tracker", "ASIL B", "30 ms", "Track coordinates and light intensity of forward vehicles up to 400 m ahead at 30 fps frame rate.", "AdbVehicleTracker_SWC", "15 ms"),
            ("High-Speed Dynamic Glare-Free Shadow Mask Polygon Generator", "ASIL B", "20 ms", "Calculate spatial exclusion box around detected vehicles, dimming target LEDs to < 1.0 lux glare limit.", "AdbGlareFreePolygon_SWC", "10 ms"),
            ("Vehicle Pitch Dynamic Leveling Sensor Axle Deflection Compensator", "ASIL B", "50 ms", "Compensate headlight vertical aim angle based on front/rear axle ride height sensors to eliminate glare over crests.", "AdbPitchLeveler_SWC", "20 ms"),
            ("Steering Angle Predictive Cornering Light Beam Swivel Commander", "ASIL B", "30 ms", "Swivel auxiliary LED cornering light beams up to +-15° into upcoming turns based on steering wheel angle.", "AdbCorneringSwivel_SWC", "15 ms"),
            ("Ambient Light & Twilight Automatic High-Beam Transition Sequencer", "ASIL B", "100 ms", "Transition smoothly between low beam and matrix high beam when ambient illuminance drops below 10 lux.", "AdbHighBeamSequencer_SWC", "50 ms"),
            ("City Low-Speed Broad Pedestrian Illumination Spread Optimizer", "ASIL B", "100 ms", "Widen horizontal low-beam spread pattern at speeds < 50 km/h to illuminate sidewalks and pedestrians.", "AdbCitySpread_SWC", "50 ms"),
            ("Highway High-Speed Long-Distance Concentrated Beam Booster", "ASIL B", "100 ms", "Concentrate central LED beam flux to extend illumination distance to 600 m at vehicle speeds > 110 km/h.", "AdbHighwayBooster_SWC", "50 ms"),
            ("Matrix Headlamp Heatsink Multi-Point Thermal Over-Temperature Derater", "ASIL B", "500 ms", "Derate LED forward drive current by 30% if headlamp aluminum heatsink temperature exceeds 85 °C.", "AdbThermalDerater_SWC", "100 ms"),
            ("Adverse Weather & Fog/Snow Back-Glare Light Dispersion Minimizer", "ASIL B", "200 ms", "Reduce upper matrix beam intensity during fog or heavy snow to prevent blinding reflections back into driver eyes.", "AdbWeatherDispersion_SWC", "100 ms"),
            ("Matrix LED Module Pixel Short/Open Circuit Hardware Safing Monitor", "ASIL B", "50 ms", "Detect burnt-out LED emitter pixels and re-balance drive current to adjacent pixels, logging DTC.", "AdbPixelFaultMonitor_SWC", "20 ms"),
            ("DEM Matrix Lighting Diagnostic Event Manager & Fault Code Latcher", "ASIL B", "100 ms", "Manage diagnostic trouble codes for leveling motor stall, camera feed timeout, and LED driver overvoltage.", "AdbDiagnosticManager_SWC", "50 ms"),
            ("Driver Matrix Lighting Mode Configuration & Instrument Cluster HMI", "ASIL A", "200 ms", "Display matrix high beam active status icon and driver sensitivity preference settings on cluster.", "AdbHmiDispatcher_SWC", "100 ms")
        ],
        "FEAT-BDY-03": [
            ("Central Crash Sensor 6-DOF IMU Accelerometer Longitudinal Impact Evaluator", "ASIL D", "1 ms", "Sample central crash accelerometers at 2000 Hz, calculating crash velocity change Delta-V within 15 ms.", "SrsImpactEvaluator_SWC", "0.2 ms"),
            ("Front Bumper Left/Right Satellite Crash Accelerometer Cross-Checker", "ASIL D", "1 ms", "Validate satellite crash sensor signals against central IMU to confirm genuine frontal barrier impact.", "SrsSatelliteCrossCheck_SWC", "0.2 ms"),
            ("B-Pillar Side Impact Pressure Satellite Sensor Pulse Integrator", "ASIL D", "1 ms", "Integrate door cavity air pressure pulse signals to detect T-bone side collisions within <= 8.0 ms.", "SrsSidePressureIntegrator_SWC", "0.2 ms"),
            ("Hardware Safing Accelerometer Independent Analog Interlock Circuit", "ASIL D", "1 ms", "Hardware analog safing sensor independently gates deployment power rail, preventing uncommanded firing.", "SrsHardwareSafing_SWC", "0.1 ms"),
            ("Dual-Stage Front Driver & Passenger Airbag Pyrotechnic Squib Firing Law", "ASIL D", "1 ms", "Fire Stage 1 squib (1.75 A for 2.0 ms) and Stage 2 squib timed 20-40 ms later based on crash severity.", "SrsSquibFiringLaw_SWC", "0.2 ms"),
            ("Side Curtain Airbag & Seat-Mounted Thorax Airbag Deployment Driver", "ASIL D", "1 ms", "Deploy rollover curtain airbags in <= 10 ms upon detecting vehicle roll rate exceeding 60 °/s with tilt > 35°.", "SrsCurtainDeployment_SWC", "0.2 ms"),
            ("Pyrotechnic Seatbelt Pretensioner & Dynamic Load Limiter Trigger", "ASIL D", "1 ms", "Fire pretensioner squibs in <= 5.0 ms of impact to retract 10 cm of seatbelt slack, locking occupant chest.", "SrsPretensionerDriver_SWC", "0.2 ms"),
            ("Passenger Seat Occupant Detection System (ODS) Weight & Child Seat Classifier", "ASIL B", "100 ms", "Classify passenger seat occupancy: Suppress passenger airbag deployment if weight < 15 kg (child seat).", "SrsOdsClassifier_SWC", "50 ms"),
            ("Deployment Energy Reserve Storage Capacitor Bank Voltage Monitor", "ASIL D", "10 ms", "Monitor backup firing capacitor bank: Guarantee sufficient stored energy (33V, 4700 µF) to fire squibs after battery cut.", "SrsCapacitorMonitor_SWC", "2 ms"),
            ("Post-Crash High-Voltage Battery Contactor Pyrofuse Immediate E-Trip", "ASIL D", "2 ms", "Broadcast hardwired crash confirmation signal to BMS to fire pyrofuse and de-energize 800V bus in <= 5 ms.", "SrsCrashEBusTrip_SWC", "0.5 ms"),
            ("Post-Crash Automatic Door Unlock, Hazard Flashers & Interior Light Egress Trigger", "ASIL B", "20 ms", "Unlock all doors, turn on interior cabin lamps, and activate hazard lights immediately following crash.", "SrsPostCrashEgress_SWC", "5 ms"),
            ("DEM Restraints Squib Resistance Line Continuity Diagnostic Monitor", "ASIL D", "50 ms", "Measure resistance of all squib firing loops (1.8 to 2.5 Ohm): Log DTC B0001 upon open or short circuit.", "SrsDiagnosticManager_SWC", "20 ms")
        ],
        "FEAT-BDY-04": [
            ("Cabin 4-Zone Temperature Setpoint & Solar Radiation Flux Balancer", "ASIL A", "200 ms", "Balance climate setpoints across 4 independent cabin quadrants based on multi-zone solar radiation sensors.", "HvacZoneBalancer_SWC", "100 ms"),
            ("Particulate Matter (PM2.5) & VOC Cabin Air Quality Sensor Observer", "ASIL A", "500 ms", "Sample laser PM2.5 and metal-oxide VOC sensors; activate cabin air recirculation if PM2.5 > 35 µg/m³.", "HvacAirQualityObserver_SWC", "200 ms"),
            ("Automated Fresh Air / Recirculation Damper Stepper Motor Servocontrol", "ASIL A", "100 ms", "Position motorized intake air flaps to switch between fresh air and high-efficiency HEPA recirculation.", "HvacRecircDamper_SWC", "50 ms"),
            ("Brushless Multi-Zone HVAC Blower Fan PWM Speed Governor", "ASIL A", "100 ms", "Regulate 12V brushless blower motor speed via PWM across 7 discrete flow levels with soft-start ramp.", "HvacBlowerGovernor_SWC", "50 ms"),
            ("Air Distribution Face, Footwell & Defrost Flap Actuator Synchronizer", "ASIL A", "100 ms", "Synchronize LIN bus stepper motor flap actuators to route airflow according to driver mode selection.", "HvacFlapSynchronizer_SWC", "50 ms"),
            ("Windshield Humidity Sensor & Predictive Glass Defogging Governor", "ASIL A", "200 ms", "Monitor windshield relative humidity: Turn on AC compressor and defrost vents before condensation forms.", "HvacDefogGovernor_SWC", "100 ms"),
            ("High-Voltage Cabin Air Electric Ionizer & Fragrance Dispenser Driver", "ASIL A", "500 ms", "Control negative ion generator and motorized fragrance cartridge dispenser to purify cabin atmosphere.", "HvacIonizerDriver_SWC", "200 ms"),
            ("Heated Steering Wheel & Multi-Stage Heated/Ventilated Seat Coordinator", "ASIL A", "200 ms", "Coordinate seat heating/ventilation PWM currents to reach target occupant surface thermal comfort.", "HvacSeatComfort_SWC", "100 ms"),
            ("Sub-Zero Ambient Heat Pump Auxiliary Heating Mode Request Arbitrator", "ASIL B", "500 ms", "Request thermal heat pump auxiliary cabin heat or PTC supplementary warmth during extreme winter cold.", "HvacHeatRequest_SWC", "200 ms"),
            ("Eco-Mode Cabin Occupancy-Based Thermal Zone Energy Conservator", "ASIL A", "1000 ms", "Shut down climate conditioning to unoccupied passenger seats when ECO driving mode is active.", "HvacEcoConservator_SWC", "500 ms"),
            ("HVAC LIN Stepper Motor Jam & Flap Travel Endpoint Self-Calibration", "ASIL A", "1000 ms", "Execute stall-detection homing sequence at key-on to calibrate flap physical endpoints (0-100%).", "HvacFlapCalibrator_SWC", "500 ms"),
            ("DEM HVAC Climate Sensor Diagnostic Event Manager & Fault Logger", "ASIL A", "200 ms", "Qualify diagnostic trouble codes for temperature thermistor open circuit and flap motor stalls.", "HvacDiagnosticManager_SWC", "100 ms"),
            ("Driver Central Touchscreen Climate Control HMI & Voice Command Interface", "ASIL A", "100 ms", "Process temperature target adjustments and fan speed changes from central display and voice assistant.", "HvacHmiDispatcher_SWC", "50 ms")
        ],
        "FEAT-BDY-05": [
            ("Power Liftgate & Window Dual Hall Sensor Position & Velocity Tracker", "ASIL B", "5 ms", "Count magnetic Hall sensor quadrature pulses to determine closure glass/lid position and closing velocity.", "SpcHallTracker_SWC", "2 ms"),
            ("FMVSS 118 Compliance Non-Reversal Anti-Pinch Force Observer", "ASIL B", "5 ms", "Differentiate motor velocity: Detect pinch resistance force (> 100 N) and reverse motor in <= 50 ms.", "SpcAntiPinchObserver_SWC", "1 ms"),
            ("Optical Infrared & Capacitive Seal Contactless Obstacle Detector", "ASIL B", "10 ms", "Detect human fingers approaching seal before physical contact, halting motor motion immediately.", "SpcContactlessSensor_SWC", "5 ms"),
            ("Power Liftgate Spindle Drive DC Motor H-Bridge PWM Driver", "ASIL B", "5 ms", "Control dual high-current H-bridge power stages driving spindle screw actuators with soft-stop ramping.", "SpcSpindleDriver_SWC", "2 ms"),
            ("Automatic Power Cincher Latch Motor Pull-In Sequence Governor", "ASIL B", "20 ms", "Engage motorized secondary latch cincher to pull liftgate or door from primary catch into full seal lock.", "SpcCincherGovernor_SWC", "10 ms"),
            ("Vehicle Motion Interlock Speed Gatekeeper (Door/Trunk Lockout)", "ASIL B", "20 ms", "Inhibit power door or liftgate opening commands whenever vehicle speed exceeds 3.0 km/h.", "SpcSpeedGatekeeper_SWC", "10 ms"),
            ("Tailgate Hands-Free Foot Kick Ultrasonic Sensor Gesture Recognizer", "ASIL B", "50 ms", "Process rear bumper kick sensor signals to validate intentional opening kick gesture under tailgate.", "SpcKickRecognizer_SWC", "20 ms"),
            ("Door Mechanical Resistance Wind Gust & Inclined Parking Gravity Compensator", "ASIL B", "20 ms", "Adjust motor closing torque profile dynamically when vehicle is parked on steep grades or in high winds.", "SpcGravityCompensator_SWC", "10 ms"),
            ("Power Closure DC Motor Thermal Overload Duty Cycle Guard", "ASIL B", "100 ms", "Inhibit repeated power closure activations if motor internal temperature exceeds 110 °C.", "SpcThermalGuard_SWC", "50 ms"),
            ("Power Window Emergency Express-Up Window Closure Safe Stop Logic", "ASIL B", "10 ms", "Halt one-touch express up window travel and reverse by 125 mm upon anti-pinch trigger.", "SpcExpressUpController_SWC", "5 ms"),
            ("DEM Power Closures Hall Sensor Fault Diagnostics & DTC Latcher", "ASIL B", "50 ms", "Detect missing Hall pulses while motor current is flowing (stall condition) and log DTC B1025.", "SpcDiagnosticManager_SWC", "20 ms"),
            ("Acoustic Warning Chime & Exterior Lamp Flasher Annunciation Driver", "ASIL A", "50 ms", "Sound exterior acoustic beeper and flash hazard lamps during automated liftgate opening/closing.", "SpcWarningChime_SWC", "20 ms")
        ],
        "FEAT-BDY-06": [
            ("Electrochromic Glass Segmented Suspended Particle Device (SPD) PWM Driver", "ASIL A", "20 ms", "Modulate 110V AC high-frequency PWM drive to SPD glass film to alter roof glass tint from 5% to 65%.", "EcRoofPwmDriver_SWC", "10 ms"),
            ("Multi-Zone Glass Roof Segment Independent Opacity Area Controller", "ASIL A", "50 ms", "Control opacity of 9 independent glass roof segments individually (e.g. driver opaque, passenger clear).", "EcRoofZoneController_SWC", "20 ms"),
            ("Ambient Sunlight Pyranometer Sensor Light Intensity Auto-Tinter", "ASIL A", "200 ms", "Automatically tint glass roof dark when ambient solar irradiance exceeds 600 W/m² to reduce cabin heat.", "EcRoofAutoTinter_SWC", "100 ms"),
            ("Cabin Thermal Heat Load Reduction & HVAC Efficiency Coordinator", "ASIL A", "500 ms", "Coordinate roof glass darkening with cabin HVAC to reduce air conditioning compressor electrical load by 15%.", "EcRoofThermalCoordinator_SWC", "200 ms"),
            ("Vehicle Parked Anti-Thermal Sunshield Automatic Darkening State Engine", "ASIL A", "1000 ms", "Transition all roof segments to 100% opaque mode when vehicle is parked in direct sunlight.", "EcRoofParkedShade_SWC", "500 ms"),
            ("Sub-Zero Ambient Glass Film Switching Latency Temperature Compensator", "ASIL A", "500 ms", "Adjust AC drive voltage amplitude to compensate for slower liquid crystal / SPD particle response at -20 °C.", "EcRoofColdCompensator_SWC", "200 ms"),
            ("Electrochromic High-Voltage Inverter Circuit Short-Circuit Hardware Safing", "ASIL B", "5 ms", "Hardware crowbar shuts down 110V AC glass power supply within <= 5 ms if glass crack or short is detected.", "EcRoofHardwareSafing_SWC", "1 ms"),
            ("Glass Film Leakage Current Resistance Insulation Fault Monitor", "ASIL B", "50 ms", "Measure insulation resistance between glass electrochromic layers and vehicle chassis ground.", "EcRoofInsulationMonitor_SWC", "20 ms"),
            ("Driver Overhead Console Gesture & Slide Touch Control Interface", "ASIL A", "50 ms", "Decode overhead swipe gestures to allow intuitive fingertip opacity dimming of roof segments.", "EcRoofGestureInterface_SWC", "20 ms"),
            ("Vehicle Crash Emergency Roof Instantaneous Clear Transparency Interlock", "ASIL A", "20 ms", "Clear glass roof transparency immediately upon airbag deployment signal to facilitate passenger rescue.", "EcRoofCrashUnlock_SWC", "5 ms"),
            ("DEM Electrochromic Roof Power Supply Diagnostics & DTC Logger", "ASIL A", "100 ms", "Qualify diagnostic trouble codes for glass film open-circuit, inverter failure, and solar sensor faults.", "EcRoofDiagnosticManager_SWC", "50 ms"),
            ("Central Touchscreen Roof Opacity Slider Graphic Display Serializer", "ASIL A", "100 ms", "Broadcast active roof segment opacity percentages to central touchscreen infotainment display.", "EcRoofHmiDispatcher_SWC", "50 ms"),
            ("Non-Volatile Electrochromic Glass Cumulative Operating Hours Tracker", "ASIL A", "2000 ms", "Record lifetime hours of energized glass operation to monitor long-term SPD film optical durability.", "EcRoofDutyCycleLogger_SWC", "1000 ms")
        ]
    }
    return specs

print("Body expansion specifications library defined.")

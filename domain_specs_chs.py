# -*- coding: utf-8 -*-
"""
Chassis Domain expansion specifications library for FEAT-CHS-03 to FEAT-CHS-08.
"""

def get_chs_expansion_specs():
    specs = {
        "FEAT-CHS-03": [
            ("Dual Redundant Hydraulic Circuit Pressure Transducer Cross-Monitor", "ASIL D", "10 ms", "Cross-check primary and secondary circuit pressure sensors: If discrepancy > 4.0 bar, isolate affected circuit.", "BbwPressureCrossCheck_SWC", "2 ms"),
            ("Electric Brake Plunger Motor Hall & Resolver Angle Decoupled Decoder", "ASIL D", "1 ms", "Decode high-speed motor position to regulate electric plunger displacement with precision +-0.05 mm.", "BbwPlungerResolver_SWC", "0.5 ms"),
            ("Decoupled Brake Pedal Force-Displacement Active Hysteresis Shaper", "ASIL D", "10 ms", "Modulate pedal feel simulator hydraulic orifice valve to create 15% tactile return hysteresis.", "BbwPedalHysteresis_SWC", "5 ms"),
            ("Foundation Caliper Pad Knock-Back Clearance Active Eliminator", "ASIL D", "20 ms", "Pulse 2.5 bar hydraulic pressure following severe cornering to restore zero pad-to-rotor clearance gap.", "BbwPadClearance_SWC", "5 ms"),
            ("Brake Fluid Vaporization & Temperature Dependent Pressure Compensator", "ASIL D", "50 ms", "Increase plunger stroke target if brake fluid boiling point degradation or seal compliance expands.", "BbwFluidCompensation_SWC", "20 ms"),
            ("Passive Hydraulic Mechanical Push-Through Solenoid Power Cut Safing", "ASIL D", "5 ms", "De-energize normally-open separation valves in <= 15 ms upon complete power loss, enabling manual braking.", "BbwMechanicalSafing_SWC", "1 ms"),
            ("Brake Fluid Low Level Reservoir Reed Switch Debouncer & Warning Gate", "ASIL B", "100 ms", "Debounce fluid level sensor to illuminate master brake warning tell-tale before air enters master cylinder.", "BbwFluidLevelMonitor_SWC", "50 ms"),
            ("Dynamic Electronic Brake Proportioning (EBD) Under Variable Payloads", "ASIL D", "10 ms", "Modulate front/rear caliper pressure ratio based on axle load cells and deceleration gradient.", "BbwEbdRegulator_SWC", "5 ms"),
            ("Secondary Brake Boost Redundant Channel Autonomous Takeover Engine", "ASIL D", "10 ms", "Ramp secondary electronic brake booster channel to 100% capacity in <= 20 ms if primary channel faults.", "BbwRedundantTakeover_SWC", "2 ms"),
            ("Dual Core Lockstep CPU Execution Flow & Watchdog Supervisor", "ASIL D", "2 ms", "Execute cyclic challenge-response with external watchdog ASIC; reset and cut valves upon execution crash.", "BbwLockstepSupervisor_SWC", "1 ms"),
            ("DEM Brake System Hydraulic Leakage Diagnostics & Freeze-Frame Storage", "ASIL D", "20 ms", "Detect caliper circuit fluid leak by monitoring plunger volume vs pressure buildup; latch DTC C1102.", "BbwDiagnosticManager_SWC", "10 ms"),
            ("Non-Volatile Brake Service Duty Cycles & Caliper Wear Buffer", "ASIL B", "1000 ms", "Log lifetime brake applications, maximum peak pressures, and thermal exposure in non-volatile flash.", "BbwServiceLogger_SWC", "500 ms")
        ],
        "FEAT-CHS-04": [
            ("Chassis 3D Rigid Body Modal Motion Observer (Heave, Pitch, Roll)", "ASIL C", "10 ms", "Synthesize rigid body heave velocity, pitch rate, and roll rate from 3 body accelerometers and 4 height sensors.", "EdcModalObserver_SWC", "5 ms"),
            ("Skyhook Body Inertial Damping Continuously Variable Force Generator", "ASIL C", "10 ms", "Compute Skyhook damping force: F_sky = -C_sky * V_body_vertical, isolating cabin from road surface inputs.", "EdcSkyhookController_SWC", "5 ms"),
            ("Groundhook Wheel Unsprung Mass Hop & Tire Grip Optimizer", "ASIL C", "10 ms", "Modulate damper force at wheel hop resonance (10-14 Hz) to maximize continuous tire-to-road contact.", "EdcGroundhookController_SWC", "5 ms"),
            ("Aggressive Steering Angle Anticipatory Anti-Roll Stiffness Booster", "ASIL C", "10 ms", "Ramp corner dampers to maximum rebound/compression in <= 15 ms upon fast steering inputs (> 120 °/s).", "EdcAntiRollBooster_SWC", "2 ms"),
            ("Panic Braking Anti-Dive & Hard Acceleration Anti-Squat Pitch Regulator", "ASIL C", "10 ms", "Stiffen front dampers during braking and rear dampers during acceleration to minimize body pitch.", "EdcAntiPitchController_SWC", "5 ms"),
            ("Road Roughness Pothole Impact Fast Pressure Relief Protection", "ASIL C", "5 ms", "Detect severe wheel impact acceleration (> 30 m/s²) and soften damper in < 8 ms to protect strut mounts.", "EdcPotholeRelief_SWC", "2 ms"),
            ("Proportional Hydraulic Damper Solenoid PWM Current Closed-Loop Driver", "ASIL C", "2 ms", "Regulate solenoid coil current between 0.2A and 1.8A with current tracking error <= 15 mA.", "EdcCurrentDriver_SWC", "1 ms"),
            ("Corner Damper Solenoid Coil Multi-Point Thermal Protection Derater", "ASIL B", "100 ms", "Derate continuous coil current if coil temperature exceeds 120 °C to prevent thermal insulation breakdown.", "EdcThermalDerater_SWC", "50 ms"),
            ("Suspension Deflection Height Sensor Plausibility & Geometry Cross-Check", "ASIL C", "10 ms", "Verify height sensors against kinematic planar chassis geometry: Flag sensor drift if discrepancy > 8.0 mm.", "EdcHeightPlausibility_SWC", "5 ms"),
            ("Fail-Safe Passive Mid-Firm Default Mechanical Hydraulic Fallback Mode", "ASIL C", "10 ms", "De-energize all 4 damper solenoids to 0.0A upon electrical fault, locking dampers in safe mid-firm baseline.", "EdcFailSafeFallback_SWC", "2 ms"),
            ("DEM Suspension Damping Fault Diagnostics & Valve Open/Short Detector", "ASIL B", "50 ms", "Qualify diagnostic trouble codes for coil open-circuit or height sensor linkage disconnection.", "EdcDiagnosticManager_SWC", "20 ms"),
            ("Driver Drive Mode Selection (Comfort, Standard, Sport) Characteristic Tuner", "ASIL B", "100 ms", "Interpolate 3D damper force-velocity lookup tables according to active cabin drive mode switch.", "EdcModeSelector_SWC", "50 ms"),
            ("Non-Volatile Damper Cumulative Energy Dissipation & Wear Life Monitor", "ASIL B", "1000 ms", "Integrate damper work done over time to predict shock absorber seal wear and fluid degradation.", "EdcEnergyLogger_SWC", "500 ms")
        ],
        "FEAT-CHS-05": [
            ("Multi-Motor Dual-Axle Real-Time Yaw Disturbance Moment Calculator", "ASIL D", "10 ms", "Compute required stabilizing yaw moment: M_z = C_yaw * (Psi_dot_actual - Psi_dot_target) at 100 Hz.", "EawdYawMoment_SWC", "2 ms"),
            ("Individual Left/Right Wheel Independent Torque Allocation Engine", "ASIL D", "10 ms", "Distribute positive drive torque to outer wheel and regenerative braking to inner wheel during cornering.", "EawdTorqueAllocator_SWC", "2 ms"),
            ("Tire Longitudinal & Lateral Friction Adhesion Circle G-G Diagram Observer", "ASIL D", "10 ms", "Estimate tire grip capacity via friction ellipse, ensuring torque vectoring does not exceed peak traction.", "EawdFrictionCircle_SWC", "2 ms"),
            ("Front/Rear Axle High-Speed Planetary Torque Split Dynamic Regulator", "ASIL D", "10 ms", "Vary front-to-rear torque split continuously between 100:0 (FWD efficiency) and 20:80 (RWD dynamics).", "EawdAxleSplitter_SWC", "5 ms"),
            ("Low-Friction Surface Split-Mu Cross-Axle Dynamic Slip Limiter", "ASIL D", "10 ms", "Limit cross-axle wheel speed differential when one wheel encounters ice or snow, simulating locked diff.", "EawdSlipLimiter_SWC", "2 ms"),
            ("High-Speed Understeer Neutralization & Corner Apex Pull-In Commander", "ASIL D", "10 ms", "Increase outer-rear motor torque by up to +180 Nm to tuck vehicle nose into high-speed corner apexes.", "EawdUndersteerPullIn_SWC", "5 ms"),
            ("Oversteer Dynamic Counter-Torque Yaw Dampening Stabilization Loop", "ASIL D", "10 ms", "Reduce outer rear wheel torque and apply forward torque to outer front wheel to catch oversteer slides.", "EawdOversteerDamp_SWC", "2 ms"),
            ("Multi-Inverter Coordinated CAN-FD Fast Command Dispatcher with E2E CRC", "ASIL D", "2 ms", "Broadcast synchronized torque requests to 4 independent corner inverters with alive counter and CRC.", "EawdE2EDispatcher_SWC", "1 ms"),
            ("Inverter Fast Single-Wheel Cutoff & Symmetrical Neutral Fallback Safing", "ASIL D", "5 ms", "Isolate faulted corner motor within <= 8 ms, zeroing opposite motor vectoring to prevent uncommanded yaw.", "EawdSafingIsolation_SWC", "2 ms"),
            ("Dual Core Lockstep Torque Comparison & Plausibility Gatekeeper", "ASIL D", "2 ms", "Verify that vectoring torque sum matches total driver accelerator demand within +-5.0 Nm.", "EawdLockstepGatekeeper_SWC", "1 ms"),
            ("DEM Torque Vectoring Diagnostics & Inverter Communication Fault Logger", "ASIL B", "50 ms", "Qualify diagnostic fault codes upon corner inverter dropouts and latch freeze-frame telemetry.", "EawdDiagnosticManager_SWC", "20 ms"),
            ("Instrument Cluster Dynamic AWD Torque Distribution Graphic Renderer", "ASIL B", "50 ms", "Transmit 4-wheel real-time torque delivery percentages to central instrument cluster display.", "EawdHmiRenderer_SWC", "20 ms"),
            ("Non-Volatile Thermal Stress & Corner Inverter Energy Throughput Tracker", "ASIL B", "1000 ms", "Log cumulative torque vectoring duration and corner thermal stresses in non-volatile storage.", "EawdStressTracker_SWC", "500 ms")
        ],
        "FEAT-CHS-06": [
            ("Chassis Ride Height Multi-Corner Closed-Loop Leveling Regulator", "ASIL C", "50 ms", "Maintain target suspension ride height across all 4 air springs with steady-state precision +-2.0 mm.", "EasLevelingRegulator_SWC", "20 ms"),
            ("Forward Road Preview Stereo Camera Pothole & Bump Active Adjuster", "ASIL C", "30 ms", "Pre-adjust air spring volume 150 ms ahead of upcoming road speed bumps detected by vision preview.", "EasRoadPreview_SWC", "15 ms"),
            ("Vehicle Speed-Dependent Aerodynamic Ride Height Lowering Scheduler", "ASIL C", "100 ms", "Lower vehicle chassis height by 20 mm at speeds > 120 km/h to reduce aerodynamic drag coefficient by 4%.", "EasAeroScheduler_SWC", "50 ms"),
            ("Pneumatic Air Compressor High-Pressure Reservoir Pressure Servoloop", "ASIL C", "100 ms", "Operate electric air compressor (up to 16.0 bar) to recharge high-pressure air reservoir tank.", "EasCompressorServo_SWC", "50 ms"),
            ("Multi-Channel Solenoid Valve Block Cross-Corner Inflation Governor", "ASIL C", "20 ms", "Pulse individual corner air spring solenoid valves with PWM duty cycles to adjust corner height.", "EasValveGovernor_SWC", "10 ms"),
            ("Passenger & Luggage Variable Payload Ingress/Egress Static Leveler", "ASIL B", "200 ms", "Level chassis automatically when passengers enter/exit or heavy luggage is placed in the rear cargo trunk.", "EasPayloadLeveler_SWC", "100 ms"),
            ("Terrain Drive Mode Selection (Off-Road High, Standard, Access Low) Manager", "ASIL B", "100 ms", "Transition chassis ground clearance across +50 mm (Off-Road), 0 mm (Standard), and -40 mm (Access mode).", "EasModeSelector_SWC", "50 ms"),
            ("Air Compressor Thermal Protection Temperature Sensor & Duty Cycle Guard", "ASIL B", "100 ms", "Halt compressor pumping if compressor cylinder head temperature exceeds 125 °C to prevent seal burnout.", "EasCompressorThermal_SWC", "50 ms"),
            ("Pneumatic Line Slow Leak & Pressure Loss Dynamic Observer", "ASIL C", "500 ms", "Detect air bladder micro-leaks by observing continuous uncommanded corner height sag overnight.", "EasLeakObserver_SWC", "200 ms"),
            ("Pneumatic Valve Cross-Axle Pressure Balance & Anti-Roll Stabilization", "ASIL C", "20 ms", "Cross-couple left and right air springs during high-speed cornering to suppress vehicle roll angles.", "EasRollStabilizer_SWC", "10 ms"),
            ("Air Suspension System Fault Fallback & Mechanical Bump-Stop Safing", "ASIL C", "20 ms", "Lock valve block in sealed hold state upon electrical loss; rely on internal polyurethane jounce bumpers.", "EasFailsafeLock_SWC", "10 ms"),
            ("DEM Pneumatic Suspension DTC Qualification & Sensor Calibration Manager", "ASIL B", "100 ms", "Manage diagnostic trouble codes for height sensor drift, valve stuck closed, and compressor faults.", "EasDiagnosticManager_SWC", "50 ms"),
            ("Non-Volatile Air Spring Cyclic Stress & Compressor Operating Hours Logger", "ASIL B", "2000 ms", "Record lifetime compressor run hours, air spring inflation cycles, and extreme elevation events.", "EasServiceLogger_SWC", "1000 ms")
        ],
        "FEAT-CHS-07": [
            ("Rear-Wheel Steering Low-Speed Counter-Phase Agility Angle Calculator", "ASIL D", "10 ms", "Compute counter-phase rear wheel steering angle (up to -8.0° opposite to front wheels) at speeds < 40 km/h.", "RwsCounterPhase_SWC", "2 ms"),
            ("High-Speed Co-Phase Directional Stability Rear Steering Angle Calculator", "ASIL D", "10 ms", "Compute co-phase rear wheel steering angle (up to +3.5° matching front wheels) at speeds > 70 km/h.", "RwsCoPhase_SWC", "2 ms"),
            ("Zero-Yaw Dynamic Crab Angle & Lateral Lane Change Transition Law", "ASIL D", "10 ms", "Synthesize co-phase steering angle to allow lateral lane translation with zero vehicle body yaw rotation.", "RwsCrabAngle_SWC", "2 ms"),
            ("Rear Steering Electromechanical Linear Actuator Closed-Loop Position Servo", "ASIL D", "2 ms", "Drive brushless motor actuator to position rear toe links with positional accuracy <= 0.05°.", "RwsActuatorServo_SWC", "0.5 ms"),
            ("Dual Redundant Hall/Resolver Rear Toe-Angle Sensor Cross-Monitor", "ASIL D", "2 ms", "Cross-check dual independent rear wheel angle sensors: Trip fault if discrepancy > 0.20° roadwheel angle.", "RwsSensorCrossCheck_SWC", "0.5 ms"),
            ("Dual-Inverter Symmetrical Motor Winding Load Sharing Controller", "ASIL D", "2 ms", "Partition demanded rear steering force 50/50 across dual independent inverter channels.", "RwsInverterLoadShare_SWC", "0.5 ms"),
            ("Single-Channel Fault Autonomous 100% Load Takeover in <= 5 ms", "ASIL D", "5 ms", "Ramp healthy inverter to full power in <= 5 ms if one winding bridge reports electrical fault.", "RwsSingleChannelTakeover_SWC", "1 ms"),
            ("Rear Mechanical Spring-Loaded Center-Lock Fallback Mechanism", "ASIL D", "10 ms", "De-energize electromagnetic brake to allow mechanical centering spring to lock rear wheels at 0.0° in <= 50 ms.", "RwsCenterLockSafing_SWC", "2 ms"),
            ("ESC Stability Override & Rear-Axle Active Counter-Steer Yaw Damper", "ASIL D", "5 ms", "Apply up to +-2.5° fast rear counter-steer in <= 30 ms to stabilize split-mu braking or oversteer slides.", "RwsEscCounterSteer_SWC", "2 ms"),
            ("Rear Wheel Tire Kinematic Clearance & Suspension Bump Envelope Guard", "ASIL D", "10 ms", "Clamp maximum rear steering angle as suspension compresses to prevent tire rubbing wheel arch liners.", "RwsClearanceGuard_SWC", "5 ms"),
            ("Actuator Thermal Overload & Continuous High-Load Torque Derater", "ASIL B", "100 ms", "Derate maximum rear steering rate if motor winding temperature exceeds 135 °C during repeated slaloms.", "RwsThermalDerater_SWC", "50 ms"),
            ("Dual Core Lockstep Microcontroller Safety Gatekeeper & Token Validator", "ASIL D", "2 ms", "Verify execution tokens between Core 0 and Core 1; fire center-lock pin upon computation disagreement.", "RwsLockstepGatekeeper_SWC", "1 ms"),
            ("DEM Rear-Wheel Steering Diagnostic Event Manager & DTC Logger", "ASIL D", "20 ms", "Qualify diagnostic fault codes for actuator jam, resolver error, and mechanical center-lock failures.", "RwsDiagnosticManager_SWC", "10 ms"),
            ("Instrument Cluster Rear-Wheel Steering Health Status & Turning Radius HMI", "ASIL B", "50 ms", "Transmit RWS operational status, turning circle animation, and warning messages to cluster display.", "RwsHmiDispatcher_SWC", "20 ms")
        ],
        "FEAT-CHS-08": [
            ("Chassis Dynamic Body Roll Moment Lateral Acceleration Observer", "ASIL C", "10 ms", "Estimate overturning roll moment from lateral accelerometer, steering angle rate, and vehicle mass.", "EarsRollMomentObserver_SWC", "2 ms"),
            ("Active Anti-Roll Bar Front/Rear Dynamic Roll Stiffness Proportioner", "ASIL C", "10 ms", "Distribute roll stiffness between front and rear axles to modulate understeer/oversteer handling balance.", "EarsStiffnessProportioner_SWC", "2 ms"),
            ("High-Torque 48V Electromechanical Roll Actuator Closed-Loop Servo", "ASIL C", "2 ms", "Drive front/rear 48V brushless stabilizer motor actuators to deliver up to 1200 Nm anti-roll torque.", "EarsActuatorServo_SWC", "0.5 ms"),
            ("Straight-Line Single-Wheel Roughness Decoupling & Ride Comfort Optimizer", "ASIL C", "10 ms", "Decouple left and right anti-roll bar halves on straight bumpy roads to eliminate single-wheel head toss.", "EarsDecouplingManager_SWC", "5 ms"),
            ("High-G Emergency Evasive Swerve Dynamic Roll Suppression Commander", "ASIL C", "5 ms", "Apply maximum counter-roll torque in <= 20 ms to keep vehicle body perfectly flat during double lane change.", "EarsRollSuppression_SWC", "2 ms"),
            ("Actuator Planetary Gearbox Torque Sensor Cross-Plausibility Monitor", "ASIL C", "5 ms", "Cross-check dual strain-gauge torque transducers on anti-roll bar shaft: Trip if discrepancy > 35 Nm.", "EarsTorqueCrossCheck_SWC", "2 ms"),
            ("48V Power Supply Brownout Current Clamping & Torque Derater", "ASIL C", "10 ms", "Clamp peak motor current if 48V supply voltage sags below 40.0V during high-demand roll events.", "EarsVoltageDerater_SWC", "5 ms"),
            ("Multi-Node Stabilizer Motor Stator Thermal Protection Derating Law", "ASIL B", "100 ms", "Derate continuous anti-roll torque by 50% if actuator motor housing temperature exceeds 130 °C.", "EarsThermalDerater_SWC", "50 ms"),
            ("Actuator Mechanical Clutch Fail-Passive Decoupling Safing Engine", "ASIL C", "10 ms", "De-energize electromagnetic actuator clutch to convert active bar into standard passive anti-roll bar.", "EarsFailPassiveSafing_SWC", "2 ms"),
            ("Dual Core Lockstep Execution Supervisor & Safing Relay Trigger", "ASIL C", "2 ms", "Cross-compare calculated torque demands across dual cores; trip hardware relay if outputs differ.", "EarsLockstepSupervisor_SWC", "1 ms"),
            ("DEM Active Roll Stabilization Diagnostic Event Manager & DTC Latcher", "ASIL B", "50 ms", "Qualify diagnostic trouble codes for motor stall, torque sensor failure, and clutch disconnect errors.", "EarsDiagnosticManager_SWC", "20 ms"),
            ("Instrument Cluster Dynamic Cornering G & Active Roll Bar Display HMI", "ASIL B", "50 ms", "Broadcast vehicle roll angle suppression percentage and lateral G to digital instrument cluster.", "EarsHmiDispatcher_SWC", "20 ms"),
            ("Non-Volatile Severe Dynamic Lateral Maneuvers & Roll Stress Logger", "ASIL B", "1000 ms", "Log extreme roll moment events (> 1000 Nm) and cumulative chassis fatigue cycles in non-volatile flash.", "EarsStressLogger_SWC", "500 ms")
        ]
    }
    return specs

print("Chassis expansion specifications library defined.")

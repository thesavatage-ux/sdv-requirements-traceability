# -*- coding: utf-8 -*-
"""
Full SDV Platform Requirements Expansion Engine.
Covers all 40 features across ADAS, Powertrain, Chassis, Body, Cockpit, and Connectivity.
"""

import features_adas_full
import features_pwr_full
import features_chs_full
import features_bdy_full
import features_cpt_full
import features_conn_full

def get_all_domain_specs():
    specs = {
        # POWERTRAIN DOMAIN
        "FEAT-PWR-01": [
            ("Cell Over-Voltage Hardware Safing & Fast Contactor Trip", "ASIL D", "10 ms", "Monitor individual cell voltages via AFE: If any cell exceeds 4.25V for > 10 ms, fire pyrofuse and open main contactors.", "BmsOvervoltage_SWC", "1 ms"),
            ("Cell Under-Voltage Protection & Discharge Power Limiter", "ASIL D", "20 ms", "Derate propulsion discharge power to zero as cell voltage approaches 2.70V to prevent copper dendrite short circuits.", "BmsUndervoltage_SWC", "5 ms"),
            ("High-Voltage Isolation Resistance Continuous Earth Monitor", "ASIL D", "100 ms", "Measure isolation resistance between HV bus and chassis ground: Trigger warning if isolation drops below 500 Ohm/V.", "BmsIsolationMonitor_SWC", "50 ms"),
            ("High-Voltage Interlock Loop (HVIL) Wire-Break Detector", "ASIL D", "10 ms", "Drive continuous 20 mA square-wave through HVIL loop: If continuity is broken, de-energize contactors in <= 10 ms.", "BmsHvilSupervisor_SWC", "2 ms"),
            ("Battery Pack Multi-Point Thermal Runaway Early Warning", "ASIL D", "50 ms", "Detect sudden thermal gradient (> 2.0 °C/s) or off-gassing pressure spike, asserting emergency pack eject/cool down.", "BmsThermalRunaway_SWC", "10 ms"),
            ("High-Current Pyro-Fuse Actuation & Short-Circuit Safing", "ASIL D", "5 ms", "Trigger pyrofuse squib firing in <= 2.0 ms upon detecting severe short-circuit current exceeding 3000 A.", "BmsPyrofuseDriver_SWC", "1 ms"),
            ("State of Charge (SOC) Extended Kalman Filter Observer", "ASIL C", "100 ms", "Estimate battery pack state-of-charge with error <= 2.0% across complete charge/discharge lifecycle.", "BmsSocObserver_SWC", "50 ms"),
            ("State of Health (SOH) Capacity & Internal Resistance Estimator", "ASIL B", "500 ms", "Estimate battery degradation, capacity fade, and cell internal resistance growth during charging cycles.", "BmsSohEstimator_SWC", "100 ms"),
            ("Active & Passive Cell Balancing Symmetrical Switched Resistor Matrix", "ASIL B", "500 ms", "Bleed charge from higher-voltage cells during top-balancing to maintain cell delta <= 15 mV at full charge.", "BmsCellBalancer_SWC", "200 ms"),
            ("DEM Non-Volatile Battery Cycle Life & Stress Buffer", "ASIL B", "100 ms", "Log cumulative Ah throughput, temperature extremes, and DTCs in non-volatile EEPROM memory.", "BmsDiagnosticManager_SWC", "50 ms")
        ],
        "FEAT-PWR-02": [
            ("Traction Motor Multi-Channel Accelerator Pedal Cross-Check", "ASIL D", "10 ms", "Sample dual potentiometric/Hall pedal sensors: If disagreement > 5.0% for > 30 ms, drop torque request to zero.", "VcuPedalCrossCheck_SWC", "2 ms"),
            ("Inverter Space Vector Modulation (SVM) Stator Flux Controller", "ASIL D", "1 ms", "Compute d-q axis direct and quadrature current setpoints to deliver motor electromagnetic torque with precision +-2.0 Nm.", "VcuFocController_SWC", "0.5 ms"),
            ("Powertrain Dynamic Torque Arbitration (Driver vs ACC vs ESC)", "ASIL D", "5 ms", "Arbitrate between driver demand, ADAS cruise commands, and ESC stability torque clamps with strict safety priority.", "VcuTorqueArbitrator_SWC", "2 ms"),
            ("Motor Rotor Resolver-to-Digital Angle Decoding & Position Observer", "ASIL D", "1 ms", "Decode high-speed resolver feedback with 16-bit resolution to synchronize stator rotating magnetic field.", "VcuResolverDecoder_SWC", "0.5 ms"),
            ("Active Inverter Discharge & DC Link Capacitor Bleed Resistor Manager", "ASIL D", "20 ms", "Discharge 800V DC link capacitor to < 60V in <= 2.0 seconds upon crash signal or ignition shutdown.", "VcuActiveDischarge_SWC", "5 ms"),
            ("Traction Inverter Phase Over-Current Hardware Trip Monitor", "ASIL D", "1 ms", "Hardware comparator trips all 6 IGBT/SiC gate drives in < 2.0 µs upon current exceeding 850 A peak.", "VcuOvercurrentTrip_SWC", "0.2 ms"),
            ("Motor Stator Winding & Rotor Magnet Multi-Zone Thermal Derater", "ASIL B", "100 ms", "Derate peak motor torque continuously from 400 Nm to 120 Nm as winding temperature rises from 140 °C to 165 °C.", "VcuThermalDerater_SWC", "50 ms"),
            ("Creep Torque & Hill Hold Powertrain Standstill Speed Governor", "ASIL B", "20 ms", "Govern low-speed vehicle creep velocity to 4.0 km/h and prevent vehicle roll-back on 20% slopes.", "VcuCreepGovernor_SWC", "10 ms"),
            ("Dual Core Lockstep Execution Flow & Watchdog Supervisor", "ASIL D", "2 ms", "Supervise lockstep CPU execution tokens and trip independent safing relay upon ALU discrepancies.", "VcuLockstepWdg_SWC", "1 ms"),
            ("DEM Powertrain DTC Qualification & Torque Limitation Logging", "ASIL B", "50 ms", "Qualify diagnostic trouble codes for inverter communication loss and latch freeze-frame snapshots.", "VcuDiagnosticManager_SWC", "20 ms")
        ],
        "FEAT-PWR-03": [
            ("Regenerative Braking Deceleration Intent & Pedal Stroke Mapper", "ASIL D", "10 ms", "Map brake pedal initial stroke (0 to 15 mm) to regenerative deceleration torque (up to -0.3g) seamlessly.", "RbcPedalMapper_SWC", "5 ms"),
            ("One-Pedal Drive Accelerator Lift-Off Deceleration Synthesizer", "ASIL B", "20 ms", "Synthesize progressive deceleration (up to -0.22g) as driver lifts off accelerator pedal, bringing car to complete stop.", "RbcOnePedalDrive_SWC", "10 ms"),
            ("Hydraulic Foundation & Electric Motor Torque Blending Coordinator", "ASIL D", "10 ms", "Blend electric regen torque with hydraulic friction brakes: Prioritize regen while preserving total driver deceleration.", "RbcTorqueBlender_SWC", "5 ms"),
            ("ABS Wheel Slip Detection & Instantaneous Regen Cutoff Safing", "ASIL D", "10 ms", "Cut electric regenerative braking torque to zero in <= 20 ms upon ABS activation to ensure directional stability.", "RbcAbsRegenCutoff_SWC", "2 ms"),
            ("High-Voltage Battery Full Charge (SOC > 95%) Regen Derating Envelope", "ASIL C", "50 ms", "Smoothly reduce regenerative braking capability from 100% to 0% as battery SOC rises from 92% to 98%.", "RbcSocDerater_SWC", "20 ms"),
            ("Low-Temperature Battery Pack Regen Current Ingestion Limiter", "ASIL C", "100 ms", "Limit maximum regen charging current when battery temperature < 0 °C to prevent lithium plating damage.", "RbcColdDerater_SWC", "50 ms"),
            ("Front/Rear Axle Regen Braking Stability Distribution Law", "ASIL D", "10 ms", "Distribute regenerative deceleration between front and rear e-axles according to dynamic tire friction limits.", "RbcAxleDistributor_SWC", "5 ms"),
            ("Powertrain Regen Active Driveline Damping & Anti-Shudder Filter", "ASIL B", "10 ms", "Apply anti-resonance notch filter to regen torque demands to eliminate driveline backlash clunk and judder.", "RbcAntiShudder_SWC", "5 ms"),
            ("Regenerative Deceleration Brake Lamp Automatic Illumination", "ASIL B", "50 ms", "Illuminate vehicle rear brake lamps automatically whenever regenerative deceleration exceeds -0.7 m/s² (ECE R13H).", "RbcBrakeLampDriver_SWC", "20 ms"),
            ("DEM Regenerative Braking Fault Isolation & Hydraulic Handover Manager", "ASIL D", "20 ms", "Seamlessly transfer 100% braking authority to hydraulic friction brakes upon inverter communication fault.", "RbcDiagnosticManager_SWC", "10 ms"),
            ("Non-Volatile Regeneration Energy Harvest Efficiency Recorder", "ASIL B", "500 ms", "Log cumulative kilowatt-hours of kinetic energy recovered per drive cycle in non-volatile flash.", "RbcEnergyLogger_SWC", "200 ms")
        ],
        "FEAT-PWR-04": [
            ("Heat Pump Multi-Port Coolant Valve Position Servocontrol", "ASIL B", "50 ms", "Position 8-way octovalve coolant manifold stepper motors with angular accuracy +-1.5° to route thermal loops.", "TmsCoolantValve_SWC", "20 ms"),
            ("Electric Scroll AC Compressor High-Voltage Inverter Speed Governor", "ASIL B", "100 ms", "Regulate 800V electric compressor rotational speed between 800 RPM and 8500 RPM via CAN-FD setpoints.", "TmsCompressorGovernor_SWC", "50 ms"),
            ("Battery Pack Liquid Chiller Heat Exchanger Thermal Regulator", "ASIL B", "100 ms", "Maintain battery coolant inlet temperature within optimal 25 °C to 35 °C window during DC fast charging.", "TmsBatteryChiller_SWC", "50 ms"),
            ("Traction Inverter & Motor Waste Heat Scavenging Recirculator", "ASIL B", "100 ms", "Scavenge powertrain waste heat from drive units to heat cabin during sub-zero ambient winter driving.", "TmsWasteHeatScavenger_SWC", "50 ms"),
            ("Cabin Evaporator Anti-Frost & Electronic Expansion Valve (EXV) Controller", "ASIL B", "50 ms", "Modulate EXV orifice opening via PWM to maintain superheat target (5.0 K) and prevent evaporator core freeze-up.", "TmsExvController_SWC", "20 ms"),
            ("High-Voltage Positive Temperature Coefficient (PTC) Cabin Heater Driver", "ASIL B", "100 ms", "Modulate 6.0 kW HV PTC ceramic heater current using PWM power stage to deliver rapid cabin warmup.", "TmsPtcHeaterDriver_SWC", "50 ms"),
            ("Refrigerant Circuit High/Low Pressure Transducer Plausibility Monitor", "ASIL B", "50 ms", "Sample pressure transducers: Trip compressor shutdown if discharge pressure exceeds 32.0 bar.", "TmsPressureMonitor_SWC", "20 ms"),
            ("Radiator Active Grille Shutter (AGS) Aerodynamic Drag Optimizer", "ASIL B", "200 ms", "Modulate motorized aerodynamic grille shutters (0% closed to 100% open) based on vehicle speed and thermal demand.", "TmsAgsController_SWC", "100 ms"),
            ("Coolant Loop Degas Reservoir Fluid Level Sensor Debouncer", "ASIL B", "500 ms", "Debounce reed-switch coolant level sensor to alert driver to coolant loss before pump cavitates.", "TmsLevelMonitor_SWC", "200 ms"),
            ("Sub-Zero Ambient Battery Preconditioning Target Thermal Scheduler", "ASIL B", "1000 ms", "Pre-heat battery pack to 30 °C prior to scheduled DC fast charging arrival using route navigation cues.", "TmsPreconditioning_SWC", "500 ms"),
            ("Thermal System Sensor Diagnostic Event Management & DTC Latching", "ASIL B", "100 ms", "Qualify diagnostic trouble codes for refrigerant leaks, valve stiction, and temperature sensor drift.", "TmsDiagnosticManager_SWC", "50 ms"),
            ("Thermal Loop Power Budget Arbitration with Powertrain Energy Manager", "ASIL B", "100 ms", "Throttle thermal system electric power consumption to <= 2.5 kW during low-battery limp-home mode.", "TmsPowerArbitrator_SWC", "50 ms"),
            ("Non-Volatile Thermal System Component Operating Hours Logger", "ASIL B", "5000 ms", "Log cumulative compressor runtime, pump cycles, and thermal duty cycles to flash memory.", "TmsDutyCycleLogger_SWC", "1000 ms")
        ],
        "FEAT-PWR-05": [
            ("AC Grid L1/L2/L3 Voltage & Phase Angle Phase-Locked Loop (PLL) Tracker", "ASIL C", "1 ms", "Synchronize on-board charger active power factor correction (PFC) bridge with grid AC line frequency (50/60 Hz).", "ObcPllTracker_SWC", "0.5 ms"),
            ("On-Board Charger Bidirectional PFC Bridge PWM Space Vector Modulator", "ASIL C", "1 ms", "Regulate AC mains current to achieve unity power factor (PF > 0.99) and THD < 3.0% at up to 22 kW AC charge.", "ObcPfcModulator_SWC", "0.5 ms"),
            ("Galvanic Isolated LLC Resonant DC-DC Converter Secondary Rectifier", "ASIL C", "1 ms", "Control high-frequency resonant LLC converter switching frequency (100-250 kHz) to step DC voltage to battery.", "ObcLlcConverter_SWC", "0.5 ms"),
            ("DC Fast Charging Combined Charging System (CCS2) ISO 15118 Protocol Handler", "ASIL C", "20 ms", "Execute HomePlug Green PHY high-level communication, session setup, and TLS certificate exchange.", "DcfcIso15118_SWC", "10 ms"),
            ("DIN 70121 & ISO 15118 DC Fast Charge Current Setpoint Negotiator", "ASIL C", "20 ms", "Transmit real-time battery maximum voltage and current limits to external DC charger every 50 ms.", "DcfcNegotiator_SWC", "10 ms"),
            ("Charging Inlet Mechanical Locking Pin Actuator & Microswitch Interlock", "ASIL C", "50 ms", "Drive solenoid lock pin to lock charging plug into vehicle inlet; confirm lock engagement before high-voltage flow.", "ObcInletLock_SWC", "20 ms"),
            ("Control Pilot (CP) PWM Duty Cycle Decoder & Proximity Pilot (PP) Sensor", "ASIL C", "10 ms", "Measure CP 1 kHz PWM duty cycle to decode grid EVSE current capacity (e.g. 16A, 32A) and detect cord uncoupling.", "ObcControlPilot_SWC", "5 ms"),
            ("DC Fast Charge Inlet Dual Thermocouple Over-Temperature Monitor", "ASIL C", "50 ms", "Monitor DC+ and DC- pin temperatures: Throttle charge current if pin temperature exceeds 90 °C; cut at 105 °C.", "DcfcPinThermal_SWC", "20 ms"),
            ("HV DC Fast Charge Pre-Charge Contactor Sequencing & Inrush Limiter", "ASIL D", "10 ms", "Close pre-charge circuit to match off-board charger DC voltage within +-10V of battery pack before main contactors.", "DcfcPreCharge_SWC", "5 ms"),
            ("AC/DC Residual Current Detection (RCD Type B) Earth Leakage Trip", "ASIL C", "5 ms", "Hardware leakage sensor trips charging contactors within <= 20 ms if DC leakage current > 6 mA or AC > 30 mA.", "ObcLeakageProtection_SWC", "1 ms"),
            ("Charging System Emergency Stop Remote E-Trip Signal Supervisor", "ASIL D", "10 ms", "De-energize main charging contactors in <= 10 ms upon emergency stop button push or EVSE disconnect.", "ObcEmergencyStop_SWC", "2 ms"),
            ("DEM Charging Session Diagnostic Event Manager & Error Logger", "ASIL B", "50 ms", "Log diagnostic fault codes for pilot anomalies, insulation breakdown, and communication timeouts.", "ObcDiagnosticManager_SWC", "20 ms"),
            ("Non-Volatile Charging Energy Metering & Battery Degradation Profiler", "ASIL B", "1000 ms", "Record revenue-grade energy ingestion (kWh) and charging history profiles in secure storage.", "ObcEnergyMeter_SWC", "500 ms")
        ],
        "FEAT-PWR-06": [
            ("V2L AC Islanding Grid Synthesizer & Autonomous Voltage Regulator", "ASIL C", "1 ms", "Synthesize stable 230V / 120V single-phase AC island grid (50/60 Hz +-0.1 Hz) supplying up to 3.6 kW off-grid load.", "V2lGridSynthesizer_SWC", "0.5 ms"),
            ("V2G Bi-Directional Grid-Tied Synchronization & Active Power Dispatcher", "ASIL C", "5 ms", "Synchronize inverter output with utility grid phase and dispatch active/reactive power (P/Q) per utility request.", "V2gPowerDispatcher_SWC", "2 ms"),
            ("V2L Inrush Current & Overload Electronic Circuit Breaker Safing", "ASIL C", "2 ms", "Trip electronic inverter output in <= 5 ms upon detecting load overcurrent exceeding 150% rating.", "V2lCircuitBreaker_SWC", "0.5 ms"),
            ("Anti-Islanding Utility Power Cut Detection & Immediate Disconnect", "ASIL C", "5 ms", "Detect utility grid blackout via active frequency drift: Disconnect from grid within <= 100 ms (IEEE 1547).", "V2gAntiIslanding_SWC", "2 ms"),
            ("V2L Discharge Lower Battery SOC Cutoff Threshold Governor", "ASIL B", "500 ms", "Halt V2L power export when vehicle battery state-of-charge drops below user-selected threshold (e.g. 20%).", "V2lSocGovernor_SWC", "100 ms"),
            ("Vehicle External Power Outlet Thermal & Weather Enclosure Interlock", "ASIL B", "100 ms", "Verify V2L external socket lid closure and internal socket temperature <= 65 °C prior to power delivery.", "V2lSocketInterlock_SWC", "50 ms"),
            ("V2G Smart Charging Schedule Optimization via ISO 15118-20 Dynamic Pricing", "ASIL B", "1000 ms", "Optimize vehicle discharge timing according to spot market electricity prices and user departure deadline.", "V2gPriceOptimizer_SWC", "500 ms"),
            ("Galvanic Output Neutral-Ground Bond Switch State Coordinator", "ASIL C", "20 ms", "Engage internal neutral-ground bonding relay in stand-alone V2L island mode; open bond in grid-tied V2G mode.", "V2lNeutralBond_SWC", "10 ms"),
            ("Inverter Power Semiconductor Symmetrical Thermal Derater", "ASIL B", "100 ms", "Derate continuous V2L export power if bidirectional converter junction temperature exceeds 110 °C.", "V2lThermalDerater_SWC", "50 ms"),
            ("High-Voltage Battery DC Injection Prevention Inverter Filter", "ASIL C", "10 ms", "Filter and monitor DC component of exported AC current: Trip if DC current injection exceeds 0.5% rating.", "V2gDcFilter_SWC", "2 ms"),
            ("V2L/V2G System Diagnostic Event Manager & Islanding Event Recorder", "ASIL B", "50 ms", "Log diagnostic fault codes and historical energy exported to household or grid in non-volatile flash.", "V2lDiagnosticManager_SWC", "20 ms"),
            ("Driver Cockpit & Smartphone App Bi-Directional Power Control Interface", "ASIL B", "100 ms", "Broadcast exported power (kW), remaining battery range, and export status to driver cockpit and mobile app.", "V2lHmiDispatcher_SWC", "50 ms"),
            ("Non-Volatile Utility Grid Compliance Certification Audit Logger", "ASIL B", "2000 ms", "Store IEEE 1547 and VDE-AR-N 4105 grid compliance audit records in tamper-proof non-volatile memory.", "V2gAuditLogger_SWC", "1000 ms")
        ],
        "FEAT-PWR-07": [
            ("Electric Axle Dog-Clutch Disconnect Solenoid Actuator Position Controller", "ASIL C", "10 ms", "Control hydraulic/electromechanical dog clutch actuator to connect/disconnect secondary axle in <= 150 ms.", "EaxleClutchController_SWC", "5 ms"),
            ("Secondary Motor Zero-Torque Speed Synchronization Prior to Engagement", "ASIL C", "10 ms", "Synchronize secondary traction motor speed to road speed within +-20 RPM before engaging mechanical clutch.", "EaxleSpeedSync_SWC", "5 ms"),
            ("2-Speed Planetary Gearbox Dual-Brake Shift Sequencing Engine", "ASIL C", "10 ms", "Coordinate friction clutch release and brake band apply to execute 1st to 2nd gear shift in <= 300 ms without torque hole.", "EaxleShiftSequencer_SWC", "5 ms"),
            ("Shift Drum Electromechanical Rotary Encoder Angle Closed-Loop Servo", "ASIL C", "5 ms", "Position shifting drum stepper motor with angular accuracy <= 0.5° across neutral, low, and high gear detents.", "EaxleDrumServo_SWC", "2 ms"),
            ("Mechanical Jam & Spline Tooth-on-Tooth Collision Re-Try Logic", "ASIL C", "20 ms", "Detect spline misalignment upon engagement; oscillate motor speed by +-50 RPM to facilitate smooth tooth engagement.", "EaxleToothAligner_SWC", "10 ms"),
            ("Axle Disconnect Drag Reduction Efficiency Maximizer", "ASIL B", "100 ms", "Automatically disconnect secondary front/rear e-axle during steady-state highway cruising to eliminate spin drag.", "EaxleEfficiencyManager_SWC", "50 ms"),
            ("Cold Temperature Gearbox Oil Viscosity Warming & Shift Inhibit Governor", "ASIL B", "500 ms", "Inhibit high-speed 2nd-gear shifting when gearbox transmission oil temperature < -10 °C until warmed up.", "EaxleColdShiftGovernor_SWC", "100 ms"),
            ("Emergency All-Wheel Drive Instantaneous Axle Re-Connect Dispatcher", "ASIL C", "10 ms", "Re-engage disconnected e-axle in <= 200 ms upon detecting wheel slip or ESC stability intervention trigger.", "EaxleFastReconnect_SWC", "5 ms"),
            ("Multi-Disk Clutches Wear Life & Friction Lining Degradation Observer", "ASIL B", "1000 ms", "Estimate cumulative clutch thermal slip energy dissipation to predict mechanical lining wear life.", "EaxleClutchWearObserver_SWC", "200 ms"),
            ("Dual Redundant Clutch Position Proximity Hall Sensor Plausibility Monitor", "ASIL C", "10 ms", "Cross-check dual Hall sensors on disconnect fork: Trip fault if position discrepancy > 1.5 mm.", "EaxlePositionCrossCheck_SWC", "2 ms"),
            ("DEM Transmission Shifting Fault Diagnostics & Limp-Gear Latching", "ASIL C", "50 ms", "Lock transmission in safe 1st gear and latch diagnostic fault code if shift actuator faults.", "EaxleDiagnosticManager_SWC", "20 ms"),
            ("Instrument Cluster e-Axle Active Drive Mode & Gear Display Serializer", "ASIL B", "50 ms", "Transmit active gear ratio (1st, 2nd, Disconnected) and AWD torque split percentage to cluster display.", "EaxleHmiDispatcher_SWC", "20 ms"),
            ("Non-Volatile Transmission Shift Counts & Actuator Cycles Audit Recorder", "ASIL B", "2000 ms", "Log total lifetime shift cycles and dog-clutch engagement counts in non-volatile flash memory.", "EaxleShiftLogger_SWC", "1000 ms")
        ]
    }
    return specs

print("Powertrain specification templates ready.")

# expand_bdy_features.py
import features_bdy_full

old_feats = {f["id"]: f for f in features_bdy_full.full_bdy_features}

# FEAT-BDY-01: PEPS (Expanded to 4 sys reqs, 8 sw reqs)
f1 = old_feats["FEAT-BDY-01"]
f1["sys_reqs"].extend([
    {
        "id": "SYS-BDY-01-03",
        "title": "IEEE 802.15.4z UWB Cryptographic Time-of-Flight Anti-Relay Bounding",
        "asil": "ASIL B / ISO 21434",
        "statement": "The System SHALL compute cryptographically authenticated Ultra-Wideband (UWB) Time-of-Flight distance (0 to 10 m with +-5 cm accuracy) using Scrambled Timestamp Sequence (STS) to prevent relay-station attacks.",
        "activation": "Active when smartphone or key fob enters BLE range (< 10 m).",
        "ftti": "50 ms",
        "safe_state": "Keep vehicle doors locked; prohibit engine/drive start.",
        "failure_reaction": "If UWB ranging timestamps show physical anomaly or phase variance, abort authentication.",
        "inputs": "UWB_STS_Encrypted_Frames, UWB_Transceiver_Antennas[5], BLE_RSSI_Dbm",
        "outputs": "Cryptographic_Distance_Meters, Relay_Attack_Detected_Flag, Key_Zone_Enum",
        "verification": "Car Connectivity Consortium (CCC) Digital Key Release 3 compliance and RF relay attack bench testing.",
        "downstream": ["SWR-BDY-01-05", "SWR-BDY-01-06"]
    },
    {
        "id": "SYS-BDY-01-04",
        "title": "Welcome Carpet Light Choreography & Walk-Away Auto-Lock",
        "asil": "QM",
        "statement": "The System SHALL orchestrate dynamic LED ground projection carpet lighting when key approaches within 3.0 m, and automatically lock all doors, close windows, fold mirrors, and arm alarm when key walks away (> 2.5 m for > 3.0s).",
        "activation": "Active in vehicle parked state.",
        "ftti": "200 ms",
        "safe_state": "Lock all doors; arm ultrasonic interior intrusion alarm.",
        "failure_reaction": "If key remains inside cabin, prohibit walk-away auto lock to prevent locking keys inside.",
        "inputs": "Key_Zone_Enum, Key_Distance_Meters, Door_Ajar_Status_Bits, Driver_Seat_Occupied",
        "outputs": "Door_Lock_Actuator_Cmd, Welcome_Carpet_LED_Duty, Security_Alarm_Armed_Flag",
        "verification": "Proximity perimeter approach and departure automation testing across 500 walk cycles.",
        "downstream": ["SWR-BDY-01-07", "SWR-BDY-01-08"]
    }
])
f1["sw_reqs"].extend([
    {
        "id": "SWR-BDY-01-05",
        "title": "IEEE 802.15.4z Scrambled Timestamp Sequence (STS) Ranging Engine",
        "parent": "SYS-BDY-01-03",
        "asil": "ASIL B",
        "swc": "PepsUwbRanging_SWC",
        "period": "20 ms",
        "wcet": "1.2 ms",
        "activation": "Active during digital key approach.",
        "algorithm": "Executes Two-Way Ranging (TWR) using AES-128 cryptographically randomized STS preamble symbols. Measures round-trip time: t_prop = 0.5 * (t_round - t_reply). Calculates physical distance d = c_light * t_prop. Rejects delayed packets.",
        "safety_mechanism": "Cryptographic nonce freshness verification to block replay attacks.",
        "failure_reaction": "Lock out digital key session for 30 seconds if MAC verification fails 3 times.",
        "inputs": "UWB_RoundTrip_Time_Picoseconds, AES_STS_Seed_Key, UWB_Antenna_Index",
        "outputs": "Physical_Distance_Cm, Ranging_Integrity_Confirmed_Flag",
        "verification": "RF chamber spoofing and intentional picosecond time-delay injection tests."
    },
    {
        "id": "SWR-BDY-01-06",
        "title": "Vehicle Perimeter 5-Antenna Zone Localization Triangulator",
        "parent": "SYS-BDY-01-03",
        "asil": "ASIL B",
        "swc": "PepsZoneTriangulator_SWC",
        "period": "20 ms",
        "wcet": "0.9 ms",
        "activation": "Active upon valid ranging.",
        "algorithm": "Multilaterates 3D key position using 5 UWB nodes (Front bumper, B-pillars left/right, Rear bumper, Cabin dome). Classifies zone: Interior Cabin (Driver/Passenger/Rear) vs Exterior Perimeter (Left, Right, Tailgate, Welcome Zone).",
        "safety_mechanism": "Boundary certainty check: Requires >= 15 cm margin between interior and exterior classification.",
        "failure_reaction": "Prohibit vehicle engine start if key position ambiguity > 20 cm.",
        "inputs": "UWB_Node_Distances[5], Vehicle_Coordinate_Origin_Offset",
        "outputs": "Key_3D_Coordinates_X_Y_Z, Precise_Zone_Enum",
        "verification": "Grid layout test around vehicle doors and windows measuring zone accuracy."
    },
    {
        "id": "SWR-BDY-01-07",
        "title": "Exterior LED Dynamic Welcome Carpet Lighting Choreographer",
        "parent": "SYS-BDY-01-04",
        "asil": "QM",
        "swc": "PepsWelcomeChoreographer_SWC",
        "period": "50 ms",
        "wcet": "0.5 ms",
        "activation": "Triggered when key enters 3.0 m welcome zone.",
        "algorithm": "Coordinates exterior lighting: Ramps mirror projector LEDs (0 to 100% PWM over 1.2s), illuminates flush door handle lights, and sweeps headlamp DRL light bars. Deploys flush motorized door handles.",
        "safety_mechanism": "Battery power guard: Inhibits welcome lighting if 12V battery voltage < 12.0V.",
        "failure_reaction": "Turn off welcome LEDs if key remains stationary in zone for > 60 seconds.",
        "inputs": "Precise_Zone_Enum, Ambient_Lux_Sensor, Battery_12V_Voltage",
        "outputs": "Mirror_Carpet_LED_PWM_Duty, Door_Handle_Deploy_Cmd, DRL_Welcome_Sweep_Trigger",
        "verification": "Optical illuminance and photometric fade timing test on ground surface."
    },
    {
        "id": "SWR-BDY-01-08",
        "title": "Walk-Away Distance Hysteresis & Automated Closure Sequencer",
        "parent": "SYS-BDY-01-04",
        "asil": "ASIL B",
        "swc": "PepsWalkAwayManager_SWC",
        "period": "100 ms",
        "wcet": "0.4 ms",
        "activation": "Active after all vehicle doors are closed.",
        "algorithm": "Tracks key departing vehicle: When distance d > 2.5 m continuously for > 3.0s and zero keys remain inside cabin, asserts Auto_Lock_Command: Fires door lock solenoids, rolls up open windows, retracts door handles, and sounds confirmation horn chirp.",
        "safety_mechanism": "Key lock-in prevention: If interior antenna detects key inside cabin, sounds double horn alert and keeps doors unlocked.",
        "failure_reaction": "Send smartphone push notification if window cannot close due to anti-pinch obstruction.",
        "inputs": "Key_3D_Coordinates_X_Y_Z, All_Doors_Closed_Microswitches, Window_Open_State_Bits",
        "outputs": "BCM_Master_Lock_Pulse_Cmd, Window_Global_Close_Cmd, Horn_Chirp_Req",
        "verification": "Field testing walking away with keys under varied environmental conditions."
    }
])

# FEAT-BDY-03: SRS Airbag (Expanded to 5 sys reqs, 11 sw reqs)
f3 = old_feats["FEAT-BDY-03"]
f3["sys_reqs"].extend([
    {
        "id": "SYS-BDY-03-03",
        "title": "Multi-Axis Front, Side & Rollover Crash Severity Classification",
        "asil": "ASIL D",
        "statement": "The System SHALL sample central and satellite accelerometers at 4 kHz, evaluating Velocity Drop (Delta_V), Crash Energy Integral, and Roll Angular Momentum in <= 8 ms to classify crash severity tier (No-Fire, Stage 1 Low-Speed, Stage 2 High-Speed, Rollover).",
        "activation": "Active at all times when ignition is ON.",
        "ftti": "8 ms",
        "safe_state": "Inhibit pyrotechnic squib firing in low-severity impacts to avoid unnecessary repair costs.",
        "failure_reaction": "If satellite crash sensor communication drops, rely on central ECU dual-core accelerometers.",
        "inputs": "Crash_Accel_X_Y_Z_Array[6], Angular_Rate_Roll_Pitch_Yaw, Satellite_Bus_Health",
        "outputs": "Crash_Severity_Level_Enum, Crash_Direction_Angle_Deg, Deployment_Fire_Permit_Flag",
        "verification": "Physical sled crash pulses (FMVSS 208, 214, 226) across rigid barrier and offset deformable barrier impacts.",
        "downstream": ["SWR-BDY-03-06", "SWR-BDY-03-07"]
    },
    {
        "id": "SYS-BDY-03-04",
        "title": "Dual-Stage Airbag Squib Firing Timing & Seatbelt Pretensioner Coordination",
        "asil": "ASIL D",
        "statement": "The System SHALL fire pyrotechnic seatbelt pretensioners in <= 12 ms, Stage 1 airbag squibs in <= 18 ms, and Stage 2 airbag squibs with variable delay (15 to 45 ms depending on crash severity and occupant position) to optimize occupant deceleration trajectory.",
        "activation": "Active upon Deployment_Fire_Permit_Flag.",
        "ftti": "2 ms for squib pulse generation.",
        "safe_state": "Open high-side and low-side firing transistors after 2.0 ms squib current pulse.",
        "failure_reaction": "If squib loop resistance is out of spec (< 1.5 ohm or > 5.5 ohm), log latched DTC B0001.",
        "inputs": "Crash_Severity_Level_Enum, Occupant_Weight_Class_Enum, Seat_Track_Position_Sensor",
        "outputs": "Squib_Fire_Command_Bitmask[16], Pretensioner_Fire_Bitmask[4]",
        "verification": "High-speed camera deployment test and squib current pulse profile measurement.",
        "downstream": ["SWR-BDY-03-08", "SWR-BDY-03-09"]
    },
    {
        "id": "SYS-BDY-03-05",
        "title": "Occupant Classification Child-Seat Suppression & HV Pyrofuse Cut-Off",
        "asil": "ASIL D",
        "statement": "The System SHALL automatically suppress passenger frontal airbag if passenger seat is occupied by child safety seat (< 15 kg according to FMVSS 208), and transmit dedicated hardware discrete crash pulse to blow high-voltage traction pyrofuse in <= 2 ms.",
        "activation": "Active in all vehicle states.",
        "ftti": "2 ms for HV pyrofuse pulse.",
        "safe_state": "De-energize 400V/800V traction battery; turn on hazard lights and unlock doors.",
        "failure_reaction": "Default passenger airbag to ENABLED if occupant classification sensor is defective.",
        "inputs": "Passenger_Seat_Bladder_Weight_Sensor_Kg, Child_Seat_ISOFIX_Switch, Crash_Deploy_Confirmed",
        "outputs": "Passenger_Airbag_Suppressed_TellTale, HV_Pyrofuse_Discrete_Trigger_Pin",
        "verification": "FMVSS 208 child dummy suppression tests and high-voltage pyrofuse explosive bench testing.",
        "downstream": ["SWR-BDY-03-10", "SWR-BDY-03-11"]
    }
])
f3["sw_reqs"].extend([
    {
        "id": "SWR-BDY-03-06",
        "title": "High-G Crash Acceleration Integral & Delta-V Core Algorithm",
        "parent": "SYS-BDY-03-03",
        "asil": "ASIL D",
        "swc": "SrsCrashClassifier_SWC",
        "period": "0.5 ms",
        "wcet": "0.12 ms",
        "activation": "Executed in 2 kHz high-priority hardware ISR.",
        "algorithm": "Computes velocity drop: Delta_V(t) = -integral(a_x * dt). Evaluates displacement s(t) = integral(Delta_V * dt). If Delta_V > 25 km/h within 30 ms AND Displacement s > 15 cm, asserts Fire_Decision_Frontal = TRUE.",
        "safety_mechanism": "Dual-core lockstep CPU verification: Requires identical deployment decision on lockstep Core B before firing.",
        "failure_reaction": "Inhibit firing if accelerometer self-test diagnostics fail.",
        "inputs": "Raw_Axial_Acceleration_X_Y_Z[4], Crash_Window_Timer_Ms",
        "outputs": "Computed_Delta_V_Kmph, Crash_Severity_Tier_Enum",
        "verification": "Playback of 250 real crash crash-test acceleration sensor records."
    },
    {
        "id": "SWR-BDY-03-07",
        "title": "Rollover Angular Rate & Tilting Kinetic Energy Observer",
        "parent": "SYS-BDY-03-03",
        "asil": "ASIL D",
        "swc": "SrsRolloverClassifier_SWC",
        "period": "2 ms",
        "wcet": "0.25 ms",
        "activation": "Continuous rollover monitoring task.",
        "algorithm": "Evaluates rollover phase plane: Roll_Rate p vs Roll_Angle Phi. If (Phi / Phi_crit)^2 + (p / p_crit)^2 > 1.0 (indicating vehicle is tripping over), commands curtain airbag deployment to prevent occupant ejection.",
        "safety_mechanism": "Slow rollover distinction: Deploys side curtain airbags earlier in sand ditch roll vs high-speed barrel roll.",
        "failure_reaction": "Inhibit rollover deployment if lateral acceleration < 0.2g (banking road).",
        "inputs": "Roll_Rate_RadS, Lateral_Accel_Y_G, Vehicle_Roll_Angle_Deg",
        "outputs": "Rollover_Deployment_Command (boolean), Curtain_Airbag_Deploy_Req",
        "verification": "FMVSS 226 ejection mitigation testing on rollover dynamic carousel."
    },
    {
        "id": "SWR-BDY-03-08",
        "title": "Dual-Stage Pyrotechnic Squib Delay Firing Sequencer",
        "parent": "SYS-BDY-03-04",
        "asil": "ASIL D",
        "swc": "SrsSquibSequencer_SWC",
        "period": "1 ms",
        "wcet": "0.15 ms",
        "activation": "Triggered on crash fire decision.",
        "algorithm": "Orders deployment sequence: t=0 ms: Seatbelt pretensioner squibs fired; t=5 ms: Frontal Stage 1 squibs fired (70% gas inflation); t=5ms + Delta_t: Stage 2 squib fired (100% inflation). Delay Delta_t dynamically adjusted between 15 ms and 40 ms based on occupant proximity.",
        "safety_mechanism": "High-side and low-side transistor interlock: Requires both independent drivers to close simultaneously to deliver 1.75A squib firing current.",
        "failure_reaction": "Limit squib firing pulse width to exactly 2.0 ms to avoid driver short-circuit burnout.",
        "inputs": "Crash_Severity_Tier_Enum, Seat_Track_Position_Cm, Occupant_Mass_Kg",
        "outputs": "HighSide_Driver_Gates[16], LowSide_Driver_Gates[16], Squib_Pulse_Duration_Ms",
        "verification": "Oscilloscope squib firing current profiling on resistive dummy loads."
    },
    {
        "id": "SWR-BDY-03-09",
        "title": "Pyrotechnic Squib Diagnostic Impedance Periodic Poller",
        "parent": "SYS-BDY-03-04",
        "asil": "ASIL D",
        "swc": "SrsSquibDiagnostics_SWC",
        "period": "500 ms",
        "wcet": "0.4 ms",
        "activation": "Periodic background diagnostic task.",
        "algorithm": "Injects low-current measurement pulse (2 mA for 50 us, well below 50 mA non-fire limit) across every squib loop. Samples ADC voltage to calculate loop resistance R_squib. Valid range: [1.8, 4.2] ohms.",
        "safety_mechanism": "Hardware current clamp: Hardware prevents diagnostic current from ever exceeding 10 mA.",
        "failure_reaction": "If loop resistance < 1.0 ohm (short) or > 6.0 ohm (open), set latched DTC B0001 and illuminate red airbag tell-tale.",
        "inputs": "Squib_Sense_ADC_Voltages[16], Diagnostic_Pulse_Permit_Flag",
        "outputs": "Measured_Squib_Resistance_Array[16], Squib_Loop_Fault_Mask",
        "verification": "Precision resistor decade box fault injection testing."
    },
    {
        "id": "SWR-BDY-03-10",
        "title": "FMVSS 208 Occupant Classification Bladder Weight Classifier",
        "parent": "SYS-BDY-03-05",
        "asil": "ASIL D",
        "swc": "SrsOccupantClassifier_SWC",
        "period": "100 ms",
        "wcet": "0.6 ms",
        "activation": "Active in vehicle running states.",
        "algorithm": "Samples passenger seat silicone fluid bladder pressure sensor: Filters vehicle road vibration. Classifies weight: Empty (< 3 kg), Child / Rear-Facing Child Seat (< 25 kg), Small Adult (25-50 kg), Large Adult (> 50 kg). Sets Passenger_Airbag_Suppress = TRUE if weight < 25 kg.",
        "safety_mechanism": "Hysteresis threshold: 2 kg hysteresis to prevent chattering between child seat and 5th percentile female.",
        "failure_reaction": "Illuminate 'Passenger Airbag OFF' light on overhead console if suppressed.",
        "inputs": "Seat_Bladder_Pressure_Mbar, Seatbelt_Tension_Sensor_N",
        "outputs": "Occupant_Weight_Class_Enum, Passenger_Airbag_Suppressed_Flag",
        "verification": "FMVSS 208 anthropomorphic test dummy (6-year-old child vs 5th percentile female) seating tests."
    },
    {
        "id": "SWR-BDY-03-11",
        "title": "High-Voltage Pyrofuse Firing Pulse Discrete Output Driver",
        "parent": "SYS-BDY-03-05",
        "asil": "ASIL D",
        "swc": "SrsPyrofuseDriver_SWC",
        "period": "1 ms",
        "wcet": "0.1 ms",
        "activation": "Executed immediately upon crash deployment decision.",
        "algorithm": "Asserts dedicated hardwired discrete pulse line routed directly to High-Voltage Battery Pyrofuse detonator: Delivers 2.5A pulse for 5.0 ms, mechanically shearing high-voltage copper busbar within 1.5 ms to isolate traction battery.",
        "safety_mechanism": "Hardware latch circuit: Maintains fired state until battery pack is physically serviced.",
        "failure_reaction": "Broadcast redundant CAN-FD crash frame to BMS and VCU controllers.",
        "inputs": "Crash_Confirmed_Deployment_Flag, Hardware_Igniter_Capacitor_Voltage",
        "outputs": "HV_Pyrofuse_Detonator_Gate_Cmd, Crash_Confirmation_CANFD_PDU",
        "verification": "High-voltage battery destructive mechanical busbar shear testing under 600A load."
    }
])

all_bdy = [f1, old_feats["FEAT-BDY-02"], f3, old_feats["FEAT-BDY-04"], old_feats["FEAT-BDY-05"], old_feats["FEAT-BDY-06"]]

print(f"Total Body features compiled: {len(all_bdy)}")
total_sys = sum(len(f['sys_reqs']) for f in all_bdy)
total_sw = sum(len(f['sw_reqs']) for f in all_bdy)
print(f"Total Body SysReqs: {total_sys}, Total Body SwReqs: {total_sw}")

code = "# Complete Body, Lighting & Restraints Domain Features (6 Features)\n\n"
code += "full_bdy_features = " + repr(all_bdy) + "\n"
code += 'print(f"Loaded all {len(full_bdy_features)} Body features successfully.")\n'

with open("features_bdy_full.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated features_bdy_full.py successfully!")

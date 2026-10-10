# -*- coding: utf-8 -*-
"""
Connectivity, Security & Diagnostics expansion specifications library (TEL-01 to TEL-03, SEC-01, DIA-01).
"""

def get_conn_expansion_specs():
    specs = {
        "FEAT-TEL-01": [
            ("UNECE R156 Software Update Management System (SUMS) Cryptographic Manifest Validator", "ASIL B", "500 ms", "Verify RSA-3072 / ECDSA digital signature and SHA-256 hash of inbound firmware update manifest.", "FotaManifestValidator_SWC", "200 ms"),
            ("A/B Dual-Bank Flash Memory Hardware Swap & Atomic Rollback Engine", "ASIL B", "200 ms", "Flash secondary memory bank in background; execute atomic bank switchover during vehicle sleep mode.", "FotaBankSwapEngine_SWC", "100 ms"),
            ("Cellular 5G / Wi-Fi Delta-Compression Firmware Package Downloader", "ASIL B", "1000 ms", "Download delta binary patches over HTTPS with resume-on-disconnect and cellular signal quality gating.", "FotaPackageDownloader_SWC", "500 ms"),
            ("Vehicle State-of-Charge & Parked Safety Precondition Evaluator", "ASIL B", "500 ms", "Confirm vehicle is parked in PARK, charging cable connected, and battery SOC > 50% prior to update.", "FotaPreconditionChecker_SWC", "200 ms"),
            ("Driver Consent & Scheduled Overnight Installation Calendar Manager", "ASIL A", "1000 ms", "Prompt driver for installation approval on central screen and schedule automated 3:00 AM execution.", "FotaConsentManager_SWC", "500 ms"),
            ("ECU Flash Programming Routine Control & UDS Diagnostics Orchestrator", "ASIL B", "100 ms", "Coordinate UDS Service $34 (RequestDownload), $36 (TransferData), and $37 (RequestTransferExit) across ECUs.", "FotaUdsOrchestrator_SWC", "50 ms"),
            ("Post-Flash Microcontroller Memory Integrity CRC-32 & Self-Test Verifier", "ASIL B", "500 ms", "Perform hardware memory CRC-32 verification across all flashed sectors prior to confirming success.", "FotaIntegrityVerifier_SWC", "200 ms"),
            ("Automated Rollback Trigger on ECU Boot-Failure or Watchdog Crash", "ASIL B", "100 ms", "Revert automatically to previous operational Bank A firmware if updated Bank B fails boot within 15s.", "FotaRollbackManager_SWC", "50 ms"),
            ("Cloud Telematics Server Installation Status & Campaign Completion Dispatcher", "ASIL B", "1000 ms", "Transmit encrypted completion telemetry report to OEM cloud backend server upon successful update.", "FotaTelemetryDispatcher_SWC", "500 ms"),
            ("DEM FOTA Diagnostic Trouble Code Qualification & Error History Logger", "ASIL B", "100 ms", "Log diagnostic fault codes for download corruption, signature failure, and flash write aborts.", "FotaDiagnosticManager_SWC", "50 ms")
        ],
        "FEAT-TEL-02": [
            ("Cellular V2X (C-V2X) PC5 Direct Sidelink 5.9 GHz RF Transceiver Interface", "ASIL B", "10 ms", "Interface with PC5 direct communication chipset to broadcast and receive safety messages at 5.9 GHz.", "V2xPc5Transceiver_SWC", "5 ms"),
            ("SAE J2735 / ETSI Basic Safety Message (BSM / CAM) Dynamic Encoder", "ASIL B", "20 ms", "Encode vehicle position, heading, velocity, acceleration, and brake status into BSM frames at 10 Hz.", "V2xBsmEncoder_SWC", "10 ms"),
            ("Intersection Collision Warning (ICW) Blind Crossing Path Evaluator", "ASIL B", "20 ms", "Compute collision risk with cross-traffic vehicles transmitting BSMs at non-line-of-sight intersections.", "V2xIcwEvaluator_SWC", "10 ms"),
            ("Emergency Electronic Brake Light (EEBL) Remote Vehicle Hard Braking Receiver", "ASIL B", "20 ms", "Receive EEBL alert from lead vehicle braking heavily beyond sightline (300 m ahead); notify driver.", "V2xEeblReceiver_SWC", "10 ms"),
            ("Emergency Vehicle Approaching (EVA) Siren & Trajectory Audible Clear Alert", "ASIL B", "50 ms", "Detect approaching ambulance or fire truck transmitting EVA packets; prompt driver to clear lane.", "V2xEvaNotifier_SWC", "20 ms"),
            ("Signal Phase and Timing (SPaT) Green Light Optimal Speed Advisory (GLOSA)", "ASIL A", "100 ms", "Calculate recommended cruising speed to pass upcoming traffic light on green based on SPaT timing.", "V2xGlosaAdvisor_SWC", "50 ms"),
            ("V2X Security Credential Management System (SCMS) Certificate Pseudonym Verifier", "ASIL B", "20 ms", "Verify IEEE 1609.2 digital signature of received V2X packets and rotate pseudonyms to ensure privacy.", "V2xSecurityVerifier_SWC", "10 ms"),
            ("V2X Message GPS Timestamp Plausibility & Replay Attack Defense Filter", "ASIL B", "10 ms", "Reject received V2X frames with GNSS timestamps deviating by > 100 ms from local synchronized time.", "V2xReplayDefense_SWC", "5 ms"),
            ("Instrument Cluster & Head-Up Display V2X Warning Visual Graphic Dispatcher", "ASIL B", "50 ms", "Display amber intersection hazard icons and emergency vehicle direction arrows on HUD and cluster.", "V2xHmiDispatcher_SWC", "20 ms"),
            ("DEM V2X RF Transceiver Diagnostics & Communication Loss Monitor", "ASIL B", "100 ms", "Monitor PC5 transceiver antenna VSWR and GPS lock; log DTC upon V2X communication system fault.", "V2xDiagnosticManager_SWC", "50 ms"),
            ("Non-Volatile V2X Safety Alerts & Hazardous Road Weather Incident Logger", "ASIL B", "1000 ms", "Record received road hazard warnings, bridge ice alerts, and collision near-miss events in NVM.", "V2xIncidentLogger_SWC", "500 ms"),
            ("Road Works Warning (RWW) Construction Lane Closure Decoupler", "ASIL B", "100 ms", "Parse RWW digital construction alerts to notify driver of lane closures 1.0 km ahead of work zones.", "V2xRwwParser_SWC", "50 ms"),
            ("V2X Congestion Control Sidelink Channel Busy Ratio (CBR) Power Manager", "ASIL B", "50 ms", "Scale transmit power and message rate (1 to 10 Hz) based on CBR to prevent RF channel saturation.", "V2xCbrPowerManager_SWC", "20 ms")
        ],
        "FEAT-TEL-03": [
            ("UNECE R144 Minimum Set of Data (MSD) Crash Telemetry Message Assembler", "ASIL B", "50 ms", "Assemble 140-byte MSD packet containing GPS coordinates, vehicle VIN, propulsion type, and direction.", "EcallMsdAssembler_SWC", "20 ms"),
            ("Automatic Crash Detection Airbag Deployment Pyrotechnic Trigger Interface", "ASIL B", "10 ms", "Trigger automated eCall sequence within <= 100 ms of receiving airbag pyrotechnic deployment signal.", "EcallAirbagTrigger_SWC", "5 ms"),
            ("Manual Emergency SOS Overhead Console Switch Debouncer & Confirm Interlock", "ASIL B", "50 ms", "Debounce overhead SOS button press (> 2.0s) to initiate emergency operator voice call without false alarms.", "EcallManualSwitch_SWC", "20 ms"),
            ("Cellular Modem Emergency Call (112 / 911 / ERA-GLONASS) Voice & In-Band Modem", "ASIL B", "100 ms", "Establish priority cellular voice call to Public Safety Answering Point (PSAP) with in-band modem data.", "EcallModemDriver_SWC", "50 ms"),
            ("Dual GNSS / GPS / GLONASS Multi-Constellation Emergency Location Engine", "ASIL B", "50 ms", "Acquire accurate vehicle crash coordinates (+-5.0 m) even in poor satellite coverage conditions.", "EcallGnssLocator_SWC", "20 ms"),
            ("Crash-Proof Back-Up Lithium Battery Pack (6.0V / 1200 mAh) Power Monitor", "ASIL B", "100 ms", "Monitor dedicated eCall internal backup battery: Ensure 20 minutes of talk time after 12V battery cut.", "EcallBackupBattery_SWC", "50 ms"),
            ("Crash-Resistant Internal Emergency Loudspeaker & Microphone Audio Driver", "ASIL B", "50 ms", "Route PSAP emergency operator audio through dedicated crash-resistant cabin microphone and speaker.", "EcallAudioDriver_SWC", "20 ms"),
            ("Emergency eCall Cellular Call Priority Pre-Emption & Automatic Re-Dialer", "ASIL B", "500 ms", "Drop non-emergency data sessions and re-dial PSAP up to 3 times if emergency cellular call is dropped.", "EcallReDialer_SWC", "200 ms"),
            ("Acoustic Call Progress & Visual Red/Green LED Overhead Console Indicator", "ASIL A", "100 ms", "Drive overhead red/green status LEDs and play acoustic prompts ('Emergency Call Connected') to occupants.", "EcallHmiIndicator_SWC", "50 ms"),
            ("DEM eCall Component Health Diagnostics & Periodic Self-Test Manager", "ASIL B", "100 ms", "Perform monthly automated self-test of backup battery, antenna continuity, and modem hardware.", "EcallDiagnosticManager_SWC", "50 ms"),
            ("Non-Volatile Emergency Dispatch Record & PSAP Acknowledgment Buffer", "ASIL B", "1000 ms", "Store cryptographically signed MSD transmission record and PSAP confirmation token in flash memory.", "EcallRecordBuffer_SWC", "500 ms"),
            ("Rollover Sensor Secondary Severe Incident Trigger Interlock", "ASIL B", "50 ms", "Initiate automatic eCall if vehicle rollover angle exceeds 90 degrees even if airbags did not deploy.", "EcallRolloverTrigger_SWC", "20 ms"),
            ("eCall SIM Card / eSIM Profile Health & Network Registration Supervisor", "ASIL B", "500 ms", "Verify eSIM emergency profile registration on any available cellular carrier network (national roaming).", "EcallEsimSupervisor_SWC", "200 ms")
        ],
        "FEAT-SEC-01": [
            ("AUTOSAR Secure On-Board Communication (SecOC) AES-128 CMAC Verifier", "ASIL B", "5 ms", "Verify 64-bit truncated AES-128 CMAC on critical chassis and powertrain CAN-FD frames in <= 2.0 ms.", "SecOcCmacVerifier_SWC", "1 ms"),
            ("SecOC Freshness Value Manager (FVM) Synchronization & Trip Counter Engine", "ASIL B", "5 ms", "Manage synchronized monotonic trip counter and reset counters to eliminate message replay attacks.", "SecOcFvmManager_SWC", "1 ms"),
            ("Central Security Gateway CAN-FD / Ethernet Stateful Packet Firewall", "ASIL B", "2 ms", "Filter network traffic across domain buses: Drop unauthorized CAN IDs and illegal payload formats in < 1 ms.", "SecGatewayFirewall_SWC", "0.5 ms"),
            ("Hardware Security Module (HSM) Cryptographic Key Storage & Secure Boot Interlock", "ASIL B", "10 ms", "Secure cryptographic root keys in tamper-proof HSM silicon; execute secure boot chain of trust.", "SecHsmKeyManager_SWC", "5 ms"),
            ("Controller Area Network Intrusion Detection System (CAN-IDS) Rate Anomaly Detector", "ASIL B", "5 ms", "Detect bus flooding attacks, frame frequency anomalies, and spoofed diagnostic requests on CAN buses.", "SecCanIdsDetector_SWC", "2 ms"),
            ("Automotive Ethernet IEEE 802.1Q MACsec Hardware Encryption Layer", "ASIL B", "2 ms", "Encrypt inter-domain Ethernet communications at wire speed (100/1000BASE-T1) using MACsec GCM-AES.", "SecEthernetMacsec_SWC", "0.5 ms"),
            ("Diagnostic Service UDS $27 SecurityAccess 256-Bit Challenge-Response Engine", "ASIL B", "50 ms", "Generate cryptographic pseudo-random seed and authenticate workshop tool response before unlock.", "SecUdsSecurityAccess_SWC", "20 ms"),
            ("Security Gateway Cyber Incident Logging & Intrusion Detection Dispatcher (IDS-M)", "ASIL B", "100 ms", "Aggregate security events from ECUs and transmit standardized IDS-M security reports to backend SIEM.", "SecIdsmDispatcher_SWC", "50 ms"),
            ("Automotive Denial-of-Service (DoS) Bus-Off Prevention & Babbling Idiot Clamp", "ASIL B", "5 ms", "Isolate babbling idiot transceivers within <= 5 ms by opening transceiver bus disconnect switches.", "SecBabblingClamp_SWC", "1 ms"),
            ("Diagnostic Port (OBD-II) Hardware Physical Access Firewalled Gateway Gatekeeper", "ASIL B", "20 ms", "Lock down OBD-II diagnostic port from accessing internal vehicle control networks while moving.", "SecObdGatekeeper_SWC", "10 ms"),
            ("DEM Cybersecurity Event Diagnostic Event Manager & Security Quorum Buffer", "ASIL B", "50 ms", "Log security violation trouble codes and trigger protective limp-home mode upon severe bus attack.", "SecDiagnosticManager_SWC", "20 ms")
        ],
        "FEAT-DIA-01": [
            ("ISO 14229 Unified Diagnostic Services (UDS) Multi-Client Protocol Server", "ASIL B", "10 ms", "Execute UDS services ($10 DiagnosticSessionControl, $22 ReadDataByIdentifier, $2E WriteDataById).", "UdsProtocolServer_SWC", "5 ms"),
            ("Diagnostic Trouble Code (DTC) 3-Byte Standard Fault Status Byte State Machine", "ASIL B", "10 ms", "Manage 8-bit status byte (TestFailed, ConfirmedDTC, PendingDTC) per ISO 14229 Service $19.", "DemStatusByte_SWC", "5 ms"),
            ("Fault Debounce Pre-Failed / Pre-Passed Counter-Based & Time-Based Filter", "ASIL B", "10 ms", "Debounce fault signals (counter threshold 10, pre-failed step +2, pre-passed step -1) to prevent false trips.", "DemDebounceFilter_SWC", "5 ms"),
            ("Diagnostic Freeze-Frame Snapshot Buffer Non-Volatile Memory Serializer", "ASIL B", "50 ms", "Capture and commit 64-byte freeze frame (speed, voltage, temperature, time) to EEPROM upon fault confirmation.", "DemFreezeFrame_SWC", "20 ms"),
            ("OBD-II California Air Resources Board (CARB) Readiness Monitor Evaluator", "ASIL B", "100 ms", "Track completion of regulatory OBD-II drive cycle readiness monitors across catalytic, EVAP, and misfire.", "ObdReadiness_SWC", "50 ms"),
            ("Diagnostic Session Control ($10) Default, Programming, and Extended Mode Guard", "ASIL B", "20 ms", "Transition between diagnostic sessions with automatic S3 timeout (5000 ms) return to default session.", "UdsSessionGuard_SWC", "10 ms"),
            ("Routine Control Service ($31) Actuator HIL Routine Self-Test Executive", "ASIL B", "50 ms", "Execute commanded component routines (e.g. purge valve pulse, pump prime) with safety interlock checks.", "UdsRoutineControl_SWC", "20 ms"),
            ("Clear Diagnostic Information Service ($14) Non-Volatile Flash Sector Eraser", "ASIL B", "100 ms", "Erase confirmed fault codes and freeze-frame buffers from flash upon authorized service command.", "UdsClearFaults_SWC", "50 ms"),
            ("Input/Output Control by Identifier Service ($2F) Actuator Override Supervisor", "ASIL B", "20 ms", "Allow diagnostic technician to temporarily override fan speed, window motor, or headlamp states safely.", "UdsIoControl_SWC", "10 ms"),
            ("Malfunction Indicator Lamp (MIL) Instrument Cluster Tell-Tale Illuminator", "ASIL B", "100 ms", "Command steady or flashing amber MIL lamp on cluster when emissions-related fault confirmed.", "DemMilDispatcher_SWC", "50 ms"),
            ("On-Board Diagnostic Tester Physical CAN-FD 500 kbps / 2 Mbps Transceiver Driver", "ASIL B", "10 ms", "Manage physical OBD-II DLC connector communication with auto baud-rate detection and ISO-TP transport.", "UdsIsoTpDriver_SWC", "5 ms")
        ]
    }
    return specs

print("Connectivity, Security & Diagnostics expansion specifications library defined.")

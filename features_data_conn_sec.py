# Connectivity, V2X, Cybersecurity & Diagnostics Features (Features 23 to 26)

conn_sec_features = [
    {
        "id": "FEAT-TEL-01",
        "name": "Firmware Over-The-Air (FOTA) Update Orchestrator",
        "slug": "FOTA",
        "domain": "Connectivity, Security & Diagnostics",
        "asil": "ASIL B / ISO 21434 / UNECE R156",
        "summary": "Downloads, cryptographically verifies, stages, and flashes firmware updates across vehicle ECUs with A/B dual-bank memory rollback protection.",
        "activation_logic": {
            "preconditions": "Vehicle parked in PARK, battery SOC > 50%, 12V auxiliary battery > 12.4V, vehicle speed == 0 km/h, cellular connection stable.",
            "entry_conditions": "Cloud manifest downloaded and verified; user confirms 'Update Now' or scheduled overnight install window opens.",
            "states": ["IDLE_CHECKING", "DOWNLOADING_CHUNKS", "CRYPTO_VERIFICATION", "USER_CONSENT_PENDING", "PRECONDITION_GATEWAY", "FLASHING_BANK_B", "POST_INSTALL_VERIFICATION", "ROLLBACK_EXECUTION"],
            "deactivation_conditions": "Update sequence successfully completed, or pre-condition violation forces abort prior to flashing.",
            "override_behavior": "Driver opening door or turning ignition on during installation is prohibited by software lock until critical flashing phase completes."
        },
        "safety_concept": {
            "safety_goal": "SG-FOTA-01: Prevent execution of corrupted or malicious firmware; prevent bricking ECUs; prevent vehicle immobilization.",
            "ftti": "N/A (Quiescent safe state)",
            "safe_state": "Autonomous hardware watchdog rollback to intact Bank A flash memory if new Bank B fails post-install boot self-test.",
            "warning_escalation": "Display install countdown on central screen; warning 'Do Not Drive - Update in Progress (Est: 20 min)'."
        },
        "failure_behaviors": {
            "power_loss_during_flashing": "Target ECUs utilize A/B dual-bank flash; power interruption leaves original Bank A untouched, allowing instant reboot.",
            "signature_verification_failure": "If binary SHA-256 hash or RSA-4096 signature check fails, delete staged chunks immediately and report security audit alert."
        },
        "sys_reqs": [
            {
                "id": "SYS-TEL-01-01",
                "title": "Cryptographic Package Signature & Integrity Verification",
                "asil": "ISO 21434 / ASIL B",
                "statement": "The System SHALL verify digital signatures of received update manifests and firmware binaries using RSA-4096 / ECDSA-P384 and SHA-256 with Hardware Security Module (HSM) root-of-trust prior to staging.",
                "activation": "Active upon completion of download package assembly.",
                "ftti": "N/A",
                "safe_state": "Purge staged flash memory; report failed authentication to cloud backend.",
                "failure_reaction": "If root certificate chain is invalid, terminate session and quarantine package.",
                "inputs": "5G_Modem_Package_Stream, HSM_Root_Public_Key, Manifest_XML_Signature",
                "outputs": "Package_Integrity_Confirmed (boolean), Decrypted_Binary_Stream",
                "verification": "Penetration testing with tampered bytes and forged digital certificates.",
                "downstream": ["SWR-TEL-01-01", "SWR-TEL-01-02"]
            },
            {
                "id": "SYS-TEL-01-02",
                "title": "Vehicle Pre-Condition Safety Interlocks Verification",
                "asil": "ASIL B",
                "statement": "The System SHALL prohibit flash execution unless: Vehicle in PARK, Vehicle Speed == 0 km/h, 12V Battery >= 12.4V, High-Voltage SOC >= 50%, Hazard Lights functional, and driver consent confirmed.",
                "activation": "Active immediately prior to initiating flashing sequence.",
                "ftti": "100 ms",
                "safe_state": "Abort update; keep vehicle in drivable state.",
                "failure_reaction": "If 12V battery drops below 12.0V during staging, abort update and engage 12V DC-DC charger.",
                "inputs": "Gear_Position_PRND, Vehicle_Speed_Mps, Battery_12V_Voltage, Battery_HV_SOC",
                "outputs": "Preconditions_Satisfied (boolean), Blocked_Precondition_Code",
                "verification": "Boundary test suite across gear selections, vehicle speeds, and battery voltages.",
                "downstream": ["SWR-TEL-01-03", "SWR-TEL-01-04"]
            },
            {
                "id": "SYS-TEL-01-03",
                "title": "A/B Dual-Bank Flash Orchestration & Self-Test Rollback",
                "asil": "ASIL B",
                "statement": "The System SHALL write new software into secondary flash bank (Bank B). If target ECU fails startup self-tests within 60 seconds post-boot, the system SHALL autonomously revert boot flags to Bank A in <= 5 seconds.",
                "activation": "Active during flashing and reboot verification.",
                "ftti": "5000 ms",
                "safe_state": "Revert to known good Bank A firmware; restore full vehicle drivability.",
                "failure_reaction": "If Bank B crashes micro, hardware watchdog toggles boot pin to Bank A.",
                "inputs": "Post_Boot_Health_PDU, Target_ECU_UDS_Diagnostic_Status, Boot_Timer_Sec",
                "outputs": "Active_Bank_Select_Register, Flash_Rollback_Audit_Code",
                "verification": "Power cut and intentional corrupt binary injection during flash updates.",
                "downstream": ["SWR-TEL-01-05", "SWR-TEL-01-06"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-TEL-01-01",
                "title": "Manifest XML Parser & Cryptographic Signature Verifier",
                "parent": "SYS-TEL-01-01",
                "asil": "QM / ISO 21434",
                "swc": "FotaManifestVerifier_SWC",
                "period": "Background event",
                "wcet": "12.0 ms",
                "activation": "Executed on download completion.",
                "algorithm": "Parses manifest containing ECU compatibility matrix, target software version, dependencies, and SHA-256 chunk hashes. Invokes HSM to verify ECDSA-P384 signature over entire manifest.",
                "safety_mechanism": "Strict dependency enforcement: Rejects firmware if dependent ECU versions mismatch.",
                "failure_reaction": "Delete all downloaded files upon signature validation failure.",
                "inputs": "Downloaded_Manifest_File, HSM_Root_Certificate",
                "outputs": "Manifest_Valid (boolean), Target_ECU_Install_List",
                "verification": "Unit test against valid and corrupted XML manifests."
            },
            {
                "id": "SWR-TEL-01-02",
                "title": "Hardware Security Module (HSM) AES-256-GCM Chunk Decryptor",
                "parent": "SYS-TEL-01-01",
                "asil": "QM / ISO 21434",
                "swc": "FotaDecryptor_SWC",
                "period": "Background event",
                "wcet": "15.0 ms",
                "activation": "Executed during binary staging.",
                "algorithm": "Decrypts 64 KB binary chunks using AES-256-GCM authenticated cipher. Validates 128-bit authentication tag for each chunk. Verifies progressive Merkle hash tree.",
                "safety_mechanism": "Zero plain-text persistence on external unencrypted flash memory.",
                "failure_reaction": "Abort staging if any chunk authentication tag fails to match.",
                "inputs": "Encrypted_Chunk_Buffer, Decryption_Session_Key",
                "outputs": "Decrypted_Chunk_Buffer, Chunk_Hash_Verified (boolean)",
                "verification": "NIST cryptographic test vector suite verification."
            },
            {
                "id": "SWR-TEL-01-03",
                "title": "Vehicle Safety Interlocks Pre-Condition Gatekeeper",
                "parent": "SYS-TEL-01-02",
                "asil": "ASIL B",
                "swc": "FotaSafetyInterlock_SWC",
                "period": "100 ms",
                "wcet": "0.6 ms",
                "activation": "Executed prior to flashing.",
                "algorithm": "Polls: (Gear == PARK) && (Speed == 0.0) && (V_12V >= 12.4) && (SOC >= 50.0) && (Vehicle_Locked == TRUE). If any condition transitions to FALSE during 30s confirmation window, abort install.",
                "safety_mechanism": "Continuous monitoring: Keeps polling interlocks during initial flash handshake.",
                "failure_reaction": "Set Install_Blocked_Reason code and notify driver via cluster.",
                "inputs": "Gear_State, Vehicle_Speed_Mps, V_12V, SOC_Pct, Lock_State",
                "outputs": "Install_Safe_Permit (boolean)",
                "verification": "Automated boundary testing of all vehicle interlock signals."
            },
            {
                "id": "SWR-TEL-01-04",
                "title": "Cluster HMI Consent & Installation Countdown Timer",
                "parent": "SYS-TEL-01-02",
                "asil": "QM",
                "swc": "FotaHmiConsent_SWC",
                "period": "100 ms",
                "wcet": "0.5 ms",
                "activation": "Executed upon manifest verification.",
                "algorithm": "Presents installation dialogue to driver: 'Update Ready. Estimated Time: 25 min. Vehicle cannot be driven.' Requires explicit PIN or button press consent; starts 120s countdown.",
                "safety_mechanism": "Allows driver to cancel update prior to countdown expiration.",
                "failure_reaction": "Postpone update if driver does not provide affirmative consent.",
                "inputs": "User_Touch_Input, Countdown_Timer_Sec",
                "outputs": "Driver_Consent_Confirmed (boolean), Scheduled_Install_Timestamp",
                "verification": "HMI user interaction simulation testing."
            },
            {
                "id": "SWR-TEL-01-05",
                "title": "UDS Diagnostic Service 0x34/0x36/0x37 Flashing Orchestrator",
                "parent": "SYS-TEL-01-03",
                "asil": "ASIL B",
                "swc": "FotaUdsFlashing_SWC",
                "period": "20 ms",
                "wcet": "3.2 ms",
                "activation": "Executed during active flashing phase.",
                "algorithm": "Executes standard diagnostic sequence: 0x10 0x02 (ProgrammingSession) -> 0x27 (SecurityAccess) -> 0x34 (RequestDownload) -> 0x36 (TransferData chunks to Bank B) -> 0x37 (RequestTransferExit) -> 0x31 (CheckMemoryRoutine).",
                "safety_mechanism": "CRC-32 verification performed on target ECU before exit programming session.",
                "failure_reaction": "If any UDS service returns Negative Response Code (NRC), halt and initiate rollback.",
                "inputs": "Target_ECU_Address, Decrypted_Binary_Stream",
                "outputs": "UDS_Diagnostic_Tx_PDU, Flashing_Progress_Pct",
                "verification": "CANoe.DiVa automated flash programming test suite."
            },
            {
                "id": "SWR-TEL-01-06",
                "title": "Dual-Bank Bootloader Pointer Switcher & Watchdog Recovery",
                "parent": "SYS-TEL-01-03",
                "asil": "ASIL B",
                "swc": "FotaBootSupervisor_SWC",
                "period": "50 ms",
                "wcet": "0.8 ms",
                "activation": "Executed post-flash completion.",
                "algorithm": "Flips non-volatile boot configuration register to point to Bank B. Commands target ECU reset (0x11 0x01). Starts 60.0-second confirmation timer: ECU must report healthy UDS diagnostic session. If timer expires, flips boot pointer back to Bank A.",
                "safety_mechanism": "Hardware watchdog fallback: Unrefreshed hardware watchdog forces boot back to Bank A.",
                "failure_reaction": "Revert to Bank A and log failure diagnostic report to cloud backend.",
                "inputs": "Target_ECU_Boot_Report_PDU, Post_Boot_Timer_Sec",
                "outputs": "Active_Boot_Bank_Select_Bit, Rollback_Executed_Flag",
                "verification": "Corrupted Bank B binary injection verifying automated rollback to Bank A."
            }
        ]
    },
    {
        "id": "FEAT-TEL-02",
        "name": "Cellular Vehicle-to-Everything Safety Warnings (C-V2X)",
        "slug": "V2X",
        "domain": "Connectivity, Security & Diagnostics",
        "asil": "ASIL B",
        "summary": "Transmits and receives 5.9 GHz PC5 direct sidelink V2X messages (BSM / CAM / DENM) to warn driver of non-line-of-sight collisions, emergency vehicles, and road hazards.",
        "activation_logic": {
            "preconditions": "12V system active, V2X transceiver RF frontend healthy, GNSS time synchronization achieved (< 1 us).",
            "entry_conditions": "Vehicle powered up; C-V2X PC5 direct mode enabled.",
            "states": ["SEARCHING_TIME_SYNC", "BEACONING_BSM", "HAZARD_LISTENING", "EMERGENCY_VEHICLE_ALERT", "COLLISION_WARNING_EEBL", "FAILSAFE_SILENT"],
            "deactivation_conditions": "Vehicle powered down or GNSS time synchronization lost for > 60 seconds.",
            "override_behavior": "Driver can dismiss visual V2X information popups; safety critical warnings cannot be muted."
        },
        "safety_concept": {
            "safety_goal": "SG-V2X-01: Provide timely warnings for non-line-of-sight collisions (blind intersections, curve hazards); prevent false warnings caused by spoofed V2X packets.",
            "ftti": "100 ms",
            "safe_state": "Silence unverified V2X warnings; revert to on-board radar/camera detection only.",
            "warning_escalation": "Visual overlay on Cluster and Head-Up Display; audible alert tone (1.0 kHz)."
        },
        "failure_behaviors": {
            "certificate_revoked": "If received V2X message is signed by a certificate on the Certificate Revocation List (CRL), discard packet instantly.",
            "gnss_sync_lost": "If GNSS satellite time lost, free-run internal oscillator for up to 60s before transitioning to passive listening."
        },
        "sys_reqs": [
            {
                "id": "SYS-TEL-02-01",
                "title": "5.9 GHz PC5 Direct Sidelink BSM Broadcast & Reception",
                "asil": "ASIL B",
                "statement": "The System SHALL broadcast Basic Safety Messages (BSM / CAM) containing vehicle position, speed, heading, and curvature at 10 Hz (100 ms), and process inbound peer messages within <= 20 ms.",
                "activation": "Active while vehicle is moving.",
                "ftti": "100 ms",
                "safe_state": "Halt transmission if positioning accuracy degrades > 5.0 m.",
                "failure_reaction": "If RF power amplifier overheats, reduce transmit power from 23 dBm to 10 dBm.",
                "inputs": "GNSS_Position_Time, Ego_Kinematics, 5.9GHz_PC5_Antenna_Array",
                "outputs": "Outbound_BSM_Packets, Inbound_V2X_Target_List",
                "verification": "SDR (Software Defined Radio) RF testing adhering to 3GPP Rel-14/15 standards.",
                "downstream": ["SWR-TEL-02-01", "SWR-TEL-02-02"]
            },
            {
                "id": "SYS-TEL-02-02",
                "title": "Non-Line-of-Sight Hazard Evaluation & Driver Alerting",
                "asil": "ASIL B",
                "statement": "The System SHALL evaluate inbound V2X messages to detect Emergency Electronic Brake Lights (EEBL), Blind Intersection Collision Warning (ICW), and Approaching Emergency Vehicle (EVW) up to 300 m away, issuing alerts <= 50 ms post-reception.",
                "activation": "Active when valid peer messages are received.",
                "ftti": "50 ms",
                "safe_state": "Do not alert driver if packet cryptographic certificate cannot be validated.",
                "failure_reaction": "If peer packet timestamp is skewed > 500 ms from local time, drop packet as replay.",
                "inputs": "Inbound_V2X_Target_List, Ego_Vehicle_Route, V2X_Security_Trust_Store",
                "outputs": "V2X_Alert_HUD_Icon, V2X_Warning_Audio_Cmd",
                "verification": "Test track intersection collision warning demonstration with obstruction walls.",
                "downstream": ["SWR-TEL-02-03", "SWR-TEL-02-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-TEL-02-01",
                "title": "SAE J2735 / ETSI ITS Basic Safety Message Formatter",
                "parent": "SYS-TEL-02-01",
                "asil": "ASIL B",
                "swc": "V2xMessageStack_SWC",
                "period": "100 ms",
                "wcet": "2.4 ms",
                "activation": "Executed cyclically every 100 ms.",
                "algorithm": "Encodes BSM Part I UPER ASN.1 buffer: [msgCount, id, secMark, lat, long, elev, accuracy, speed, heading, angle, accelSet, brakes, size]. Transmits over PC5 interface via Linux socket API.",
                "safety_mechanism": "MAC address pseudonym rotation every 5 minutes to prevent vehicle tracking.",
                "failure_reaction": "If GNSS position uncertainty > 5.0 m, flag position as DEGRADED in message header.",
                "inputs": "GNSS_Latitude, GNSS_Longitude, Ego_Speed_Mps, Ego_Heading_Deg",
                "outputs": "Encoded_BSM_Buffer[256]",
                "verification": "ASN.1 syntax conformance testing against SAE J2735 standard."
            },
            {
                "id": "SWR-TEL-02-02",
                "title": "IEEE 1609.2 / ETSI TS 103 097 Elliptic Curve Security Verifier",
                "parent": "SYS-TEL-02-01",
                "asil": "ASIL B / ISO 21434",
                "swc": "V2xSecurityVerifier_SWC",
                "period": "Event-driven",
                "wcet": "6.5 ms (HSM accelerated)",
                "activation": "Executed on every incoming V2X packet.",
                "algorithm": "Verifies ECDSA NIST-P256 signature using public key extracted from certificate. Checks certificate validity period, geographical scope, and verifies against local Certificate Revocation List (CRL).",
                "safety_mechanism": "Replay window check: Discard packet if timestamp difference abs(t_rx - t_tx) > 200 ms.",
                "failure_reaction": "Silently drop unauthenticated or invalid packets; increment security audit counter.",
                "inputs": "Inbound_V2X_Signed_Packet, Local_CRL_Database",
                "outputs": "Packet_Authenticated_Flag (boolean), Verified_Payload_Buffer",
                "verification": "Cryptographic fuzzing test with invalid, expired, and revoked certificates."
            },
            {
                "id": "SWR-TEL-02-03",
                "title": "Intersection Collision Threat & Blind Spot Geometry Resolver",
                "parent": "SYS-TEL-02-02",
                "asil": "ASIL B",
                "swc": "V2xThreatResolver_SWC",
                "period": "20 ms",
                "wcet": "1.8 ms",
                "activation": "Executed every 20 ms on verified peer targets.",
                "algorithm": "Projects trajectory intersection point: Evaluates time-to-intersection (TTI) for cross-traffic approaching at 90 degrees. If delta_TTI < 1.5s and line-of-sight is obstructed by buildings, triggers Blind Intersection Alert.",
                "safety_mechanism": "Ego path cross-check: Confirms ego vehicle is actively on path intersecting peer.",
                "failure_reaction": "Suppress alert if peer vehicle indicates it has already come to complete stop.",
                "inputs": "Peer_Position, Peer_Velocity, Peer_Heading, Ego_Pose, Ego_Speed",
                "outputs": "Intersection_Collision_Threat (boolean), Threat_TTI_Sec",
                "verification": "SIL scenario testing of blind-corner cross-traffic encounters."
            },
            {
                "id": "SWR-TEL-02-04",
                "title": "Emergency Vehicle & Electronic Brake Light (EEBL) HMI Dispatcher",
                "parent": "SYS-TEL-02-02",
                "asil": "QM",
                "swc": "V2xHmiDispatcher_SWC",
                "period": "50 ms",
                "wcet": "0.6 ms",
                "activation": "Executed upon threat detection.",
                "algorithm": "If Peer_Brake_Status indicates hard deceleration (> 4.0 m/s²) 2 to 5 cars ahead: Displays EEBL warning icon. If Emergency Vehicle approaching with siren active: Displays direction arrow (Behind / Left / Right).",
                "safety_mechanism": "Alert priority coordinator: ADAS immediate radar/camera alerts take precedence over V2X warnings.",
                "failure_reaction": "Clear alert if peer stops transmitting for > 1.0 second.",
                "inputs": "Intersection_Collision_Threat, Peer_Special_Vehicle_Code",
                "outputs": "HUD_V2X_Alert_PDU, Instrument_Cluster_V2X_PopUp",
                "verification": "Cockpit HMI visual integration and priority arbitration testing."
            }
        ]
    },
    {
        "id": "FEAT-SEC-01",
        "name": "Central Security Gateway & SecOC Intrusion Detection",
        "slug": "SecOC",
        "domain": "Connectivity, Security & Diagnostics",
        "asil": "ASIL B / ISO 21434",
        "summary": "Authenticates critical in-vehicle bus communication using AES-128-CMAC and monotonic freshness values, filtering unauthorized packets and detecting Denial-of-Service attacks.",
        "activation_logic": {
            "preconditions": "Hardware Security Module (HSM) secure boot verified, cryptographic session keys loaded into hardware keystore.",
            "entry_conditions": "Central Gateway powered up and forwarding in-vehicle bus traffic.",
            "states": ["SECURE_FORWARDING", "SYNC_FRESHNESS_EXCHANGE", "ANOMALY_LOGGING", "PORT_RATE_LIMITING", "INTRUSION_CONTAINMENT", "SECURITY_LOCKOUT"],
            "deactivation_conditions": "Gateway power down.",
            "override_behavior": "UDS Diagnostic Security Access (Service 0x27) temporarily unlocks engineering routing tables upon valid cryptographic key handshake."
        },
        "safety_concept": {
            "safety_goal": "SG-SEC-01: Prevent unauthorized command injection, replay attacks, or bus-flooding denial of service on safety-critical chassis and powertrain networks.",
            "ftti": "10 ms",
            "safe_state": "Drop unauthenticated frames immediately; isolate compromised network segments.",
            "warning_escalation": "Log RFC 5424 security event record into tamper-resistant security log; notify fleet SOC via telematics."
        },
        "failure_behaviors": {
            "mac_verification_failure": "If received MAC does not match computed MAC, drop frame instantly in <= 1.0 ms and increment ECU security anomaly counter.",
            "freshness_counter_desync": "If freshness counter drifts outside acceptance window, initiate authenticated sync frame exchange."
        },
        "sys_reqs": [
            {
                "id": "SYS-SEC-01-01",
                "title": "AUTOSAR SecOC Cryptographic Message Authentication & Freshness Counter",
                "asil": "ASIL B / ISO 21434",
                "statement": "The System SHALL compute and verify a 64-bit truncated AES-128-CMAC and monotonic Freshness Value on all safety-critical CAN-FD and SOME/IP messages with <= 1.0 ms processing latency per message.",
                "activation": "Active at all times on safety-critical network interfaces.",
                "ftti": "5 ms",
                "safe_state": "Discard unauthenticated PDU; do not pass to application SWCs.",
                "failure_reaction": "If 5 consecutive verification failures occur from an ECU, flag ECU as compromised.",
                "inputs": "Raw_CANFD_Frame_Payload, Hardware_Keystore, Local_Freshness_Value_Manager",
                "outputs": "SecOC_Verified_PDU, Verification_Result_Status (PASS/FAIL)",
                "verification": "CAN bus fuzzing, payload tampering, and replay injection test suite.",
                "downstream": ["SWR-SEC-01-01", "SWR-SEC-01-02"]
            },
            {
                "id": "SYS-SEC-01-02",
                "title": "Central Gateway Firewall Whitelist Filtering & DoS Rate Limiting",
                "asil": "QM / ISO 21434",
                "statement": "The Central Gateway SHALL filter Ethernet SOME/IP and CAN-FD routing tables against a static whitelist, dropping unauthorized message IDs and rate-limiting broadcast packets exceeding 1000 msg/s.",
                "activation": "Active across all gateway routing channels.",
                "ftti": "10 ms",
                "safe_state": "Halt routing on flooded port; preserve bandwidth on remaining critical ports.",
                "failure_reaction": "If port flood exceeds 5000 msg/s, isolate physical Ethernet switch port.",
                "inputs": "Inbound_Packet_Headers, Static_Routing_Whitelist_Table, Port_Traffic_Counters",
                "outputs": "Forwarded_Network_Packets, Dropped_Frame_Counter, IDS_Security_Alert_Log",
                "verification": "Line-rate network traffic flood injection testing on Automotive Ethernet switch.",
                "downstream": ["SWR-SEC-01-03", "SWR-SEC-01-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-SEC-01-01",
                "title": "Hardware-Accelerated AES-128-CMAC Computation Engine",
                "parent": "SYS-SEC-01-01",
                "asil": "ASIL B",
                "swc": "SecocVerification_SWC",
                "period": "Interrupt-driven (<= 1 ms)",
                "wcet": "0.35 ms (hardware crypto)",
                "activation": "Executed on RX message interrupt.",
                "algorithm": "Appends local freshness counter to received payload: M = Payload || Freshness. Computes MAC = AES-128-CMAC(K_session, M). Truncates to 64 bits. Compares with received MAC. If identical, marks PDU authenticated.",
                "safety_mechanism": "Constant-time memory comparison to prevent cryptographic timing side-channel attacks.",
                "failure_reaction": "Drop packet and increment Security_Violation_Counter if MACs differ.",
                "inputs": "RX_Payload_Buffer, RX_MAC_Buffer, Freshness_Value_64Bit",
                "outputs": "Authenticated_PDU_Buffer, SecOC_Result_Enum",
                "verification": "NIST SP 800-38B CMAC test vectors and timing jitter analysis."
            },
            {
                "id": "SWR-SEC-01-02",
                "title": "Synchronized Monotonic Freshness Value Manager (FVM)",
                "parent": "SYS-SEC-01-01",
                "asil": "ASIL B",
                "swc": "FvmCoordinator_SWC",
                "period": "10 ms",
                "wcet": "0.4 ms",
                "activation": "Executed cyclically every 10 ms.",
                "algorithm": "Maintains Trip Counter (16-bit), Reset Counter (16-bit), and Message Counter (32-bit). Broadcasts authenticated FVM Sync message every 500 ms. Verifies message freshness is strictly monotonic.",
                "safety_mechanism": "Non-volatile persistence of Trip Counter prevents counter replay across power cycles.",
                "failure_reaction": "If message counter rolls over, increment Reset Counter and re-authenticate.",
                "inputs": "Local_Timestamp, FVM_Sync_PDU, Persistent_Trip_Counter",
                "outputs": "Full_Freshness_Value_64Bit (uint64)",
                "verification": "Counter overflow and out-of-order packet sequence testing."
            },
            {
                "id": "SWR-SEC-01-03",
                "title": "Automotive Ethernet Switch Firewall Whitelist Filter",
                "parent": "SYS-SEC-01-02",
                "asil": "QM / ISO 21434",
                "swc": "GatewayFirewall_SWC",
                "period": "Interrupt-driven",
                "wcet": "0.2 ms",
                "activation": "Executed on inbound Ethernet switch frames.",
                "algorithm": "Inspects Ethernet header: Checks Source MAC, Target IP, Layer 4 Port, and SOME/IP Service ID against static whitelist matrix. If tuple does not exist in whitelist, packet is dropped.",
                "safety_mechanism": "Default-Deny policy: Any unconfigured service or port is blocked by default.",
                "failure_reaction": "Log unauthorized packet header details to security audit circular buffer.",
                "inputs": "Ethernet_Frame_Header_Bytes, Routing_Whitelist_Table",
                "outputs": "Forward_Permitted (boolean)",
                "verification": "Automated penetration testing with unauthorized port scanners."
            },
            {
                "id": "SWR-SEC-01-04",
                "title": "Intrusion Detection System (IDS) Traffic Anomaly & DoS Monitor",
                "parent": "SYS-SEC-01-02",
                "asil": "QM / ISO 21434",
                "swc": "IdsSecurityMonitor_SWC",
                "period": "10 ms",
                "wcet": "0.7 ms",
                "activation": "Executed every 10 ms.",
                "algorithm": "Tracks packet arrival rates per ID: Delta_t = t_now - t_last. If Delta_t < minimum inter-arrival time (e.g. 5 ms for a 20 ms cyclic frame), or total port rate > 1000 msg/s, flags DoS attack and throttles port.",
                "safety_mechanism": "Token-bucket rate limiter permits short micro-bursts but clamps sustained floods.",
                "failure_reaction": "Serialize RFC 5424 syslog audit event and trigger cellular telematics alert.",
                "inputs": "Port_Frame_Counters, Message_Arrival_Timestamps",
                "outputs": "Port_Rate_Limit_Enforce (boolean), Security_Event_Record",
                "verification": "Network flood injection testing up to 100 Mbps line saturation."
            }
        ]
    },
    {
        "id": "FEAT-DIA-01",
        "name": "Unified Diagnostic Services & OBD-II Fault Management (UDS)",
        "slug": "UDS",
        "domain": "Connectivity, Security & Diagnostics",
        "asil": "ASIL B / QM",
        "summary": "Implements ISO 14229-1 UDS diagnostic server, Diagnostic over IP (DoIP ISO 13400), Diagnostic Trouble Code (DTC) debouncing, freeze frame serialization, and OBD-II compliance.",
        "activation_logic": {
            "preconditions": "12V system active, diagnostic stack initialized.",
            "entry_conditions": "Diagnostic tester connects via OBD port (CAN-FD) or Ethernet RJ45 (DoIP), sending valid UDS request.",
            "states": ["DEFAULT_SESSION", "PROGRAMMING_SESSION", "EXTENDED_DIAGNOSTIC_SESSION", "SECURITY_UNLOCKED", "DTC_QUALIFYING", "FREEZE_FRAME_WRITING"],
            "deactivation_conditions": "Tester disconnects, S3 timeout (5000 ms) expires, or ignition powered down.",
            "override_behavior": "Diagnostic Routine Control (Service 0x31) can command component test overrides only when vehicle speed == 0 km/h."
        },
        "safety_concept": {
            "safety_goal": "SG-DIA-01: Accurately record safety-critical system faults; prevent unauthorized diagnostic routine execution while driving.",
            "ftti": "N/A",
            "safe_state": "Reject actuator override requests (NRC 0x22: ConditionsNotCorrect) if vehicle is in motion.",
            "warning_escalation": "Illumination of Malfunction Indicator Lamp (MIL) for emissions or safety-related DTCs."
        },
        "failure_behaviors": {
            "nvm_write_failure": "If EEPROM/Flash write fails, cache freeze frame record in RAM circular buffer and retry at next cycle.",
            "tester_timeout": "If S3_server timer expires without tester ping, automatically revert to Default Session."
        },
        "sys_reqs": [
            {
                "id": "SYS-DIA-01-01",
                "title": "ISO 14229-1 UDS Diagnostic Services & DoIP Session Server",
                "asil": "QM",
                "statement": "The System SHALL support UDS services: 0x10, 0x11, 0x14, 0x19, 0x22, 0x2E, 0x27, 0x28, 0x2F, 0x31 over DoIP (ISO 13400) and CAN-FD, conforming to response time P2_server <= 50 ms and P2*_server <= 5000 ms.",
                "activation": "Active upon receipt of diagnostic request.",
                "ftti": "N/A",
                "safe_state": "Return Negative Response Code (NRC 0x10 / 0x22 / 0x33).",
                "failure_reaction": "If requested service is disallowed in current session, return NRC 0x7F (ServiceNotSupportedInActiveSession).",
                "inputs": "Diagnostic_Request_PDU (DoIP / CAN-FD), Vehicle_Speed_Mps, Engine_RPM",
                "outputs": "Diagnostic_Response_PDU, Active_Session_Enum, Security_Level_Enum",
                "verification": "Vector CANoe.DiVa automated protocol conformance test suite.",
                "downstream": ["SWR-DIA-01-01", "SWR-DIA-01-02"]
            },
            {
                "id": "SYS-DIA-01-02",
                "title": "DTC Fault Qualification, Freeze Frame Persistence & MIL Management",
                "asil": "ASIL B",
                "statement": "The System SHALL qualify faults as confirmed when persistent for >= 500 ms, record associated freeze frame environment variables into non-volatile memory, and illuminate the Malfunction Indicator Lamp (MIL) within <= 1.0 second.",
                "activation": "Active at all times during vehicle operation.",
                "ftti": "500 ms",
                "safe_state": "Persist fault record into redundant EEPROM sector.",
                "failure_reaction": "If EEPROM sector fails, write to secondary non-volatile flash partition.",
                "inputs": "SWC_Fault_Reports, Odometer_Km, Vehicle_Speed, Battery_Voltage, Timestamp",
                "outputs": "DTC_Status_Byte (ISO 14229-1), Freeze_Frame_Record_Bytes, MIL_Lamp_Command",
                "verification": "Fault injection testing across all calibrated DTC fault monitors.",
                "downstream": ["SWR-DIA-01-03", "SWR-DIA-01-04"]
            }
        ],
        "sw_reqs": [
            {
                "id": "SWR-DIA-01-01",
                "title": "AUTOSAR Dcm Diagnostic Communication Manager Protocol Parser",
                "parent": "SYS-DIA-01-01",
                "asil": "QM",
                "swc": "DcmProtocol_SWC",
                "period": "10 ms",
                "wcet": "1.4 ms",
                "activation": "Executed cyclically every 10 ms.",
                "algorithm": "Parses diagnostic request buffer: Validates SID, sub-function, and data identifier (DID). Enforces security levels (0x27 Seed & Key). Manages P2 and S3 timers. Formats positive responses or NRCs.",
                "safety_mechanism": "Speed gating: Actuator control (0x2F) and routines (0x31) rejected with NRC 0x22 if vehicle speed > 0 km/h.",
                "failure_reaction": "Transmit NRC 0x78 (ResponsePending) if internal routine requires > 50 ms.",
                "inputs": "Dcm_Rx_Buffer, Vehicle_Speed_Mps, Security_Unlocked_Flag",
                "outputs": "Dcm_Tx_Buffer, Active_Session_Code",
                "verification": "DiVa test suite achieving 100% service code coverage."
            },
            {
                "id": "SWR-DIA-01-02",
                "title": "ISO 13400-2 DoIP (Diagnostic over IP) TCP/UDP Server",
                "parent": "SYS-DIA-01-01",
                "asil": "QM",
                "swc": "DoIpServer_SWC",
                "period": "10 ms",
                "wcet": "1.8 ms",
                "activation": "Executed on Ethernet diagnostic port connections.",
                "algorithm": "Handles DoIP Vehicle Announcement (UDP 13400), Routing Activation (TCP 13400), and Diagnostic Message Routing. Verifies OEM Activation Code before opening TCP socket routing.",
                "safety_mechanism": "TCP connection limit: Closes secondary connection attempts to prevent denial of service.",
                "failure_reaction": "Close TCP socket if no traffic received within 5 minutes.",
                "inputs": "DoIP_Ethernet_Socket_Data, Ethernet_Link_Status",
                "outputs": "DoIP_Diagnostic_Payload_Buffer, DoIP_Routing_Active (boolean)",
                "verification": "DoIP client connection compliance and stress test."
            },
            {
                "id": "SWR-DIA-01-03",
                "title": "AUTOSAR Dem Counter-Based Fault Debouncing State Machine",
                "parent": "SYS-DIA-01-02",
                "asil": "ASIL B",
                "swc": "DemDebounce_SWC",
                "period": "10 ms",
                "wcet": "0.7 ms",
                "activation": "Executed every 10 ms.",
                "algorithm": "Maintains fault counter: Increments by +2 on PREFAILED; decrements by -1 on PREPASSED. When counter reaches +100 (500 ms persistence), sets DTC Status Byte bit 0 (testFailed) and bit 3 (confirmedDTC).",
                "safety_mechanism": "Debounce counter bounds clamped to [-128, +127] to prevent integer overflow.",
                "failure_reaction": "If fault clears for 40 driving cycles, clear confirmedDTC bit.",
                "inputs": "Monitor_Status_Report_Enum, Debounce_Step_Size",
                "outputs": "DTC_Status_Byte (uint8), Event_Qualified_Trigger (boolean)",
                "verification": "State machine transition test verifying exact debounce timing."
            },
            {
                "id": "SWR-DIA-01-04",
                "title": "Freeze Frame Environmental Snapshot Serialization & NVM Commit",
                "parent": "SYS-DIA-01-02",
                "asil": "ASIL B",
                "swc": "DemSnapshotWriter_SWC",
                "period": "Event-driven",
                "wcet": "2.2 ms",
                "activation": "Executed upon Event_Qualified_Trigger.",
                "algorithm": "Captures snapshot parameters: [DTC_ID, Odometer, Timestamp, Vehicle_Speed, Pack_Voltage, Inverter_Torque, Coolant_Temp]. Serializes into standardized record format and calls NvM_WriteBlock to store in redundant EEPROM.",
                "safety_mechanism": "CRC-16 checksum appended to snapshot record to verify data integrity upon subsequent readout.",
                "failure_reaction": "Log NVM storage failure event if write operation times out.",
                "inputs": "Event_Qualified_Trigger, Vehicle_Operating_Parameters",
                "outputs": "NvM_Write_Payload_Buffer, NvM_Write_Request_Flag",
                "verification": "Power cut during NVM write operation evaluating snapshot record recovery."
            }
        ]
    }
]

print(f"Loaded all {len(conn_sec_features)} Connectivity & Security features successfully.")

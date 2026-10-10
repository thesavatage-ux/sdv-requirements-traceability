# expand_conn_features.py
import features_conn_full

old_feats = {f["id"]: f for f in features_conn_full.full_conn_features}

# FEAT-TEL-01: FOTA (Expanded to 5 sys reqs, 10 sw reqs)
f1 = old_feats["FEAT-TEL-01"]
f1["sys_reqs"].extend([
    {
        "id": "SYS-TEL-01-04",
        "title": "Cellular 5G Differential Delta Binary Compression & Chunk Stager",
        "asil": "ASIL B / UNECE R156",
        "statement": "The System SHALL download compressed differential delta patches (reducing payload size by >= 75% compared to full binary images) over 5G/4G, reconstructing target flash binary in external non-volatile eMMC staging memory with SHA-256 chunk verification.",
        "activation": "Active upon cloud campaign notification.",
        "ftti": "N/A (Quiescent download)",
        "safe_state": "Purge corrupted chunks; resume download from last valid byte offset.",
        "failure_reaction": "If cellular signal drops below -115 dBm RSRP, pause download and resume when signal recovers.",
        "inputs": "5G_Modem_Chunk_Stream, Base_Firmware_Hash_ROM, Staged_Patch_Metadata",
        "outputs": "Reconstructed_Target_Binary, Chunk_Download_Progress_Pct, Download_Complete_Flag",
        "verification": "Delta patch reconstruction accuracy and bit-for-bit binary comparison test.",
        "downstream": ["SWR-TEL-01-07", "SWR-TEL-01-08"]
    },
    {
        "id": "SYS-TEL-01-05",
        "title": "Fleet Campaign Management, User Scheduling & Rollback Logger",
        "asil": "ISO 24089 / UNECE R156",
        "statement": "The System SHALL interface with OEM cloud campaign servers to report install progress, allow driver to schedule overnight installation windows (e.g. 02:00 AM), and securely record diagnostic rollback events into non-volatile audit log upon installation failure.",
        "activation": "Active during vehicle connected states.",
        "ftti": "N/A",
        "safe_state": "Keep current operational firmware intact; notify backend of campaign pause.",
        "failure_reaction": "If user initiates vehicle drive during scheduled window, postpone update automatically.",
        "inputs": "Cloud_Campaign_Schedule_Request, User_Consent_Selection, Rollback_Diagnostic_Codes",
        "outputs": "Campaign_Status_Telemetry_PDU, Central_Display_Schedule_UI_State",
        "verification": "End-to-end cloud-to-vehicle fleet deployment and rollback telemetry validation.",
        "downstream": ["SWR-TEL-01-09", "SWR-TEL-01-10"]
    }
])
f1["sw_reqs"].extend([
    {
        "id": "SWR-TEL-01-07",
        "title": "Bsdiff Differential Delta Binary Decompression Engine",
        "parent": "SYS-TEL-01-04",
        "asil": "ASIL B",
        "swc": "FotaDeltaReconstructor_SWC",
        "period": "50 ms",
        "wcet": "4.5 ms",
        "activation": "Executed during binary staging phase.",
        "algorithm": "Applies bsdiff/bspatch differential decompression algorithm: Reads existing flash Bank A binary and differential delta patch stream. Synthesizes new Bank B image. Computes SHA-256 hash across reconstructed 128 MB image: Confirms match with signed manifest.",
        "safety_mechanism": "Cryptographic memory guard: Reconstructed image stored in write-protected eMMC partition.",
        "failure_reaction": "Delete staged file and request re-download if reconstructed hash does not match.",
        "inputs": "Delta_Patch_Byte_Stream, Origin_Firmware_BankA_Bytes",
        "outputs": "Reconstructed_BankB_Firmware_Bytes, Hash_Verification_Passed_Flag",
        "verification": "Automated regression testing across 100 firmware delta patch versions."
    },
    {
        "id": "SWR-TEL-01-08",
        "title": "Non-Volatile Chunk Staging & Resume Checkpoint Manager",
        "parent": "SYS-TEL-01-04",
        "asil": "ASIL B",
        "swc": "FotaChunkCheckpoint_SWC",
        "period": "100 ms",
        "wcet": "1.2 ms",
        "activation": "Active during cellular download.",
        "algorithm": "Manages 4 MB chunk staging: Writes each downloaded chunk to eMMC storage and updates persistent bitmap index. If cellular connection is interrupted or ignition turns off, resumes exactly from missing chunk upon next wake-up.",
        "safety_mechanism": "Flash wear leveling: Restricts staging writes to dedicated update partition.",
        "failure_reaction": "Retry download of corrupted chunk up to 5 times before failing campaign.",
        "inputs": "Chunk_Sequence_Index, Chunk_Payload_Buffer[4096], Cellular_Link_Active_Flag",
        "outputs": "Chunk_Bitmap_Status_Array[32], Download_Resumed_Offset_Bytes",
        "verification": "Power cut-off and cell tower handoff interruption resilience testing."
    },
    {
        "id": "SWR-TEL-01-09",
        "title": "Vehicle Overnight Update Scheduler & Driver HMI Consent Flow",
        "parent": "SYS-TEL-01-05",
        "asil": "QM",
        "swc": "FotaScheduler_SWC",
        "period": "1000 ms",
        "wcet": "0.5 ms",
        "activation": "Cyclic 1 Hz task.",
        "algorithm": "Manages user interaction: Prompts driver on central screen 'Software Update Ready (Est. 25 min) - Install Now or Schedule Tonight at 02:00?'. If scheduled, wakes vehicle telematics via RTC alarm at 01:50 AM to verify pre-conditions and commence flashing.",
        "safety_mechanism": "Hazard warning check: Prohibits automatic update if vehicle hazard lights are blinking.",
        "failure_reaction": "Cancel overnight update if battery drops below 50% SOC prior to install window.",
        "inputs": "User_Schedule_Selection_Enum, Vehicle_RTC_Clock, Traction_Battery_SOC",
        "outputs": "RTC_Alarm_Wakeup_Register, Scheduled_Update_Pending_Flag",
        "verification": "HMI user workflow testing and RTC overnight wakeup verification."
    },
    {
        "id": "SWR-TEL-01-10",
        "title": "UNECE R156 Software Identification (RXSWIN) & Audit Logger",
        "parent": "SYS-TEL-01-05",
        "asil": "ISO 24089 / UNECE R156",
        "swc": "FotaAuditLogger_SWC",
        "period": "100 ms",
        "wcet": "0.8 ms",
        "activation": "Executed upon installation completion or failure.",
        "algorithm": "Generates regulatory Regulation X Software Identification Number (RXSWIN conforming to UNECE R156): Signs updated vehicle ECU software bill-of-materials with HSM private key. Appends cryptographic audit entry to tamper-proof internal blackbox.",
        "safety_mechanism": "Non-volatile append-only flash logging preventing erasure of software history.",
        "failure_reaction": "Transmit audit log immediately to OEM cloud backend upon next cellular connection.",
        "inputs": "Updated_ECU_Versions_Array[16], HSM_Private_Key_Handle, Install_Result_Code",
        "outputs": "Certified_Vehicle_RXSWIN_String, Cloud_Campaign_Report_Payload",
        "verification": "Type-approval compliance inspection according to UNECE R156."
    }
])

# FEAT-SEC-01: SecOC (Expanded to 4 sys reqs, 8 sw reqs)
f_sec = old_feats["FEAT-SEC-01"]
f_sec["sys_reqs"].extend([
    {
        "id": "SYS-SEC-01-03",
        "title": "Hardware Security Module (HSM) Isolated Key Store & Secure Boot",
        "asil": "ASIL D / ISO 21434",
        "statement": "The System SHALL implement an isolated on-chip Hardware Security Module (HSM with dedicated crypto core, RAM, and ROM) storing symmetric AES-128 keys and private ECC keys, executing authenticated Secure Boot in <= 35 ms from reset to prevent untrusted firmware execution.",
        "activation": "Continuous hardware root-of-trust from power-on reset.",
        "ftti": "10 ms",
        "safe_state": "Lock microcontroller in bootloader quarantine mode; assert external reset pin.",
        "failure_reaction": "If Secure Boot cryptographic signature check fails, halt execution and illuminate security indicator.",
        "inputs": "Reset_Vector_Trigger, HSM_Secure_ROM_Keys, Application_Flash_Signature",
        "outputs": "Secure_Boot_Success_Flag (boolean), HSM_Isolated_Key_Handles",
        "verification": "Hardware side-channel analysis (DPA) and fault-injection glitched clock attack testing.",
        "downstream": ["SWR-SEC-01-05", "SWR-SEC-01-06"]
    },
    {
        "id": "SYS-SEC-01-04",
        "title": "Vehicle Network Intrusion Detection System (IDS) & Anomaly Firewall",
        "asil": "ISO 21434 / UNECE R155",
        "statement": "The System SHALL monitor CAN-FD, LIN, and Automotive Ethernet traffic at line rate, detecting bus flooding (> 85% bus load), unexpected CAN ID spoofing, diagnostic service brute-force attempts, and unauthorized cyclic frame jitter, logging security events in <= 5 ms.",
        "activation": "Active at all times on all external gateways.",
        "ftti": "20 ms",
        "safe_state": "Quarantine offending network segment; filter malicious frames at hardware gateway.",
        "failure_reaction": "Block corrupted CAN ID messages while keeping safety-critical chassis communication open.",
        "inputs": "Gateway_Ethernet_Packets, CANFD_Raw_Frames, Bus_Load_Counter_Array[8]",
        "outputs": "IDS_Security_Alert_PDU, Firewall_Drop_Packet_Command, Intrusion_Severity_Enum",
        "verification": "Automotive penetration testing (CAN bus fuzzing, spoofing, denial-of-service attack suite).",
        "downstream": ["SWR-SEC-01-07", "SWR-SEC-01-08"]
    }
])
f_sec["sw_reqs"].extend([
    {
        "id": "SWR-SEC-01-05",
        "title": "HSM Dedicated Crypto Accelerator AES-CMAC & ECDSA Engine",
        "parent": "SYS-SEC-01-03",
        "asil": "ASIL D",
        "swc": "SecOcHsmDriver_SWC",
        "period": "1 ms",
        "wcet": "0.15 ms",
        "activation": "Executed in crypto coprocessor ISR.",
        "algorithm": "Directs hardware cryptographic engine to compute AES-128 CMAC and verify ECDSA-P256 digital signatures without exposing raw key bytes to main CPU cores. Completes AES-CMAC operation in <= 15 microseconds.",
        "safety_mechanism": "Memory isolation: HSM internal SRAM is physically invisible to primary CPU bus.",
        "failure_reaction": "Lock HSM crypto engine and trigger hardware tamper alarm upon unauthorized read.",
        "inputs": "HSM_Key_Handle, Raw_PDU_Payload_Buffer, Crypto_Operation_Type",
        "outputs": "Computed_MAC_Tag[8], Signature_Verification_Result (boolean)",
        "verification": "FIPS 140-3 Level 3 cryptographic algorithm validation suite."
    },
    {
        "id": "SWR-SEC-01-06",
        "title": "Authenticated Secure Boot RSA-4096 / ECDSA Chain-of-Trust Verifier",
        "parent": "SYS-SEC-01-03",
        "asil": "ASIL D",
        "swc": "SecOcSecureBoot_SWC",
        "period": "1 ms",
        "wcet": "12.5 ms",
        "activation": "Executed at microcontroller boot phase.",
        "algorithm": "Executes staged verification: 1) HSM ROM verifies Bootloader public key; 2) Bootloader verifies Application OS hash using SHA-256 and RSA-4096 signature; 3) Only jumps to application reset handler if signature is 100% mathematically valid.",
        "safety_mechanism": "Anti-rollback counter: Rejects firmware with version number lower than OTP fuse register.",
        "failure_reaction": "Trap CPU in infinite debug loop if firmware authentication fails.",
        "inputs": "Application_Flash_Image, Public_Key_Certificate_Chain, AntiRollback_OTP_Fuse",
        "outputs": "Boot_Permit_Signal, Secure_Boot_Integrity_Status",
        "verification": "Malicious tampered firmware injection test validating boot refusal."
    },
    {
        "id": "SWR-SEC-01-07",
        "title": "CAN-FD Line-Rate Bus Flooding & ID Whitelist Hardware Filter",
        "parent": "SYS-SEC-01-04",
        "asil": "ISO 21434 / UNECE R155",
        "swc": "SecOcFirewallFilter_SWC",
        "period": "1 ms",
        "wcet": "0.2 ms",
        "activation": "Hardware gateway packet ingress interrupt.",
        "algorithm": "Inspects incoming CAN-FD frames against strict hardware whitelist: Verifies CAN ID, DLC length, and payload format. Drops unauthorized CAN IDs. Computes instantaneous bus load: If bus load > 85% for > 50 ms, throttles offending source node.",
        "safety_mechanism": "Bypass protection: Safety-critical brake and steering CAN IDs (0x100 - 0x1FF) cannot be blocked.",
        "failure_reaction": "Isolate compromised OBD-II diagnostic port from internal powertrain bus.",
        "inputs": "Ingress_CAN_ID, Ingress_DLC, Gateway_Port_Index",
        "outputs": "Packet_Forward_Permit (boolean), Filtered_Drop_Counter",
        "verification": "CAN bus fuzz testing injecting 100,000 invalid frames per second."
    },
    {
        "id": "SWR-SEC-01-08",
        "title": "Vehicle Intrusion Detection System (IDS) Security Event Reporter",
        "parent": "SYS-SEC-01-04",
        "asil": "ISO 21434 / UNECE R155",
        "swc": "SecOcIdsReporter_SWC",
        "period": "100 ms",
        "wcet": "0.8 ms",
        "activation": "Cyclic 100 ms task.",
        "algorithm": "Aggregates security events from all network gateways: Formats standard Security Event Frame (SEF according to AUTOSAR IDS). Rates severity (Low: message jitter, High: invalid SecOC MAC, Critical: OBD diagnostic brute force). Dispatches event to onboard Security Event Memory and cloud VSOC.",
        "safety_mechanism": "Rate limiter on reporting: Prevents IDS reporter itself from overwhelming vehicle network during attack.",
        "failure_reaction": "Store security events in non-volatile flash if cloud connection is offline.",
        "inputs": "Security_Event_Raw_Queue[32], Cloud_VSOC_Connection_Status",
        "outputs": "Formatted_SEF_PDU, Security_Audit_Log_Record",
        "verification": "Automated security orchestration test verifying cloud VSOC alert dispatch in < 1.0s."
    }
])

# FEAT-DIA-01: UDS/EDR (Expanded to 4 sys reqs, 8 sw reqs)
f_dia = old_feats["FEAT-DIA-01"]
f_dia["sys_reqs"].extend([
    {
        "id": "SYS-DIA-01-03",
        "title": "49 CFR Part 563 Crash Event Data Recorder (EDR) Blackbox Buffer",
        "asil": "ASIL D / 49 CFR Part 563",
        "statement": "The System SHALL continuously record vehicle dynamic parameters at 100 Hz into circular FIFO RAM: Upon crash trigger (airbag deploy or delta-V > 8 km/h), system SHALL freeze and lock 5.0 seconds pre-crash and 300 ms post-crash telemetry into tamper-proof non-volatile flash memory.",
        "activation": "Active at all times while vehicle is powered.",
        "ftti": "10 ms",
        "safe_state": "Lock EDR flash memory against overwrite; preserve crash record across power loss.",
        "failure_reaction": "If flash write errors occur, write to redundant secondary EEPROM chip.",
        "inputs": "Vehicle_Speed_100Hz, Accelerator_Pedal_Pct_100Hz, Brake_Status_100Hz, Steering_Angle_100Hz, Delta_V_X_Y",
        "outputs": "EDR_Frozen_Record_Locked_Flag, NonVolatile_Flash_Write_Cmd",
        "verification": "Crash sled test and compliance verification against US NHTSA 49 CFR Part 563 regulatory data format.",
        "downstream": ["SWR-DIA-01-05", "SWR-DIA-01-06"]
    },
    {
        "id": "SYS-DIA-01-04",
        "title": "UDS ISO 14229 Service 0x27 Security Access Cryptographic Seed-Key",
        "asil": "ISO 21434 / ASIL B",
        "statement": "The System SHALL protect sensitive diagnostic services (flashing, variant coding, actuator override) using UDS Service 0x27 Security Access: Generating 32-byte cryptographically random seed and validating HMAC-SHA256 key response with anti-brute-force delay lockout (10s delay after 3 failed attempts).",
        "activation": "Active upon diagnostic session transition to Programming or Extended mode.",
        "ftti": "N/A",
        "safe_state": "Reject diagnostic command; lock security access level.",
        "failure_reaction": "If invalid key is supplied, increment failed attempt counter and enforce exponential time penalty.",
        "inputs": "Diagnostic_Session_Type, UDS_Security_Key_Response[32], TRNG_Random_Seed_Bytes",
        "outputs": "Security_Access_Unlocked_Level, NRC_Negative_Response_Code",
        "verification": "Diagnostic security penetration test attempting brute force dictionary attacks."
        ,"downstream": ["SWR-DIA-01-07", "SWR-DIA-01-08"]
    }
])
f_dia["sw_reqs"].extend([
    {
        "id": "SWR-DIA-01-05",
        "title": "100 Hz Circular RAM Crash Telemetry FIFO Ring Buffer",
        "parent": "SYS-DIA-01-03",
        "asil": "ASIL D",
        "swc": "EdrRingBuffer_SWC",
        "period": "10 ms",
        "wcet": "0.3 ms",
        "activation": "Executed continuously in 100 Hz cyclic task.",
        "algorithm": "Samples vehicle crash parameters: Speed (0.1 km/h res), Engine/Motor RPM, Throttle pedal %, Service brake ON/OFF, Steering angle, Lateral/Longitudinal accel, Seatbelt buckle status. Writes to 500-sample circular RAM buffer (5.0 seconds history).",
        "safety_mechanism": "ECC-protected RAM buffer: Detects single-bit memory flips and corrects automatically.",
        "failure_reaction": "Zero out corrupted sample and flag memory parity warning.",
        "inputs": "Vehicle_Speed_Mps, Accelerator_Pedal_Pct, Brake_Switch_Digital, Steering_Angle_Deg, IMU_Axial_G[3]",
        "outputs": "Circular_Buffer_Pointer, Current_Sample_Timestamp_Unix_Ms",
        "verification": "Timing jitter and buffer overwrite consistency test over 72 continuous hours."
    },
    {
        "id": "SWR-DIA-01-06",
        "title": "49 CFR Part 563 Crash Event Non-Volatile Flash Lock Controller",
        "parent": "SYS-DIA-01-03",
        "asil": "ASIL D",
        "swc": "EdrFlashLock_SWC",
        "period": "1 ms",
        "wcet": "0.5 ms",
        "activation": "Triggered on Airbag deployment discrete pin.",
        "algorithm": "Upon crash trigger interrupt, halts ring buffer overwrite: Continues sampling for exactly 300 ms (post-crash window), then copies entire 5.3s telemetry record to dedicated write-once flash memory sector. Computes CRC-32 checksum and asserts hardware write-protect pin.",
        "safety_mechanism": "Hardware write-protect: Flash sector permanently locked against erasure or UDS clear commands.",
        "failure_reaction": "If main 12V supply collapses, energy reserve capacitor powers flash write for 250 ms.",
        "inputs": "Airbag_Deploy_Interrupt_Flag, Backup_Capacitor_Voltage_V",
        "outputs": "EDR_Flash_Write_Complete_Flag, Hardware_Write_Protect_Pin",
        "verification": "Physical destructive crash sled testing with battery severance at impact t=0 ms."
    },
    {
        "id": "SWR-DIA-01-07",
        "title": "UDS 0x27 Cryptographic Pseudo-Random Seed Generator",
        "parent": "SYS-DIA-01-04",
        "asil": "ISO 21434 / ASIL B",
        "swc": "UdsSecurityAccess_SWC",
        "period": "10 ms",
        "wcet": "0.4 ms",
        "activation": "Triggered upon diagnostic request 0x27 0x01 / 0x03.",
        "algorithm": "Generates 32-byte cryptographically secure random number using on-chip True Random Number Generator (TRNG) entropy source. Transmits seed to diagnostic client. Starts 5.0-second response timeout window.",
        "safety_mechanism": "Seed reuse prevention: Every request generates fresh non-repeating random seed.",
        "failure_reaction": "Send NRC 0x37 (RequiredTimeDelayNotExpired) if client requests seed during lockout.",
        "inputs": "Diagnostic_Service_Request_Payload, TRNG_Entropy_Pool_Bytes",
        "outputs": "Diagnostic_Seed_Buffer[32], Security_Timeout_Timer_Ms",
        "verification": "NIST SP 800-22 statistical randomness test on generated diagnostic seeds."
    },
    {
        "id": "SWR-DIA-01-08",
        "title": "HMAC-SHA256 Key Validation & Brute-Force Delay Lockout",
        "parent": "SYS-DIA-01-04",
        "asil": "ISO 21434 / ASIL B",
        "swc": "UdsKeyValidator_SWC",
        "period": "10 ms",
        "wcet": "1.2 ms",
        "activation": "Triggered upon client submitting key (0x27 0x02 / 0x04).",
        "algorithm": "Computes expected key K_exp = HMAC_SHA256(Secret_Diagnostic_Key, Seed). Compares with client key using constant-time comparison to prevent timing attacks. If matching, unlocks security level. If mismatch, increments failed counter: Enforces 10-second lockout after 3 fails.",
        "safety_mechanism": "Constant-time memory comparator prevents side-channel timing analysis.",
        "failure_reaction": "Send NRC 0x35 (InvalidKey) and log security audit event.",
        "inputs": "Client_Submitted_Key_Bytes[32], Secret_Diagnostic_Master_Key, Failed_Attempt_Counter",
        "outputs": "Security_Unlocked_Flag (boolean), UDS_Negative_Response_Code",
        "verification": "Automated brute-force attack testing validating exponential time lockout."
    }
])

all_conn = [
    f1,
    old_feats["FEAT-TEL-02"],
    old_feats["FEAT-TEL-03"],
    f_sec,
    f_dia
]

print(f"Total Connectivity features compiled: {len(all_conn)}")
total_sys = sum(len(f['sys_reqs']) for f in all_conn)
total_sw = sum(len(f['sw_reqs']) for f in all_conn)
print(f"Total Connectivity SysReqs: {total_sys}, Total Connectivity SwReqs: {total_sw}")

code = "# Complete Telematics, Connectivity, Cybersecurity & Diagnostics Domain Features (5 Features)\n\n"
code += "full_conn_features = " + repr(all_conn) + "\n"
code += 'print(f"Loaded all {len(full_conn_features)} Connectivity, Security & Diagnostics features successfully.")\n'

with open("features_conn_full.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated features_conn_full.py successfully!")

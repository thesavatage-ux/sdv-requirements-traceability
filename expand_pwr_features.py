# expand_pwr_features.py
import features_pwr_full

old_feats = {f["id"]: f for f in features_pwr_full.full_pwr_features}

# FEAT-PWR-01: BMS (Expanded to 6 sys reqs, 14 sw reqs)
f1 = old_feats["FEAT-PWR-01"]
f1["sys_reqs"].extend([
    {
        "id": "SYS-PWR-01-04",
        "title": "Active & Passive High-Efficiency Cell Balancing Management",
        "asil": "ASIL C",
        "statement": "The System SHALL monitor cell delta voltage (|Delta_V_cell|) during charging: If Delta_V_cell > 15 mV, activate passive bleed resistors (up to 200 mA discharge per cell) or active inductive balancing to equalize cell voltages within +-5 mV at end-of-charge.",
        "activation": "Active in CLOSED_CHARGE state and top balancing phase.",
        "ftti": "500 ms",
        "safe_state": "Open balancing FET switches; terminate cell discharge.",
        "failure_reaction": "If balance resistor temperature exceeds 85°C, pulse balance duty cycle down to 25%.",
        "inputs": "Cell_Voltages_Array[192], Balance_Resistor_Temperatures[16], Charge_Current_A",
        "outputs": "Cell_Balancing_Switch_Bitmask[192], Balancing_Active_Flag",
        "verification": "Endurance top-balancing accuracy and thermal dissipation bench testing.",
        "downstream": ["SWR-PWR-01-09", "SWR-PWR-01-10"]
    },
    {
        "id": "SYS-PWR-01-05",
        "title": "High-Voltage Interlock Loop (HVIL) & Chassis Insulation Monitoring",
        "asil": "ASIL D",
        "statement": "The System SHALL sample High-Voltage Interlock Loop (HVIL) continuity at 1 kHz and evaluate insulation resistance between HV DC bus and 12V chassis ground (> 500 ohms/volt conforming to ISO 6469-1), opening main contactors in <= 20 ms if insulation degrades below 100 ohms/volt.",
        "activation": "Active continuously whenever BMS is energized.",
        "ftti": "20 ms",
        "safe_state": "Open high-voltage contactors; discharge DC link inverters.",
        "failure_reaction": "If HVIL loop breaks while driving, ramp motor torque to 0 Nm in 100 ms then open contactors.",
        "inputs": "HVIL_Pilot_Current_ADC, Insulation_Monitor_AC_Injected_Leakage, Pack_Voltage_V",
        "outputs": "Insulation_Resistance_kOhms, HVIL_Intact_Flag, Emergency_Open_Contactors_Cmd",
        "verification": "ISO 6469 electrical safety and deliberate human touch insulation fault injection.",
        "downstream": ["SWR-PWR-01-11", "SWR-PWR-01-12"]
    },
    {
        "id": "SYS-PWR-01-06",
        "title": "Cell Thermal Runaway Precursor Gas & Pressure Wave Detection",
        "asil": "ASIL D",
        "statement": "The System SHALL monitor battery pack internal cavity pressure sensors (Delta_P > 50 mbar/s) and hydrogen/CO electrochemical gas sensors at 100 Hz, firing the pyrofuse within <= 2 ms and opening emergency pack aerosol gas vents upon thermal runaway onset.",
        "activation": "Active at all times, including parked sleeping state.",
        "ftti": "5 ms",
        "safe_state": "Blow pyrofuse disconnect; command cabin emergency evacuation siren.",
        "failure_reaction": "Wake up BMS micro instantly if pack enclosure burst disc switch activates.",
        "inputs": "Pack_Cavity_Pressure_Sensor_Bar, H2_Gas_Sensor_PPM, Module_Thermistor_Max_Rate_DegC_S",
        "outputs": "Pyrofuse_Fire_Signal, Emergency_Vent_Valve_Cmd, Thermal_Runaway_Evacuation_Alarm",
        "verification": "UL 2580 cell nail penetration destructive runaway testing in explosion-proof chamber.",
        "downstream": ["SWR-PWR-01-13", "SWR-PWR-01-14"]
    }
])
f1["sw_reqs"].extend([
    {
        "id": "SWR-PWR-01-09",
        "title": "Cell Voltage Sorting & Passive Bleed Duration Scheduler",
        "parent": "SYS-PWR-01-04",
        "asil": "ASIL C",
        "swc": "BmsBalancingScheduler_SWC",
        "period": "100 ms",
        "wcet": "1.2 ms",
        "activation": "Executed during battery charging.",
        "algorithm": "Computes lowest cell voltage V_min = min(V_cell[1..192]). For each cell i: If V_cell[i] - V_min > 15 mV and V_cell[i] > 3.90V, commands bleed switch ON for duration t_bleed = K_bal * (V_cell[i] - V_min). Interleaves balancing to distribute module thermal heat.",
        "safety_mechanism": "Thermal duty limiter: Clamps maximum concurrent balancing channels to <= 25% of cells.",
        "failure_reaction": "Disable balancing if any balance zone thermistor exceeds 80°C.",
        "inputs": "Cell_Voltages_Array[192], Module_Temperatures_Array[32]",
        "outputs": "Balance_Channel_Commands[192], Balancing_Current_Estimate_mA",
        "verification": "Cell equalization bench test across 100 unbalanced synthetic cells."
    },
    {
        "id": "SWR-PWR-01-10",
        "title": "Balancing Switch Stuck-Closed Hardware Diagnostic Monitor",
        "parent": "SYS-PWR-01-04",
        "asil": "ASIL C",
        "swc": "BmsBalancingDiag_SWC",
        "period": "1000 ms",
        "wcet": "0.5 ms",
        "activation": "Executed periodically when balancing is idle.",
        "algorithm": "Commands all balancing switches OFF. Measures voltage drop across bleed resistors. If voltage drop indicates continuous current draw (> 5 mA) when commanded OFF, identifies stuck-closed balancing MOSFET.",
        "safety_mechanism": "Protects cell from permanent over-discharge self-drain.",
        "failure_reaction": "Set DEM DTC P0B24 (Battery Cell Balancing Circuit Stuck On) and notify service.",
        "inputs": "Bleed_Resistor_Current_Sensors, Balancing_Command_State",
        "outputs": "Balancing_Circuit_Fault_Mask[192], Stuck_Switch_Detected_Flag",
        "verification": "Hardware fault injection shorting balance MOSFET gate."
    },
    {
        "id": "SWR-PWR-01-11",
        "title": "High-Voltage Interlock Loop (HVIL) Fast Edge-Detector",
        "parent": "SYS-PWR-01-05",
        "asil": "ASIL D",
        "swc": "BmsHvilSupervisor_SWC",
        "period": "1 ms",
        "wcet": "0.15 ms",
        "activation": "Executed in 1 kHz hardware timer ISR.",
        "algorithm": "Samples high-speed comparator monitoring 10 mA pilot current loop routed through all HV connectors, inverter covers, and service plugs. If pilot line opens for >= 2 consecutive samples (2 ms), asserts HVIL_Trip_Asserted.",
        "safety_mechanism": "Direct hardware trip pin to contactor economizer driver circuit.",
        "failure_reaction": "Command VCU inverter zero torque in 50 ms then open contactors.",
        "inputs": "HVIL_Current_ADC, HVIL_Comparator_Interrupt_Flag",
        "outputs": "HVIL_Trip_Asserted (boolean), HVIL_Break_Timestamp_Unix_Ms",
        "verification": "Mechanical connector unplugging under live high-voltage load test bench."
    },
    {
        "id": "SWR-PWR-01-12",
        "title": "Low-Frequency AC Injected Chassis Insulation Impedance Observer",
        "parent": "SYS-PWR-01-05",
        "asil": "ASIL D",
        "swc": "BmsInsulationObserver_SWC",
        "period": "100 ms",
        "wcet": "0.8 ms",
        "activation": "Continuous cyclic task.",
        "algorithm": "Injects balanced 10 Hz AC sinusoidal pilot voltage (+-20V) between HV DC bus and vehicle chassis. Measures leakage return current and phase angle. Extracts real isolation resistance R_iso = V_inject / I_real. Flags warning if R_iso < 500 kOhm; trips critical if R_iso < 100 kOhm.",
        "safety_mechanism": "Galvanic isolation guard: Injected pilot signal energy limited to < 2.0 mJ (harmless to touch).",
        "failure_reaction": "Latch DTC P0AA6 (Hybrid/EV Battery Voltage System Isolation Fault).",
        "inputs": "Injected_Pilot_Voltage_ADC, Injected_Leakage_Current_ADC, DC_Bus_Voltage_V",
        "outputs": "Measured_Isolation_Resistance_kOhm, Isolation_Fault_Level_Enum",
        "verification": "Calibrated decade resistance box leakage test to chassis ground."
    },
    {
        "id": "SWR-PWR-01-13",
        "title": "Pack Cavity Pressure Wave dP/dt Transient Analyzer",
        "parent": "SYS-PWR-01-06",
        "asil": "ASIL D",
        "swc": "BmsPressureWave_SWC",
        "period": "10 ms",
        "wcet": "0.4 ms",
        "activation": "Continuous safety task.",
        "algorithm": "Samples sealed battery pack enclosure barometric pressure: Computes pressure rate of rise dP/dt = (P[k] - P[k-1]) / dT. If dP/dt > 50.0 mbar/s (indicative of cell safety vent rupture), flags Thermal_Runaway_Onset.",
        "safety_mechanism": "Barometric pressure compensation: Adjusts baseline for atmospheric pressure changes when driving uphill.",
        "failure_reaction": "Trigger emergency pyrofuse disconnect within 2 ms.",
        "inputs": "Pack_Internal_Pressure_Mbar, Ambient_Barometric_Pressure_Mbar",
        "outputs": "Pressure_Rate_Of_Rise_Mbar_S, Pressure_Wave_Detected_Flag (boolean)",
        "verification": "Gas cannister controlled pulse venting inside sealed battery mock enclosure."
    },
    {
        "id": "SWR-PWR-01-14",
        "title": "Hydrogen Electrochemical Precursor Gas Cross-Correlator",
        "parent": "SYS-PWR-01-06",
        "asil": "ASIL D",
        "swc": "BmsGasCorrelator_SWC",
        "period": "50 ms",
        "wcet": "0.6 ms",
        "activation": "Continuous gas monitoring.",
        "algorithm": "Samples solid-state hydrogen (H2) and carbon monoxide (CO) electrochemical sensors inside pack venting plenum. If H2 concentration exceeds 500 ppm AND any cell temperature rate dT/dt > 1.0 °C/s, asserts Thermal_Runaway_Confirmed.",
        "safety_mechanism": "Sensor baseline autozero calibration to prevent false alarms over 10-year vehicle lifetime.",
        "failure_reaction": "Command vehicle horn alarm and broadcast cloud telematics fire alert.",
        "inputs": "H2_Sensor_Concentration_PPM, CO_Sensor_Concentration_PPM, Max_Cell_Temp_Rate_DegC_S",
        "outputs": "Thermal_Runaway_Confirmed_Flag (boolean), Off_Gas_Severity_Index",
        "verification": "Electrochemical laboratory off-gassing test during lithium-ion overcharge."
    }
])

# FEAT-PWR-02: VCU (Expanded to 5 sys reqs, 11 sw reqs)
f2 = old_feats["FEAT-PWR-02"]
f2["sys_reqs"].extend([
    {
        "id": "SYS-PWR-02-04",
        "title": "Low-Speed Creep & Hill-Hold Anti-Rollback Controller",
        "asil": "ASIL C",
        "statement": "The System SHALL simulate automatic transmission creep torque (up to 40 Nm @ 0-5 km/h) when brake is released in DRIVE, and execute active motor zero-speed electrical hill-hold on inclines up to 30% without vehicle rollback (> 2 cm).",
        "activation": "Active at speeds < 5 km/h in forward or reverse gears.",
        "ftti": "40 ms",
        "safe_state": "Engage hydraulic ESP brake clamping; zero motor electrical hold.",
        "failure_reaction": "If electric motor overheats during sustained hill hold (> 10s), clamp foundation brakes.",
        "inputs": "Road_Incline_Grade_Pct, Brake_Pedal_Released_Flag, Motor_Rotor_Position_Resolver",
        "outputs": "Creep_Torque_Demand_Nm, Anti_Rollback_Hold_Torque_Nm, Hill_Hold_Active_Flag",
        "verification": "30% steep ramp vehicle stop and roll-back prevention proving ground testing.",
        "downstream": ["SWR-PWR-02-08", "SWR-PWR-02-09"]
    },
    {
        "id": "SYS-PWR-02-05",
        "title": "Multi-Component Thermal Derating & Motor Over-Temperature Limiter",
        "asil": "ASIL B",
        "statement": "The System SHALL monitor stator winding temperatures (FL, FR, Rear motors) and inverter SiC MOSFET junction temperatures, smoothly derating maximum allowable drive torque (from 100% to 20% over 140°C to 175°C) to prevent thermal demagnetization.",
        "activation": "Active at all times during vehicle propulsion.",
        "ftti": "200 ms",
        "safe_state": "Limit motor torque to 50 Nm limp-home mode.",
        "failure_reaction": "If stator temperature exceeds 185°C, disconnect motor inverter gate drives immediately.",
        "inputs": "Motor_Stator_Temp_DegC, Inverter_SiC_Temp_DegC, Coolant_Flow_Rate_Lpm",
        "outputs": "Thermal_Derated_Torque_Limit_Nm, Motor_Cooling_Pump_Target_RPM",
        "verification": "Dynamometer high-speed autobahn top-speed thermal saturation endurance testing.",
        "downstream": ["SWR-PWR-02-10", "SWR-PWR-02-11"]
    }
])
f2["sw_reqs"].extend([
    {
        "id": "SWR-PWR-02-08",
        "title": "Zero-Speed Motor Rotor Electrical Hill-Hold Servo",
        "parent": "SYS-PWR-02-04",
        "asil": "ASIL C",
        "swc": "VcuHillHold_SWC",
        "period": "5 ms",
        "wcet": "0.4 ms",
        "activation": "Active when vehicle stopped on grade.",
        "algorithm": "Samples high-resolution motor resolver: If vehicle velocity < 0.1 km/h and brake pedal is released, executes position-locking PID servo on motor rotor angle: T_hold = K_p_pos * (Theta_target - Theta_meas) + K_d_pos * Omega_meas + m_veh * g * sin(Grade) * r_wheel.",
        "safety_mechanism": "Rotor movement guard: If rotor slips backward > 15 degrees, pulses hydraulic brake pressure.",
        "failure_reaction": "Handover to ESP hydraulic hill hold if motor current draws > 150A for > 8.0s.",
        "inputs": "Motor_Resolver_Angle_Rad, Incline_Grade_Rad, Brake_Pedal_Pressure_Bar",
        "outputs": "Active_Rotor_Hold_Torque_Nm, ESP_Handover_Request_Flag",
        "verification": "Chassis dynamometer slope simulation with zero rollback verification."
    },
    {
        "id": "SWR-PWR-02-09",
        "title": "Configurable Low-Speed Vehicle Creep Velocity Profiler",
        "parent": "SYS-PWR-02-04",
        "asil": "ASIL B",
        "swc": "VcuCreepProfiler_SWC",
        "period": "10 ms",
        "wcet": "0.3 ms",
        "activation": "Active when creep mode enabled by driver.",
        "algorithm": "Generates simulated torque converter creep feel: T_creep = T_creep_max * max(0.0, 1.0 - v_ego / V_creep_limit) with V_creep_limit = 6.0 km/h and T_creep_max = 50 Nm. Smoothly decays torque to zero when driver touches brake pedal.",
        "safety_mechanism": "Door ajar interlock: Creep torque is forced to 0 Nm if any passenger door or trunk opens.",
        "failure_reaction": "Zero creep torque if accelerator pedal sensor status is questionable.",
        "inputs": "Vehicle_Speed_Mps, Driver_Creep_Enable_Setting, Door_Status_Bits",
        "outputs": "Regulated_Creep_Torque_Demand_Nm, Creep_Active_Status (boolean)",
        "verification": "Subjective low-speed parking lot driveability evaluation."
    },
    {
        "id": "SWR-PWR-02-10",
        "title": "Stator Winding & SiC Inverter Thermal Resistance Model",
        "parent": "SYS-PWR-02-05",
        "asil": "ASIL B",
        "swc": "VcuThermalModel_SWC",
        "period": "100 ms",
        "wcet": "0.8 ms",
        "activation": "Cyclic 100 ms task.",
        "algorithm": "Implements 4-node lumped thermal capacitance model: Computes internal motor magnet temperature T_rotor_est and power module junction temperature T_j: T_j = T_case + P_loss * R_th_jc. Detects hotspot divergence from single point sensor.",
        "safety_mechanism": "Conservative bound: If coolant temperature sensor fails, assumes worst-case 85°C coolant.",
        "failure_reaction": "Report DEM DTC P0A2F (Drive Motor Temperature Sensor Circuit Range/Performance).",
        "inputs": "Motor_Stator_Thermistor_DegC, Coolant_Inlet_Temp_DegC, Inverter_Phase_Current_RMS",
        "outputs": "Estimated_Rotor_Magnet_Temp_DegC, Junction_Temp_Max_DegC",
        "verification": "Infrared thermal camera dynamometer validation on electric motor test cell."
    },
    {
        "id": "SWR-PWR-02-11",
        "title": "Continuous Thermal Torque Derating Look-Up Interpolator",
        "parent": "SYS-PWR-02-05",
        "asil": "ASIL B",
        "swc": "VcuThermalDerater_SWC",
        "period": "20 ms",
        "wcet": "0.4 ms",
        "activation": "Active during propulsion.",
        "algorithm": "Computes scaling factor K_thermal in [0.0, 1.0]: K_thermal = 1.0 if T_max < 140°C; linearly scales to 0.1 at 175°C; reaches 0.0 at 185°C. Applies rate limiter (max -50 Nm/s) to ensure smooth torque fade without abrupt deceleration jerk.",
        "safety_mechanism": "Cluster notification trigger: Displays 'Power Reduced Due to Temperature' icon when K_thermal < 0.7.",
        "failure_reaction": "Clamp torque to 30% if temperature sensors short or open.",
        "inputs": "Junction_Temp_Max_DegC, Estimated_Rotor_Magnet_Temp_DegC",
        "outputs": "Thermal_Torque_Derate_Factor, Cluster_Thermal_Derate_Alert",
        "verification": "Climatic chamber hot desert hill-climb full throttle simulation."
    }
])

# FEAT-PWR-03: RBC (Expanded to 4 sys reqs, 8 sw reqs)
f3 = old_feats["FEAT-PWR-03"]
f3["sys_reqs"].extend([
    {
        "id": "SYS-PWR-03-03",
        "title": "ABS Wheel Slip Fast Regeneration Cutback & Surface Coordination",
        "asil": "ASIL D",
        "statement": "The System SHALL reduce regenerative motor braking torque to 0 Nm in <= 20 ms upon ESP detecting wheel slip (slip ratio lambda > 12% on low-friction road surfaces), transferring 100% deceleration to modulated hydraulic ABS.",
        "activation": "Active during regenerative deceleration on slippery roads.",
        "ftti": "20 ms",
        "safe_state": "Zero electric motor regen torque; enable hydraulic ABS.",
        "failure_reaction": "If motor torque ramp-down is delayed > 25 ms, open inverter PWM gates.",
        "inputs": "Wheel_Slip_Ratio_Array[4], ABS_Intervention_Active_Flag, ESP_Friction_Mu_Est",
        "outputs": "Regen_Cutback_Command (boolean), Motor_Regen_Torque_Clamp_Nm",
        "verification": "Split-mu ice-asphalt braking deceleration stability tests."
        ,"downstream": ["SWR-PWR-03-05", "SWR-PWR-03-06"]
    },
    {
        "id": "SYS-PWR-03-04",
        "title": "Battery Low-Temperature & High SOC Regeneration Envelope Limiter",
        "asil": "ASIL C",
        "statement": "The System SHALL dynamically scale regenerative deceleration based on battery BMS charge acceptance limit (P_chg_max): Seamlessly substituting hydraulic friction braking to maintain consistent driver pedal decel feel when battery is cold (< 0°C) or fully charged (> 95% SOC).",
        "activation": "Active whenever regenerative braking is engaged.",
        "ftti": "100 ms",
        "safe_state": "Rely 100% on foundation hydraulic brakes for deceleration.",
        "failure_reaction": "If BMS broadcast drops, restrict regen power to 0 kW.",
        "inputs": "BMS_Max_Charge_Power_Limit_kW, Battery_Pack_SOC_Pct, Battery_Pack_Min_Temp_DegC",
        "outputs": "Allowable_Regen_Power_kW, Friction_Brake_Compensation_Demand_Bar",
        "verification": "Winter cold soak (-20°C) braking deceleration consistency test."
        ,"downstream": ["SWR-PWR-03-07", "SWR-PWR-03-08"]
    }
])
f3["sw_reqs"].extend([
    {
        "id": "SWR-PWR-03-05",
        "title": "Fast Wheel Slip Motor Inverter Regeneration Trip Commander",
        "parent": "SYS-PWR-03-03",
        "asil": "ASIL D",
        "swc": "RbcSlipCoordinator_SWC",
        "period": "2 ms",
        "wcet": "0.15 ms",
        "activation": "Executed in 500 Hz high-speed traction ISR.",
        "algorithm": "Samples ABS slip active flag over dedicated chassis CAN-FD: If Slip_Active == TRUE OR Wheel_Decel > -18 m/s², immediately ramps motor regenerative torque to 0 Nm at slew rate d(T)/dt = 10,000 Nm/s (achieving 0 Nm in < 15 ms).",
        "safety_mechanism": "Direct SPI bus trip signal sent directly to motor inverter control core.",
        "failure_reaction": "Command emergency gate shutdown if motor fails to de-torque.",
        "inputs": "ESP_Slip_Flag_Array[4], Motor_Actual_Regen_Torque_Nm",
        "outputs": "Fast_Regen_Cutback_Req, Inverter_Torque_Clamp_Nm",
        "verification": "Low-friction split-mu dyno bench step response testing."
    },
    {
        "id": "SWR-PWR-03-06",
        "title": "ESP Hydraulic Friction Brake Blending Handover Manager",
        "parent": "SYS-PWR-03-03",
        "asil": "ASIL D",
        "swc": "RbcFrictionBlending_SWC",
        "period": "5 ms",
        "wcet": "0.3 ms",
        "activation": "Active during regen cutback.",
        "algorithm": "Calculates deceleration deficit: Delta_a = Decel_Demanded - Decel_Motor_Delivered. Transmits friction brake pressure request to ESP: P_caliper = Delta_a * M_veh * R_wheel / (2 * A_piston * mu_pad * r_eff) to guarantee seamless vehicle stopping distance.",
        "safety_mechanism": "Deceleration continuity guard: Ensures vehicle deceleration does not drop by > 0.05g during handover.",
        "failure_reaction": "Engage maximum hydraulic booster pressure upon motor cutback failure.",
        "inputs": "Delta_a_Decel_Deficit_Mps2, ESP_Master_Pressure_Bar",
        "outputs": "ESP_Pressure_Compensation_Bar, Blending_Handoff_Status_Enum",
        "verification": "Braking distance repeatability test across 100 cold/wet stops."
    },
    {
        "id": "SWR-PWR-03-07",
        "title": "BMS Charge Acceptance Dynamic Envelope Follower",
        "parent": "SYS-PWR-03-04",
        "asil": "ASIL C",
        "swc": "RbcBmsEnvelopeFollower_SWC",
        "period": "10 ms",
        "wcet": "0.4 ms",
        "activation": "Cyclic 10 ms task.",
        "algorithm": "Ingests BMS P_chg_max (kW) over E2E-protected CAN-FD. Calculates maximum allowable motor regenerative torque: T_regen_max = min(T_one_pedal, (P_chg_max * 1000) / (Omega_motor + 0.1)). Clamps motor negative torque within battery electrochemical safe envelope.",
        "safety_mechanism": "Battery overvoltage protection: Cuts regen instantly if DC bus voltage exceeds 420V / 840V.",
        "failure_reaction": "Default allowable regen to 0 kW upon BMS communication loss.",
        "inputs": "BMS_Max_Charge_Power_kW, DC_Bus_Voltage_V, Motor_Speed_RadS",
        "outputs": "Battery_Clamped_Regen_Torque_Nm, Overvoltage_Safety_Trip (boolean)",
        "verification": "Full battery pack charge tapering and HIL battery emulator testing."
    },
    {
        "id": "SWR-PWR-03-08",
        "title": "Consistent Pedal Feel Friction Hydraulic Compensator",
        "parent": "SYS-PWR-03-04",
        "asil": "ASIL C",
        "swc": "RbcPedalFeelCompensator_SWC",
        "period": "10 ms",
        "wcet": "0.5 ms",
        "activation": "Active when battery derating reduces regen.",
        "algorithm": "When battery SOC > 95% and regen torque is curtailed, automatically commands electric brake booster to apply foundation caliper friction brakes equal to missing regen torque: Driver experiences identical 0.2g one-pedal lift-off deceleration regardless of battery state.",
        "safety_mechanism": "Brake pad thermal accumulator model: Monitors rotor temperature during sustained friction compensation.",
        "failure_reaction": "Display 'Regen Braking Temporarily Reduced' cluster prompt if brakes warm.",
        "inputs": "Driver_Throttle_Pedal_Pct, Battery_Clamped_Regen_Torque_Nm, Nominal_Regen_Torque_Nm",
        "outputs": "Friction_Caliper_Compensation_Bar, Consistent_Pedal_Feel_Active (boolean)",
        "verification": "Driver blind subjective pedal feel consistency evaluations across 100% vs 20% SOC."
    }
])

all_pwr = [f1, f2, f3, old_feats["FEAT-PWR-04"], old_feats["FEAT-PWR-05"], old_feats["FEAT-PWR-06"], old_feats["FEAT-PWR-07"]]

print(f"Total Powertrain features compiled: {len(all_pwr)}")
total_sys = sum(len(f['sys_reqs']) for f in all_pwr)
total_sw = sum(len(f['sw_reqs']) for f in all_pwr)
print(f"Total Powertrain SysReqs: {total_sys}, Total Powertrain SwReqs: {total_sw}")

code = "# Complete Electric Powertrain, Battery & Charging Domain Features (7 Features)\n\n"
code += "full_pwr_features = " + repr(all_pwr) + "\n"
code += 'print(f"Loaded all {len(full_pwr_features)} Powertrain features successfully.")\n'

with open("features_pwr_full.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated features_pwr_full.py successfully!")

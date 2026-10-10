import json
import os
import re
import features_adas_full
import features_pwr_full
import features_chs_full
import features_bdy_full
import features_cpt_full
import features_conn_full

conn_order = {'FEAT-TEL-01': 1, 'FEAT-TEL-02': 2, 'FEAT-TEL-03': 3, 'FEAT-SEC-01': 4, 'FEAT-DIA-01': 5}
sorted_conn = sorted(features_conn_full.full_conn_features, key=lambda x: conn_order.get(x['id'], 99))

all_features = (
    features_adas_full.adas_features +
    features_pwr_full.full_pwr_features +
    features_chs_full.full_chs_features +
    features_bdy_full.full_bdy_features +
    features_cpt_full.full_cpt_features +
    sorted_conn
)

BASE_DIR = r"c:\Workset\AntiGravityProjects\TestOptimisationExperiement"

def determine_swc_type(name):
    n = name.lower()
    if any(k in n for k in ['sensor', 'fusion', 'observer', 'predict', 'estimator', 'camera', 'radar', 'imu', 'gnss']):
        return "SensorActuatorSWC"
    if any(k in n for k in ['actuator', 'coordinator', 'driver', 'booster', 'modulator', 'inverter', 'pwm', 'gate']):
        return "ActuatorSWC"
    if any(k in n for k in ['state', 'supervisor', 'manager', 'arbitrat', 'governor', 'interlock', 'sequencer']):
        return "ServiceSupervisorSWC"
    if any(k in n for k in ['cdd', 'direct', 'spi_dma', 'dma']):
        return "ComplexDeviceDriverSWC"
    return "ApplicationSWC"

def determine_core_allocation(domain, asil):
    d = domain.lower()
    if 'chassis' in d or 'motion' in d:
        return {"core": "Core 1", "desc": "Lockstep ASIL D Chassis Core", "freq": "300 MHz", "task": "Task_1ms_Chassis"}
    elif 'powertrain' in d or 'power' in d:
        return {"core": "Core 2", "desc": "Lockstep ASIL C/D Powertrain Core", "freq": "300 MHz", "task": "Task_1ms_Inverter"}
    elif 'adas' in d:
        return {"core": "Core 3", "desc": "High-Performance ASIL B ADAS Core", "freq": "400 MHz", "task": "Task_10ms_ADAS"}
    elif 'body' in d:
        return {"core": "Core 0", "desc": "Body & Vehicle Infrastructure Core", "freq": "300 MHz", "task": "Task_20ms_Body"}
    elif 'cockpit' in d:
        return {"core": "HPC Core", "desc": "ARM Cortex-A78 HPC Application Cluster", "freq": "1.8 GHz", "task": "Posix_App_Cockpit"}
    else:
        return {"core": "Core 0", "desc": "Gateway, Security & BSW Core", "freq": "300 MHz", "task": "Task_5ms_Gateway"}

def determine_mpu_partition(asil):
    a = (asil or "QM").upper()
    if "ASIL D" in a:
        return {"partition": "MPU_PARTITION_ASIL_D", "privilege": "Supervisor (Isolated Lockstep)", "color": "#ef4444"}
    elif "ASIL C" in a:
        return {"partition": "MPU_PARTITION_ASIL_C", "privilege": "Trusted ASIL C", "color": "#f97316"}
    elif "ASIL B" in a:
        return {"partition": "MPU_PARTITION_ASIL_B", "privilege": "Standard ASIL B", "color": "#eab308"}
    elif "ASIL A" in a:
        return {"partition": "MPU_PARTITION_ASIL_A", "privilege": "Monitored ASIL A", "color": "#38bdf8"}
    else:
        return {"partition": "MPU_PARTITION_QM", "privilege": "Non-Privileged QM User Mode", "color": "#94a3b8"}

# Build SWC Registry
swc_registry = {}

for f in all_features:
    f_id = f["id"]
    f_name = f["name"]
    domain = f["domain"]
    
    for sw in f.get("sw_reqs", []):
        swc_name = sw.get("swc", "Generic_SWC")
        
        if swc_name not in swc_registry:
            swc_type = determine_swc_type(swc_name)
            asil_val = sw.get("asil", f.get("asil", "QM"))
            core_info = determine_core_allocation(domain, asil_val)
            mpu_info = determine_mpu_partition(asil_val)
            
            swc_registry[swc_name] = {
                "name": swc_name,
                "type": swc_type,
                "domain": domain,
                "feature_id": f_id,
                "feature_name": f_name,
                "asil": asil_val,
                "core": core_info["core"],
                "core_desc": core_info["desc"],
                "core_task": core_info["task"],
                "mpu_partition": mpu_info["partition"],
                "mpu_privilege": mpu_info["privilege"],
                "mpu_color": mpu_info["color"],
                "runnables": [],
                "ports_required": [],
                "ports_provided": [],
                "dem_events": [],
                "sw_req_ids": [],
                "primary_period": sw.get("period", "10 ms"),
                "total_wcet_ms": 0.0
            }
            
        entry = swc_registry[swc_name]
        entry["sw_req_ids"].append(sw["id"])
        
        # Parse WCET
        wcet_str = sw.get("wcet", "0.5 ms")
        wcet_num = 0.5
        match = re.search(r"([\d\.]+)", wcet_str)
        if match:
            try:
                wcet_num = float(match.group(1))
            except:
                pass
        entry["total_wcet_ms"] = round(entry["total_wcet_ms"] + wcet_num, 2)
        
        # Build Runnable
        runnable_name = f"Runnable_{swc_name.replace('_SWC', '')}_{sw.get('period', '10ms').replace(' ', '')}"
        entry["runnables"].append({
            "name": runnable_name,
            "sw_req_id": sw["id"],
            "title": sw["title"],
            "period": sw.get("period", "10 ms"),
            "wcet": wcet_str,
            "wcet_num": wcet_num,
            "trigger": "TimingEvent" if "ms" in sw.get("period", "") else "DataReceivedEvent",
            "algorithm": sw.get("algorithm", "Deterministic mathematical law evaluation."),
            "safety_mechanism": sw.get("safety_mechanism", "Plausibility bounds checking."),
            "stack_bytes": 1024 if "ASIL D" in entry["asil"] else 512
        })
        
        # Parse Required Ports (Inputs)
        raw_inputs = sw.get("inputs", "")
        for p in [x.strip() for x in raw_inputs.split(",") if x.strip()]:
            clean_p = p.replace("`", "")
            port_name = clean_p.split()[0].split("(")[0]
            if port_name and not any(rp["name"] == port_name for rp in entry["ports_required"]):
                data_type = "float32"
                if "bool" in clean_p.lower() or "flag" in clean_p.lower(): data_type = "boolean"
                elif "array" in clean_p.lower() or "[" in clean_p: data_type = "Array_t"
                elif "struct" in clean_p.lower(): data_type = "Structure_t"
                elif "enum" in clean_p.lower() or "code" in clean_p.lower() or "state" in clean_p.lower(): data_type = "uint8"
                
                entry["ports_required"].append({
                    "name": f"RPort_{port_name}",
                    "signal": port_name,
                    "interface_type": "SenderReceiverInterface",
                    "data_type": data_type,
                    "e2e_profile": "Profile_4 (CRC-16)" if "ASIL" in entry["asil"] else "None",
                    "init_val": "0.0" if data_type == "float32" else "FALSE" if data_type == "boolean" else "0"
                })
                
        # Parse Provided Ports (Outputs)
        raw_outputs = sw.get("outputs", "")
        for p in [x.strip() for x in raw_outputs.split(",") if x.strip()]:
            clean_p = p.replace("`", "")
            port_name = clean_p.split()[0].split("(")[0]
            if port_name and not any(pp["name"] == port_name for pp in entry["ports_provided"]):
                data_type = "float32"
                if "bool" in clean_p.lower() or "flag" in clean_p.lower(): data_type = "boolean"
                elif "array" in clean_p.lower() or "[" in clean_p: data_type = "Array_t"
                elif "struct" in clean_p.lower(): data_type = "Structure_t"
                elif "enum" in clean_p.lower() or "status" in clean_p.lower(): data_type = "uint8"
                
                entry["ports_provided"].append({
                    "name": f"PPort_{port_name}",
                    "signal": port_name,
                    "interface_type": "SenderReceiverInterface",
                    "data_type": data_type,
                    "e2e_profile": "Profile_4 (CRC-16)" if "ASIL" in entry["asil"] else "None",
                    "init_val": "0.0" if data_type == "float32" else "FALSE" if data_type == "boolean" else "0"
                })
                
        # Parse DEM Events
        fail_react = sw.get("failure_reaction", "")
        if "dem" in fail_react.lower() or "dtc" in fail_react.lower():
            dem_id = f"DEM_EVENT_{swc_name.upper()}_ERR"
            if dem_id not in entry["dem_events"]:
                entry["dem_events"].append(dem_id)

swc_list = sorted(list(swc_registry.values()), key=lambda x: (x["domain"], x["name"]))
print(f"Total Unique AUTOSAR SWCs fully modeled: {len(swc_list)}")

# Compute Architecture Stats
stats = {
    "total_swcs": len(swc_list),
    "total_runnables": sum(len(s["runnables"]) for s in swc_list),
    "total_required_ports": sum(len(s["ports_required"]) for s in swc_list),
    "total_provided_ports": sum(len(s["ports_provided"]) for s in swc_list),
    "asil_d_swcs": sum(1 for s in swc_list if "ASIL D" in s["asil"].upper()),
    "core_distribution": {},
    "type_distribution": {},
    "domain_distribution": {}
}

for s in swc_list:
    c = s["core"]
    stats["core_distribution"][c] = stats["core_distribution"].get(c, 0) + 1
    t = s["type"]
    stats["type_distribution"][t] = stats["type_distribution"].get(t, 0) + 1
    d = s["domain"]
    stats["domain_distribution"][d] = stats["domain_distribution"].get(d, 0) + 1

print("Architecture Stats:", stats)

# Write software_architecture.md
arch_md = f"""# Software Architecture & Component Design Specification (AUTOSAR Classic & Adaptive)
**Document Version:** 3.0.0  
**Compliance Standards:** ASPICE PAM v3.1 (SWE.2 Software Architecture, SWE.3 Component Design) / ISO 26262:2018 Part 6 / AUTOSAR Release 4.4.0 & Adaptive R20-11  
**Target Hardware:** Multi-Core Automotive SoC / MCU (Infineon AURIX TC49x TriCore / ARM Cortex-R52 + Cortex-A78 HPC)  
**Interactive Design Viewer:** [`software_architecture_design.html`](software_architecture_design.html)  
**Requirements Traceability Matrix:** [`requirements_traceability_matrix.html`](requirements_traceability_matrix.html)

---

## 1. Executive Summary & Architecture Scope

This specification defines the complete layered software architecture and detailed component design for our **40 Software-Defined Vehicle (SDV) Features**, comprising **{stats['total_swcs']} AUTOSAR Software Components (SWCs)**, **{stats['total_runnables']} Periodic/Event Runnables**, and **{stats['total_required_ports'] + stats['total_provided_ports']} VFB Port Interfaces**.

```mermaid
graph TD
    subgraph "Application Layer (SWE.2 / SWE.3)"
        SWC_App["Application SWCs (Control Laws & State Machines)"]
        SWC_Sens["Sensor SWCs (Filtering & Plausibility)"]
        SWC_Act["Actuator SWCs (PWM & Gate Drivers)"]
    end

    subgraph "Runtime Environment (RTE) / Virtual Functional Bus (VFB)"
        RTE["AUTOSAR RTE (Contract Phase & Generation Phase)<br>• S/R Interfaces (E2E Protection)<br>• C/S Operations & Inter-Runnable Variables (IRVs)"]
    end

    subgraph "Basic Software (BSW)"
        subgraph "Services Layer"
            OS["AUTOSAR OS (Multi-Core, OSEK/VDX Tasks)"]
            DEM["Diagnostic Event Manager (DEM / DTCs)"]
            WdgM["Watchdog Manager (WdgM / Alive & Deadline)"]
            SecOC["Secure Onboard Communication (SecOC / MAC)"]
            NvM["Non-Volatile Memory Manager (NvM / Flash)"]
        end
        subgraph "ECU Abstraction Layer"
            IoHwAb["IO Hardware Abstraction (IoHwAb)"]
            CanIf["CAN Interface (CanIf / CAN-FD)"]
            EthIf["Ethernet Interface (EthIf / SOME/IP)"]
        end
        subgraph "Microcontroller Abstraction Layer (MCAL)"
            MCU["MCU / Clock Driver"]
            ADC["ADC Driver (SENT / SPI)"]
            PWM["PWM / Motor Gate Driver"]
            PORT["Port / Dio Driver"]
        end
    end

    SWC_App <--> RTE
    SWC_Sens <--> RTE
    SWC_Act <--> RTE
    RTE <--> OS
    RTE <--> DEM
    RTE <--> WdgM
    RTE <--> SecOC
    RTE <--> NvM
    IoHwAb <--> ADC
    CanIf <--> MCU
    EthIf <--> MCU
```

---

## 2. Multi-Core Allocation & OS Task Scheduling (TC49x / R52)

| Compute Core | Target Domain | Core Frequency | OS Task Queues | ASIL Isolation | Allocated SWCs | Primary Function |
| :--- | :--- | :---: | :--- | :---: | :-: | :--- |
| **Core 0** | Infrastructure, BSW & Gateway | 300 MHz | `Task_5ms_Gateway`<br>`Task_10ms_Diag`<br>`Task_20ms_Body` | QM / ASIL B | {stats['core_distribution'].get('Core 0', 0)} | CAN-FD / Ethernet Routing, SecOC, UDS Diagnostics, Body Lighting |
| **Core 1** | Vehicle Motion & Chassis Control | 300 MHz Lockstep | `Task_1ms_Chassis`<br>`Task_5ms_Motion`<br>`Task_10ms_ESC` | **ASIL D** | {stats['core_distribution'].get('Core 1', 0)} | Steer-by-Wire (SbW), Brake-by-Wire (BbW), ESC, Active Rear Steer |
| **Core 2** | Electric Powertrain & Energy | 300 MHz Lockstep | `Task_1ms_Inverter`<br>`Task_10ms_Torque`<br>`Task_50ms_BMS` | **ASIL C / D** | {stats['core_distribution'].get('Core 2', 0)} | Dual Inverter FOC Vector Control, BMS Safety, Torque Vectoring |
| **Core 3** | ADAS & Active Safety | 400 MHz | `Task_10ms_ADAS`<br>`Task_20ms_Fusion`<br>`Task_50ms_Planner` | **ASIL B** | {stats['core_distribution'].get('Core 3', 0)} | ACC, AEB, Lane Centering, Track Fusion, Camera/Radar Arbitration |
| **HPC Cluster** | Cockpit & Autonomous Driving | 1.8 GHz Octa-Core | `Posix_App_Cockpit`<br>`Posix_App_Vision`<br>`ara::com SOME/IP` | QM / ASIL B | {stats['core_distribution'].get('HPC Core', 0)} | AR-HUD, Vision Deep Learning, Telematics 5G, FOTA Dual-Bank |

---

## 3. Freedom from Interference (FFI) & Safety Mechanisms (ISO 26262 Part 6)

1. **Memory Protection Unit (MPU) Partitioning:**
   - **ASIL D Partition:** Read/Write restricted to private OS memory stack; hardware register access strictly via trusted MCAL drivers.
   - **QM Partition Isolation:** Any boundary violation triggers an immediate MPU trap (`TRAP_MPU_ACCESS_VIOLATION`) causing core shutdown or safe limp-home reset without impacting adjacent ASIL D tasks.
2. **Watchdog Manager (WdgM) Multi-Level Supervision:**
   - **Alive Supervision:** Cyclically counts runnable invocation checkpoints (e.g. `10 ms ± 1 ms`).
   - **Deadline Supervision:** Verifies maximum execution latency between sensor capture and actuator command dispatch (`Latency <= 5 ms`).
   - **Logical Supervision (Program Flow):** Verifies deterministic graph transitions between state machine checkpoints using program counters.
3. **End-to-End (E2E) Communication Protection:**
   - Applied to all ASIL B through ASIL D Sender-Receiver interfaces via AUTOSAR E2E Profile 4 / Profile 7:
     - 4-bit Alive Counter (detects message drop and repetition).
     - 16-bit / 32-bit CRC calculation (detects hardware transmission bus bit corruption).
     - 16-bit Unique Data ID (detects message masquerading and routing errors).

---

## 4. Software Component Sample Design (Detailed Specification)

"""

for s in swc_list[:10]:
    ports_req_str = "\n".join([f"  - `{rp['name']}` ({rp['data_type']}, E2E: {rp['e2e_profile']})" for rp in s["ports_required"]]) or "  - *None (Independent Source)*"
    ports_prov_str = "\n".join([f"  - `{pp['name']}` ({pp['data_type']}, E2E: {pp['e2e_profile']})" for pp in s["ports_provided"]]) or "  - *None (Actuator Sink)*"
    runnables_str = "\n".join([f"  - `{r['name']}`: Period: {r['period']}, WCET: {r['wcet']}, Trigger: {r['trigger']}\n    *Logic:* {r['algorithm']}\n    *Safety:* {r['safety_mechanism']}" for r in s["runnables"]])
    
    arch_md += f"""### `{s['name']}` ({s['type']})
- **Parent Feature:** `{s['feature_id']}` ({s['feature_name']})
- **Domain:** {s['domain']} | **Target ASIL:** `{s['asil']}`
- **Multi-Core Target:** `{s['core']}` ({s['core_task']})
- **Memory Partition:** `{s['mpu_partition']}` ({s['mpu_privilege']})
- **Total WCET Budget:** `{s['total_wcet_ms']} ms`
- **Required Ports (`R-Ports`):**
{ports_req_str}
- **Provided Ports (`P-Ports`):**
{ports_prov_str}
- **Internal Runnables & Algorithmic Laws:**
{runnables_str}

---
"""

with open(os.path.join(BASE_DIR, "software_architecture.md"), "w", encoding="utf-8") as f:
    f.write(arch_md)

print("Saved software_architecture.md")

# Prepare JSON data for HTML application
swcs_json_data = json.dumps(swc_list, ensure_ascii=False)
stats_json_data = json.dumps(stats, ensure_ascii=False)

html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Automotive Software Architecture & Component Design Explorer</title>
  <meta name="description" content="Interactive AUTOSAR Classic & Adaptive Software Architecture, Component Design (SWE.2 / SWE.3), Port Interfaces & Multi-Core Task Allocation">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    :root {{
      --bg-primary: #070a12;
      --bg-secondary: #0c1222;
      --bg-surface: #151f38;
      --bg-surface-hover: #1e2c4f;
      --border-color: #27375e;
      --border-focus: #38bdf8;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;

      --accent-blue: #38bdf8;
      --accent-cyan: #06b6d4;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-purple: #a855f7;
      --accent-indigo: #6366f1;

      --asil-d-color: #ef4444;
      --asil-d-bg: rgba(239, 68, 68, 0.18);
      --asil-c-color: #f97316;
      --asil-c-bg: rgba(249, 115, 22, 0.18);
      --asil-b-color: #eab308;
      --asil-b-bg: rgba(234, 179, 8, 0.18);
      --asil-a-color: #38bdf8;
      --asil-a-bg: rgba(56, 189, 248, 0.18);
      --asil-qm-color: #94a3b8;
      --asil-qm-bg: rgba(148, 163, 184, 0.12);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      line-height: 1.5;
      min-height: 100vh;
      overflow-x: hidden;
    }}

    header.app-header {{
      background: linear-gradient(180deg, #0e172e 0%, rgba(12, 18, 34, 0.95) 100%);
      border-bottom: 1px solid var(--border-color);
      padding: 1.25rem 2rem;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(14px);
    }}

    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1rem;
    }}

    .brand-title-wrap {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, #4f46e5, #06b6d4);
      color: #fff;
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      font-size: 1.1rem;
      padding: 0.35rem 0.75rem;
      border-radius: 8px;
      box-shadow: 0 0 16px rgba(79, 70, 229, 0.4);
    }}

    h1.app-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.35rem;
      font-weight: 700;
      color: #ffffff;
    }}

    .app-subtitle {{
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-top: 0.15rem;
    }}

    .compliance-badges {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    .tag-badge {{
      font-size: 0.72rem;
      font-weight: 600;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-muted);
      text-decoration: none;
    }}

    .tag-badge:hover {{
      color: #ffffff;
      border-color: rgba(255, 255, 255, 0.3);
    }}

    .tag-badge.active-link {{
      background: rgba(56, 189, 248, 0.15);
      border-color: var(--accent-blue);
      color: var(--accent-blue);
    }}

    /* Global Metrics KPI Bar */
    .kpi-bar {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 0.75rem;
    }}

    .kpi-card {{
      background: rgba(21, 31, 56, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      padding: 0.65rem 0.85rem;
      display: flex;
      flex-direction: column;
      transition: all 0.2s ease;
    }}

    .kpi-card:hover {{
      border-color: rgba(56, 189, 248, 0.4);
      transform: translateY(-2px);
    }}

    .kpi-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      font-weight: 600;
      margin-bottom: 0.2rem;
    }}

    .kpi-value {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.35rem;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.1;
    }}

    .kpi-value.cyan {{ color: var(--accent-cyan); }}
    .kpi-value.emerald {{ color: var(--accent-emerald); }}
    .kpi-value.rose {{ color: var(--accent-rose); }}
    .kpi-value.amber {{ color: var(--accent-amber); }}
    .kpi-value.purple {{ color: var(--accent-purple); }}

    /* Main Container */
    main.app-main {{
      max-width: 1720px;
      margin: 0 auto;
      padding: 1.5rem 2rem;
    }}

    /* Architecture Layer Blueprint Navigator */
    .blueprint-panel {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }}

    .blueprint-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }}

    .blueprint-header h2 {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.15rem;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .layer-stack {{
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}

    .layer-card {{
      background: rgba(21, 31, 56, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      padding: 0.75rem 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .layer-card:hover {{
      background: rgba(30, 44, 79, 0.8);
      border-color: var(--accent-blue);
      transform: translateX(4px);
    }}

    .layer-card.active {{
      background: rgba(56, 189, 248, 0.15);
      border-color: var(--accent-blue);
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.2);
    }}

    .layer-name-wrap {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .layer-pill {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
      background: #1e3a8a;
      color: #93c5fd;
    }}

    .layer-title {{
      font-size: 0.92rem;
      font-weight: 600;
      color: #f1f5f9;
    }}

    .layer-desc {{
      font-size: 0.78rem;
      color: var(--text-muted);
    }}

    /* Filters Toolbar */
    .filters-panel {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.5rem;
    }}

    .filters-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1rem;
      margin-bottom: 1rem;
    }}

    .filter-group {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }}

    .filter-label {{
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}

    .search-input {{
      width: 100%;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      color: var(--text-main);
      padding: 0.6rem 0.85rem;
      font-size: 0.88rem;
      font-family: inherit;
    }}

    .search-input:focus {{
      outline: none;
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    }}

    select.filter-select {{
      width: 100%;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      color: var(--text-main);
      padding: 0.6rem 0.85rem;
      font-size: 0.88rem;
      font-family: inherit;
      cursor: pointer;
    }}

    .filter-pills-bar {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-top: 0.5rem;
    }}

    .filter-pill {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.76rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      font-family: 'JetBrains Mono', monospace;
    }}

    .filter-pill:hover {{
      background: var(--bg-surface-hover);
      color: #ffffff;
      border-color: #64748b;
    }}

    .filter-pill.active {{
      background: rgba(56, 189, 248, 0.2);
      color: var(--accent-blue);
      border-color: var(--accent-blue);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
    }}

    .view-controls-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
      padding-top: 1rem;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.4rem 0.85rem;
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid var(--border-color);
      background: var(--bg-surface);
      color: var(--text-main);
      transition: all 0.2s ease;
      font-family: inherit;
    }}

    .btn:hover {{ background: var(--bg-surface-hover); border-color: #64748b; }}
    .btn.active {{
      background: var(--accent-blue);
      color: #0b1120;
      border-color: var(--accent-blue);
    }}

    .btn-export {{
      color: var(--accent-emerald);
      border-color: rgba(16, 185, 129, 0.3);
      background: rgba(16, 185, 129, 0.08);
    }}

    .btn-reset {{
      color: var(--accent-rose);
      border-color: rgba(244, 63, 94, 0.3);
      background: rgba(244, 63, 94, 0.08);
    }}

    /* Component Cards Grid */
    .components-grid {{
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}

    .swc-card {{
      background: #0f162b;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3);
      transition: border-color 0.2s ease;
    }}

    .swc-card:hover {{ border-color: rgba(56, 189, 248, 0.4); }}

    .swc-header {{
      padding: 1rem 1.25rem;
      background: linear-gradient(90deg, #152243 0%, #0f162b 100%);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      cursor: pointer;
    }}

    .swc-header-left {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      flex: 1;
    }}

    .swc-badge-row {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    .id-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
    }}

    .id-badge.swc {{ background: #312e81; color: #c7d2fe; border: 1px solid #6366f1; }}

    .type-pill {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      font-weight: 600;
      background: rgba(6, 182, 212, 0.15);
      color: #22d3ee;
      border: 1px solid rgba(6, 182, 212, 0.35);
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
    }}

    .core-pill {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      font-weight: 600;
      background: rgba(168, 85, 247, 0.15);
      color: #c084fc;
      border: 1px solid rgba(168, 85, 247, 0.35);
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
    }}

    .badge-asil {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
    }}

    .badge-asil.d {{ background: var(--asil-d-bg); color: var(--asil-d-color); border: 1px solid var(--asil-d-color); }}
    .badge-asil.c {{ background: var(--asil-c-bg); color: var(--asil-c-color); border: 1px solid var(--asil-c-color); }}
    .badge-asil.b {{ background: var(--asil-b-bg); color: var(--asil-b-color); border: 1px solid var(--asil-b-color); }}
    .badge-asil.a {{ background: var(--asil-a-bg); color: var(--asil-a-color); border: 1px solid var(--asil-a-color); }}
    .badge-asil.qm {{ background: var(--asil-qm-bg); color: var(--asil-qm-color); border: 1px solid var(--asil-qm-color); }}

    h3.swc-title {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.05rem;
      font-weight: 700;
      color: #ffffff;
    }}

    .swc-meta-line {{
      font-size: 0.76rem;
      color: var(--text-dim);
    }}

    .swc-meta-line span {{ color: var(--text-muted); font-weight: 500; }}

    .swc-body {{ padding: 1.25rem; }}

    .swc-card.collapsed .swc-body {{ display: none; }}
    .swc-card.collapsed .accordion-arrow {{ transform: rotate(-90deg); }}

    .accordion-arrow {{
      color: var(--text-muted);
      font-size: 0.85rem;
      transition: transform 0.2s ease;
    }}

    /* Component Ports Matrix */
    .ports-section {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1rem;
      margin-bottom: 1.25rem;
    }}

    .port-column {{
      background: rgba(21, 31, 56, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 8px;
      padding: 0.85rem 1rem;
    }}

    .port-column-title {{
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 0.6rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .port-column-title.req {{ color: #38bdf8; }}
    .port-column-title.prov {{ color: #10b981; }}

    .port-item {{
      background: rgba(12, 18, 34, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.04);
      border-radius: 6px;
      padding: 0.45rem 0.65rem;
      margin-bottom: 0.4rem;
      font-size: 0.82rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .port-item-name {{
      font-family: 'JetBrains Mono', monospace;
      color: #e2e8f0;
      font-weight: 600;
    }}

    .port-item-type {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      color: var(--text-dim);
    }}

    .runnables-section {{
      border-top: 1px dashed rgba(255, 255, 255, 0.08);
      padding-top: 1rem;
      margin-top: 0.5rem;
    }}

    .runnables-title {{
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--accent-amber);
      margin-bottom: 0.75rem;
    }}

    .runnable-card {{
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 0.75rem 1rem;
      margin-bottom: 0.6rem;
    }}

    .runnable-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.35rem;
    }}

    .runnable-name {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      font-weight: 700;
      color: #f1f5f9;
    }}

    .runnable-timing {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      color: var(--accent-cyan);
    }}

    .runnable-algo {{
      font-size: 0.83rem;
      color: #94a3b8;
      line-height: 1.45;
    }}

    /* ARXML Modal */
    .arxml-modal {{
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(8px);
      display: none;
      justify-content: center;
      align-items: center;
      z-index: 1000;
    }}

    .arxml-dialog {{
      background: #0d1424;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      width: 90%;
      max-width: 900px;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
    }}

    .arxml-dialog-header {{
      padding: 1rem 1.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .arxml-dialog-body {{
      padding: 1.25rem 1.5rem;
      overflow-y: auto;
      flex: 1;
    }}

    .arxml-code-block {{
      background: #060913;
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 8px;
      padding: 1rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      color: #a5b4fc;
      white-space: pre-wrap;
      line-height: 1.5;
    }}

    /* Footer */
    footer.app-footer {{
      border-top: 1px solid var(--border-color);
      padding: 2rem;
      text-align: center;
      margin-top: 3rem;
      color: var(--text-dim);
      font-size: 0.8rem;
    }}
  </style>
</head>
<body>

  <!-- Top Header -->
  <header class="app-header">
    <div class="header-top">
      <div class="brand-title-wrap">
        <div class="logo-badge">AUTOSAR SWE.2 / SWE.3</div>
        <div>
          <h1 class="app-title">Automotive Software Architecture & Component Design Explorer</h1>
          <p class="app-subtitle">Layered AUTOSAR Architecture, VFB Interfaces, Multi-Core Allocation & Detailed Component Design</p>
        </div>
      </div>
      <div class="compliance-badges">
        <a href="requirements_traceability_matrix.html" class="tag-badge">📋 View Requirements Traceability Matrix</a>
        <span class="tag-badge active-link">🏗 Software Architecture (SWE.2 / SWE.3)</span>
        <span class="tag-badge">AUTOSAR Classic 4.4</span>
        <span class="tag-badge">Adaptive R20-11</span>
        <span class="tag-badge">ISO 26262 Part 6</span>
      </div>
    </div>

    <!-- Live KPI Summary Bar -->
    <div class="kpi-bar">
      <div class="kpi-card">
        <span class="kpi-label">Total AUTOSAR SWCs</span>
        <span class="kpi-value cyan" id="kpi-swcs-count">{stats['total_swcs']}</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Active Runnables</span>
        <span class="kpi-value emerald" id="kpi-runnables-count">{stats['total_runnables']}</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Required Ports (RPort)</span>
        <span class="kpi-value purple" id="kpi-rports-count">{stats['total_required_ports']}</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Provided Ports (PPort)</span>
        <span class="kpi-value amber" id="kpi-pports-count">{stats['total_provided_ports']}</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">ASIL D Safety SWCs</span>
        <span class="kpi-value rose" id="kpi-asild-count">{stats['asil_d_swcs']}</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Compute Targets</span>
        <span class="kpi-value">5 Cores</span>
      </div>
    </div>
  </header>

  <main class="app-main">
    <!-- AUTOSAR Architectural Blueprint Stack -->
    <section class="blueprint-panel">
      <div class="blueprint-header">
        <h2>🏗 AUTOSAR Layered Architecture Blueprint Stack</h2>
        <span style="font-size:0.8rem; color:var(--text-muted);">Click any architectural layer to filter components</span>
      </div>
      <div class="layer-stack">
        <div class="layer-card" onclick="filterByLayer('ApplicationSWC')">
          <div class="layer-name-wrap">
            <span class="layer-pill" style="background:#1e3a8a; color:#93c5fd;">LAYER 1</span>
            <div>
              <div class="layer-title">Application Layer (ApplicationSWC / SensorActuatorSWC / ServiceSupervisorSWC)</div>
              <div class="layer-desc">766 Component Types encapsulating Control Laws, State Machines, Sensor Fusion, and Actuator Coordinators</div>
            </div>
          </div>
          <span style="font-family:'JetBrains Mono',monospace; font-size:0.82rem; color:var(--accent-blue);">766 SWCs</span>
        </div>

        <div class="layer-card" onclick="alert('RTE Layer implements Virtual Functional Bus (VFB) contracts, 1:1 and 1:N Sender-Receiver communication, and E2E Profile 4/7 protection.')">
          <div class="layer-name-wrap">
            <span class="layer-pill" style="background:#065f46; color:#6ee7b7;">LAYER 2</span>
            <div>
              <div class="layer-title">Runtime Environment (RTE) / Virtual Functional Bus (VFB)</div>
              <div class="layer-desc">Decouples Software Components from Underlying Hardware; Manages Inter-Runnable Variables (IRVs) & E2E CRC Handshakes</div>
            </div>
          </div>
          <span style="font-family:'JetBrains Mono',monospace; font-size:0.82rem; color:var(--accent-emerald);">Contract & Generation</span>
        </div>

        <div class="layer-card" onclick="alert('Basic Software Services Layer: OS (Multi-core Tasks), DEM (Diagnostic Events & DTCs), WdgM (Watchdog Supervision), SecOC (Crypto MAC).')">
          <div class="layer-name-wrap">
            <span class="layer-pill" style="background:#701a75; color:#f0abfc;">LAYER 3</span>
            <div>
              <div class="layer-title">BSW Services Layer (OS, DEM, WdgM, SecOC, NvM, BswM, EcuM)</div>
              <div class="layer-desc">Multi-Core Task Scheduling, ISO 14229 UDS Diagnostics, Hardware Watchdog Management, and Secure Onboard Communication</div>
            </div>
          </div>
          <span style="font-family:'JetBrains Mono',monospace; font-size:0.82rem; color:var(--accent-purple);">System Services</span>
        </div>

        <div class="layer-card" onclick="alert('BSW ECU Abstraction & MCAL: IoHwAb, CanIf, EthIf, MCU, ADC, PWM, SPI Drivers directly interfacing microcontroller silicon.')">
          <div class="layer-name-wrap">
            <span class="layer-pill" style="background:#7c2d12; color:#fdba74;">LAYER 4</span>
            <div>
              <div class="layer-title">ECU Abstraction & MCAL Silicon Layer (IoHwAb, CanIf, EthIf, MCU, ADC, PWM, SPI)</div>
              <div class="layer-desc">Direct Silicon Register Abstraction for Infineon AURIX TC49x and ARM Cortex-R52 Real-Time Cores</div>
            </div>
          </div>
          <span style="font-family:'JetBrains Mono',monospace; font-size:0.82rem; color:var(--accent-amber);">Hardware Abstraction</span>
        </div>
      </div>
    </section>

    <!-- Filter Toolbar -->
    <section class="filters-panel">
      <div class="filters-grid">
        <div class="filter-group">
          <label class="filter-label" for="search-input">Search Components</label>
          <input type="text" id="search-input" class="search-input" placeholder="Search SWC name, runnable, signal, domain..." autocomplete="off">
        </div>

        <div class="filter-group">
          <label class="filter-label" for="domain-filter">Engineering Domain</label>
          <select id="domain-filter" class="filter-select">
            <option value="ALL">All Domains (6 Domains)</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label" for="type-filter">SWC Architectural Type</label>
          <select id="type-filter" class="filter-select">
            <option value="ALL">All SWC Types</option>
            <option value="ApplicationSWC">ApplicationSWC (Control Laws)</option>
            <option value="SensorActuatorSWC">SensorActuatorSWC (Sensors & Observers)</option>
            <option value="ActuatorSWC">ActuatorSWC (Actuation Drivers)</option>
            <option value="ServiceSupervisorSWC">ServiceSupervisorSWC (State Supervisors)</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label" for="core-filter">Multi-Core Allocation</label>
          <select id="core-filter" class="filter-select">
            <option value="ALL">All Compute Cores</option>
            <option value="Core 0">Core 0 (Gateway & BSW)</option>
            <option value="Core 1">Core 1 (Lockstep ASIL D Chassis)</option>
            <option value="Core 2">Core 2 (Lockstep ASIL C/D Powertrain)</option>
            <option value="Core 3">Core 3 (ASIL B ADAS)</option>
            <option value="HPC Core">HPC Cluster (ARM Cortex-A78)</option>
          </select>
        </div>
      </div>

      <!-- ASIL Filter Pills -->
      <div class="filter-pills-bar">
        <span style="font-size:0.75rem; color:var(--text-muted); font-weight:600; margin-right:0.25rem;">ASIL Integrity:</span>
        <button class="filter-pill active" data-asil="ALL">All ASILs</button>
        <button class="filter-pill" data-asil="ASIL D">ASIL D</button>
        <button class="filter-pill" data-asil="ASIL C">ASIL C</button>
        <button class="filter-pill" data-asil="ASIL B">ASIL B</button>
        <button class="filter-pill" data-asil="ASIL A">ASIL A</button>
        <button class="filter-pill" data-asil="QM">QM</button>
      </div>

      <div class="view-controls-bar">
        <span style="font-size:0.85rem; color:var(--text-muted);" id="results-count-text">Showing <b>766</b> Components</span>
        <div style="display:flex; gap:0.5rem;">
          <button id="toggle-expand-all" class="btn">⊟ Collapse All</button>
          <button id="btn-export-csv" class="btn btn-export">📥 Export SWC Catalog CSV</button>
          <button id="btn-reset" class="btn btn-reset">↺ Reset Filters</button>
        </div>
      </div>
    </section>

    <!-- Component Cards List -->
    <section class="components-grid" id="components-container">
      <!-- Rendered dynamically by JS -->
    </section>

    <!-- ARXML Dialog Modal -->
    <div id="arxml-modal" class="arxml-modal" onclick="closeArxmlModal(event)">
      <div class="arxml-dialog" onclick="event.stopPropagation()">
        <div class="arxml-dialog-header">
          <h3 id="arxml-modal-title" style="font-family:'Outfit',sans-serif; color:#ffffff;">AUTOSAR ARXML Component Descriptor</h3>
          <button class="btn" onclick="closeArxmlModal()">✕ Close</button>
        </div>
        <div class="arxml-dialog-body">
          <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.75rem;">Standard AUTOSAR Release 4.4.0 Software Component Description snippet:</p>
          <pre class="arxml-code-block" id="arxml-code-content"></pre>
        </div>
      </div>
    </div>
  </main>

  <footer class="app-footer">
    <p>Automotive Software Architecture & Component Design Explorer | ASPICE PAM v3.1 (SWE.2 & SWE.3) & ISO 26262:2018 (Part 6)</p>
    <p style="margin-top:0.4rem; color:#475569;">AUTOSAR Classic 4.4 / Adaptive Platform Architecture | Multi-Core AURIX TC49x & ARM Cortex-R52 Model</p>
  </footer>

  <script>
    const RAW_SWCS = {swcs_json_data};
    const STATS = {stats_json_data};

    let state = {{
      search: "",
      domain: "ALL",
      type: "ALL",
      core: "ALL",
      asil: "ALL",
      allExpanded: true
    }};

    const searchInput = document.getElementById("search-input");
    const domainFilter = document.getElementById("domain-filter");
    const typeFilter = document.getElementById("type-filter");
    const coreFilter = document.getElementById("core-filter");
    const resultsCountText = document.getElementById("results-count-text");
    const componentsContainer = document.getElementById("components-container");
    const toggleExpandAllBtn = document.getElementById("toggle-expand-all");
    const btnReset = document.getElementById("btn-reset");
    const btnExportCsv = document.getElementById("btn-export-csv");
    const arxmlModal = document.getElementById("arxml-modal");
    const arxmlModalTitle = document.getElementById("arxml-modal-title");
    const arxmlCodeContent = document.getElementById("arxml-code-content");

    function initFilters() {{
      const domains = Object.keys(STATS.domain_distribution).sort();
      domains.forEach(d => {{
        const opt = document.createElement("option");
        opt.value = d;
        opt.textContent = d;
        domainFilter.appendChild(opt);
      }});
    }}

    function getFilteredSWCs() {{
      const q = state.search.toLowerCase().trim();
      return RAW_SWCS.filter(s => {{
        if (state.domain !== "ALL" && s.domain !== state.domain) return false;
        if (state.type !== "ALL" && s.type !== state.type) return false;
        if (state.core !== "ALL" && s.core !== state.core) return false;
        if (state.asil !== "ALL" && !s.asil.toUpperCase().includes(state.asil.toUpperCase())) return false;

        if (q) {{
          const matchName = s.name.toLowerCase().includes(q);
          const matchFeature = s.feature_name.toLowerCase().includes(q) || s.feature_id.toLowerCase().includes(q);
          const matchSignal = s.ports_required.some(p => p.signal.toLowerCase().includes(q)) ||
                              s.ports_provided.some(p => p.signal.toLowerCase().includes(q));
          const matchRunnable = s.runnables.some(r => r.name.toLowerCase().includes(q) || r.algorithm.toLowerCase().includes(q));
          if (!matchName && !matchFeature && !matchSignal && !matchRunnable) return false;
        }}
        return true;
      }});
    }}

    function getAsilClass(asilStr) {{
      const s = (asilStr || "").toUpperCase();
      if (s.includes("ASIL D")) return "d";
      if (s.includes("ASIL C")) return "c";
      if (s.includes("ASIL B")) return "b";
      if (s.includes("ASIL A")) return "a";
      return "qm";
    }}

    function renderComponents() {{
      const filtered = getFilteredSWCs();
      resultsCountText.innerHTML = `Showing <b>${{filtered.length}}</b> of ${{RAW_SWCS.length}} Components`;

      if (filtered.length === 0) {{
        componentsContainer.innerHTML = `
          <div style="text-align:center; padding:3rem; background:var(--bg-secondary); border:1px dashed var(--border-color); border-radius:12px;">
            <p style="font-size:1.1rem; color:#ffffff; font-weight:600;">No matching software components found</p>
            <p style="font-size:0.85rem; color:var(--text-muted); margin-top:0.25rem;">Try adjusting search terms or clearing active filters.</p>
          </div>
        `;
        return;
      }}

      // Display up to 50 on initial page for extreme speed, with 'Load More' if needed
      const displayItems = filtered.slice(0, 100);

      const html = displayItems.map(s => {{
        const asilCls = getAsilClass(s.asil);
        const isCollapsed = !state.allExpanded;

        // Ports lists
        const rportsHtml = s.ports_required.length > 0 ? s.ports_required.map(p => `
          <div class="port-item">
            <span class="port-item-name">📥 ${{p.name}}</span>
            <span class="port-item-type">${{p.data_type}} | ${{p.e2e_profile}}</span>
          </div>
        `).join("") : `<div style="font-size:0.75rem; color:var(--text-dim); padding:0.4rem;">No upstream inputs (Independent Source)</div>`;

        const pportsHtml = s.ports_provided.length > 0 ? s.ports_provided.map(p => `
          <div class="port-item">
            <span class="port-item-name">📤 ${{p.name}}</span>
            <span class="port-item-type">${{p.data_type}} | ${{p.e2e_profile}}</span>
          </div>
        `).join("") : `<div style="font-size:0.75rem; color:var(--text-dim); padding:0.4rem;">No downstream outputs (Actuator Sink)</div>`;

        // Runnables
        const runnablesHtml = s.runnables.map(r => `
          <div class="runnable-card">
            <div class="runnable-header">
              <span class="runnable-name">⚡ ${{r.name}}</span>
              <span class="runnable-timing">Period: <b>${{r.period}}</b> | WCET: <b>${{r.wcet}}</b> | Stack: <b>${{r.stack_bytes}} B</b></span>
            </div>
            <div class="runnable-algo"><b>Algorithmic Law:</b> ${{r.algorithm}}</div>
            <div style="font-size:0.78rem; color:#cbd5e1; margin-top:0.35rem;"><b>Safety Gate:</b> ${{r.safety_mechanism}}</div>
          </div>
        `).join("");

        return `
          <article class="swc-card ${{isCollapsed ? 'collapsed' : ''}}" id="swc-${{s.name}}">
            <div class="swc-header" onclick="toggleCard('${{s.name}}')">
              <div class="swc-header-left">
                <div class="swc-badge-row">
                  <span class="id-badge swc">${{s.name}}</span>
                  <span class="type-pill">${{s.type}}</span>
                  <span class="core-pill">💻 ${{s.core}}</span>
                  <span class="badge-asil ${{asilCls}}">${{s.asil}}</span>
                  <span style="font-size:0.72rem; color:${{s.mpu_color}}; font-weight:700; background:rgba(255,255,255,0.05); padding:0.15rem 0.5rem; border-radius:4px;">${{s.mpu_partition}}</span>
                </div>
                <h3 class="swc-title">${{s.name}}</h3>
                <div class="swc-meta-line">
                  Feature: <span>${{s.feature_id}} (${{s.feature_name}})</span> • Domain: <span>${{s.domain}}</span> • Task: <span>${{s.core_task}}</span> • Total WCET: <span style="color:var(--accent-rose);">${{s.total_wcet_ms}} ms</span>
                </div>
              </div>
              <div style="display:flex; align-items:center; gap:0.75rem;">
                <button class="btn" style="padding:0.25rem 0.6rem; font-size:0.72rem;" onclick="event.stopPropagation(); viewArxml('${{s.name}}')">📜 View ARXML</button>
                <span class="accordion-arrow">▼</span>
              </div>
            </div>
            <div class="swc-body">
              <div class="ports-section">
                <div class="port-column">
                  <div class="port-column-title req">📥 Required Ports (R-Ports / Inbound Inputs) [${{s.ports_required.length}}]</div>
                  ${{rportsHtml}}
                </div>
                <div class="port-column">
                  <div class="port-column-title prov">📤 Provided Ports (P-Ports / Outbound Commands) [${{s.ports_provided.length}}]</div>
                  ${{pportsHtml}}
                </div>
              </div>
              <div class="runnables-section">
                <div class="runnables-title">⚡ AUTOSAR Periodic & Event-Triggered Runnables (${{s.runnables.length}})</div>
                ${{runnablesHtml}}
              </div>
            </div>
          </article>
        `;
      }}).join("");

      componentsContainer.innerHTML = html;
      if (filtered.length > 100) {{
        componentsContainer.innerHTML += `
          <div style="text-align:center; padding:1.5rem;">
            <p style="font-size:0.85rem; color:var(--text-muted);">Showing first 100 of ${{filtered.length}} components for maximum rendering speed. Narrow your search above to view specific components.</p>
          </div>
        `;
      }}
    }}

    window.toggleCard = function(swcName) {{
      const c = document.getElementById(`swc-${{swcName}}`);
      if (c) c.classList.toggle("collapsed");
    }};

    window.filterByLayer = function(type) {{
      state.type = type;
      typeFilter.value = type;
      renderComponents();
      componentsContainer.scrollIntoView({{ behavior: "smooth" }});
    }};

    window.viewArxml = function(swcName) {{
      const swc = RAW_SWCS.find(s => s.name === swcName);
      if (!swc) return;

      arxmlModalTitle.textContent = `AUTOSAR ARXML: ${{swc.name}} (${{swc.type}})`;

      const portsXml = [
        ...swc.ports_required.map(p => `          <R-PORT-PROTOTYPE>\n            <SHORT-NAME>${{p.name}}</SHORT-NAME>\n            <REQUIRED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">/Interfaces/${{p.signal}}_IF</REQUIRED-INTERFACE-TREF>\n          </R-PORT-PROTOTYPE>`),
        ...swc.ports_provided.map(p => `          <P-PORT-PROTOTYPE>\n            <SHORT-NAME>${{p.name}}</SHORT-NAME>\n            <PROVIDED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">/Interfaces/${{p.signal}}_IF</PROVIDED-INTERFACE-TREF>\n          </P-PORT-PROTOTYPE>`)
      ].join("\n");

      const runnablesXml = swc.runnables.map(r => `          <RUNNABLE-ENTITY>\n            <SHORT-NAME>${{r.name}}</SHORT-NAME>\n            <CAN-BE-INVOKED-CONCURRENTLY>false</CAN-BE-INVOKED-CONCURRENTLY>\n            <SYMBOL>${{r.name}}_func</SYMBOL>\n          </RUNNABLE-ENTITY>`).join("\n");

      const arxml = `<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-4-0.xsd">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>ComponentTypes</SHORT-NAME>
      <ELEMENTS>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>${{swc.name}}</SHORT-NAME>
          <CATEGORY>${{swc.type}}</CATEGORY>
          <PORTS>
${{portsXml}}
          </PORTS>
          <INTERNAL-BEHAVIORS>
            <SWC-INTERNAL-BEHAVIOR>
              <SHORT-NAME>${{swc.name}}_InternalBehavior</SHORT-NAME>
              <RUNNABLES>
${{runnablesXml}}
              </RUNNABLES>
            </SWC-INTERNAL-BEHAVIOR>
          </INTERNAL-BEHAVIORS>
        </APPLICATION-SW-COMPONENT-TYPE>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>`;

      arxmlCodeContent.textContent = arxml;
      arxmlModal.style.display = "flex";
    }};

    window.closeArxmlModal = function() {{
      arxmlModal.style.display = "none";
    }};

    // Event Listeners
    searchInput.addEventListener("input", (e) => {{
      state.search = e.target.value;
      renderComponents();
    }});

    domainFilter.addEventListener("change", (e) => {{
      state.domain = e.target.value;
      renderComponents();
    }});

    typeFilter.addEventListener("change", (e) => {{
      state.type = e.target.value;
      renderComponents();
    }});

    coreFilter.addEventListener("change", (e) => {{
      state.core = e.target.value;
      renderComponents();
    }});

    document.querySelectorAll(".filter-pill[data-asil]").forEach(pill => {{
      pill.addEventListener("click", () => {{
        document.querySelectorAll(".filter-pill[data-asil]").forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        state.asil = pill.dataset.asil;
        renderComponents();
      }});
    }});

    toggleExpandAllBtn.addEventListener("click", () => {{
      state.allExpanded = !state.allExpanded;
      toggleExpandAllBtn.textContent = state.allExpanded ? "⊟ Collapse All" : "⊞ Expand All";
      document.querySelectorAll(".swc-card").forEach(c => {{
        if (state.allExpanded) c.classList.remove("collapsed");
        else c.classList.add("collapsed");
      }});
    }});

    btnReset.addEventListener("click", () => {{
      state.search = "";
      state.domain = "ALL";
      state.type = "ALL";
      state.core = "ALL";
      state.asil = "ALL";

      searchInput.value = "";
      domainFilter.value = "ALL";
      typeFilter.value = "ALL";
      coreFilter.value = "ALL";

      document.querySelectorAll(".filter-pill[data-asil]").forEach(p => {{
        p.classList.toggle("active", p.dataset.asil === "ALL");
      }});

      renderComponents();
    }});

    btnExportCsv.addEventListener("click", () => {{
      const filtered = getFilteredSWCs();
      let csv = "Component Name,Type,Domain,Feature ID,ASIL,Multi-Core Target,MPU Partition,WCET ms,Required Ports,Provided Ports\\n";
      filtered.forEach(s => {{
        csv += `"${{s.name}}","${{s.type}}","${{s.domain}}","${{s.feature_id}}","${{s.asil}}","${{s.core}}","${{s.mpu_partition}}","${{s.total_wcet_ms}}","${{s.ports_required.length}}","${{s.ports_provided.length}}"\\n`;
      }});
      const blob = new Blob([csv], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `AUTOSAR_SWC_Catalog_${{new Date().toISOString().slice(0,10)}}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }});

    initFilters();
    renderComponents();
  </script>
</body>
</html>
"""

with open(os.path.join(BASE_DIR, "software_architecture_design.html"), "w", encoding="utf-8") as f:
    f.write(html_code)

print("Saved software_architecture_design.html successfully!")

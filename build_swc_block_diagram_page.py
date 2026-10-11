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
        return {"core": "Core 1", "desc": "Lockstep ASIL D Chassis Core", "color": "#ef4444"}
    elif 'powertrain' in d or 'power' in d:
        return {"core": "Core 2", "desc": "Lockstep ASIL C/D Powertrain Core", "color": "#f97316"}
    elif 'adas' in d:
        return {"core": "Core 3", "desc": "High-Performance ASIL B ADAS Core", "color": "#38bdf8"}
    elif 'body' in d:
        return {"core": "Core 0", "desc": "Body & Vehicle Infrastructure Core", "color": "#10b981"}
    elif 'cockpit' in d:
        return {"core": "HPC Core", "desc": "ARM Cortex-A78 HPC Application Cluster", "color": "#a855f7"}
    else:
        return {"core": "Core 0", "desc": "Gateway, Security & BSW Core", "color": "#06b6d4"}

# Build features data structure with their SWC pipelines and mermaid diagrams
features_data = []

for f in all_features:
    f_id = f["id"]
    f_name = f["name"]
    domain = f["domain"]
    f_asil = f["asil"]
    
    feature_swcs = []
    seen_swc_names = set()
    
    for sw in f.get("sw_reqs", []):
        swc_name = sw.get("swc", "Generic_SWC")
        if swc_name not in seen_swc_names:
            seen_swc_names.add(swc_name)
            
            swc_type = determine_swc_type(swc_name)
            core_info = determine_core_allocation(domain, sw.get("asil", f_asil))
            
            raw_in = sw.get("inputs", "")
            raw_out = sw.get("outputs", "")
            
            in_signals = [x.strip().replace("`", "") for x in raw_in.split(",") if x.strip()]
            out_signals = [x.strip().replace("`", "") for x in raw_out.split(",") if x.strip()]
            
            feature_swcs.append({
                "name": swc_name,
                "type": swc_type,
                "period": sw.get("period", "10 ms"),
                "wcet": sw.get("wcet", "0.5 ms"),
                "asil": sw.get("asil", f_asil),
                "core": core_info["core"],
                "core_color": core_info["color"],
                "in_signals": in_signals,
                "out_signals": out_signals,
                "algorithm": sw.get("algorithm", "Deterministic processing."),
                "safety_mechanism": sw.get("safety_mechanism", "Plausibility monitoring.")
            })
            
    def clean_signal_label(raw: str) -> str:
        if not raw:
            return "RTE Bus"
        # Remove array indexing like [16] or [0..3]
        s = re.sub(r'\[.*?\]', '', raw)
        # Remove characters that violate Mermaid edge/node grammar
        s = re.sub(r'[\[\]{}()|"<>\'`:,;*&%#\\]', '', s)
        s = s.strip()
        if not s:
            return "RTE Bus"
        tokens = s.split()
        chosen = tokens[0] if tokens else "RTE Bus"
        chosen = chosen[:22].rstrip('_')
        return chosen if chosen else "RTE Bus"

    mermaid_lines = [
        "graph LR",
        "    classDef sensor fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff;",
        "    classDef app fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff;",
        "    classDef supervisor fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#fff;",
        "    classDef actuator fill:#4c0519,stroke:#f43f5e,stroke-width:2px,color:#fff;",
        "    classDef bsw fill:#3b0764,stroke:#a855f7,stroke-width:2px,color:#fff;",
        "    classDef ext fill:#111827,stroke:#64748b,stroke-width:1px,stroke-dasharray: 4 4,color:#cbd5e1;"
    ]
    
    first_swc = feature_swcs[0] if feature_swcs else None
    last_swc = feature_swcs[-1] if feature_swcs else None
    
    mermaid_lines.append('    InboundSensors["Physical Sensors / Bus In<br/>SENT / ADC / CAN-FD"]:::ext')
    mermaid_lines.append('    OutboundActuators["Physical Actuators / Output Stage<br/>H-Bridge / PWM / Inverter"]:::ext')
    mermaid_lines.append('    DEM["AUTOSAR DEM / DTC Logger<br/>Diagnostic Event Manager"]:::bsw')
    
    for idx, s in enumerate(feature_swcs):
        node_id = f"SWC_{idx}"
        clean_name = re.sub(r'[\[\]{}()|"<>\'`]', '', s['name'])
        clean_period = re.sub(r'[\[\]{}()|"<>\'`]', '', s['period'])
        clean_asil = re.sub(r'[\[\]{}()|"<>\'`]', '', s['asil'])
        label = f"<b>{clean_name}</b><br/><small>{clean_period} - {clean_asil}</small>"
        cls_name = "app"
        if s["type"] == "SensorActuatorSWC": cls_name = "sensor"
        elif s["type"] == "ServiceSupervisorSWC": cls_name = "supervisor"
        elif s["type"] == "ActuatorSWC": cls_name = "actuator"
        
        mermaid_lines.append(f'    {node_id}["{label}"]:::{cls_name}')
        
    if feature_swcs:
        mermaid_lines.append('    InboundSensors -->|Raw Sensor Stream| SWC_0')
        
        for idx in range(len(feature_swcs) - 1):
            s_curr = feature_swcs[idx]
            s_next = feature_swcs[idx + 1]
            
            sig_label = "RTE S/R Bus"
            if s_curr["out_signals"]:
                sig_label = clean_signal_label(s_curr["out_signals"][0])
            elif s_next["in_signals"]:
                sig_label = clean_signal_label(s_next["in_signals"][0])
                
            mermaid_lines.append(f'    SWC_{idx} -->|{sig_label}| SWC_{idx+1}')
            
        last_idx = len(feature_swcs) - 1
        mermaid_lines.append(f'    SWC_{last_idx} -->|Command Duty Cycle| OutboundActuators')
        
        sup_idx = next((i for i, s in enumerate(feature_swcs) if s["type"] == "ServiceSupervisorSWC"), None)
        if sup_idx is not None:
            mermaid_lines.append(f'    SWC_{sup_idx} -.->|Fault Event| DEM')
        else:
            mermaid_lines.append(f'    SWC_{last_idx} -.->|Fault Event| DEM')
            
    feature_mermaid = "\n".join(mermaid_lines)
    
    features_data.append({
        "id": f_id,
        "name": f_name,
        "domain": domain,
        "asil": f_asil,
        "swcs": feature_swcs,
        "mermaid_diagram": feature_mermaid
    })

print(f"Processed {len(features_data)} features with complete SWC block diagrams.")

global_mermaid = """graph TD
    classDef domain fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff;
    classDef vfb fill:#0f172a,stroke:#38bdf8,stroke-width:3px,color:#38bdf8;
    classDef bsw fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#fff;
    classDef hw fill:#18181b,stroke:#71717a,stroke-width:1px,stroke-dasharray: 4 4,color:#e4e4e7;

    Sensors["Physical Sensors & Input Feeds<br/>Camera, Radar, LiDAR, Ultrasonic<br/>Wheel Speed, Steering Angle, IMU<br/>Battery Cell Voltages, Brake Pressure"]:::hw

    subgraph VFB["Virtual Functional Bus (VFB) / Runtime Environment (RTE) Backbone"]
        direction TB
        DOM_ADAS["Domain 1: ADAS & Autonomous Driving<br/>AccTargetFusion, AebCrashPlanner, LcaCentering<br/>Core 3 (400 MHz) - ASIL B"]:::domain
        DOM_CHS["Domain 2: Vehicle Motion & Chassis Control<br/>SbW Handwheel/Rack, BbW Decel, ESC Dynamics<br/>Core 1 Lockstep (300 MHz) - ASIL D"]:::domain
        DOM_PWR["Domain 3: Electric Powertrain & Energy<br/>Dual Inverter FOC, BMS Isolation, Torque Vectoring<br/>Core 2 Lockstep (300 MHz) - ASIL C/D"]:::domain
        DOM_BDY["Domain 4: Body, Lighting & Restraints<br/>PEPS UWB, Matrix LED, Airbag SRS, Heat Pump<br/>Core 0 (300 MHz) - ASIL B/D"]:::domain
        DOM_CPT["Domain 5: Digital Cockpit & Cabin Sensing<br/>Driver Monitoring (DMS), AR-HUD, AVAS Sound<br/>HPC Cortex-A78 Cluster - QM/ASIL B"]:::domain
        DOM_CONN["Domain 6: Connectivity, Security & Diagnostics<br/>5G Telematics, SecOC Crypto, FOTA, UDS DEM<br/>Core 0 Gateway & HSM - ASIL B/QM"]:::domain
    end

    subgraph BSW_STACK["AUTOSAR Basic Software (BSW) & Safety Core"]
        direction LR
        OS["Multi-Core OS<br/>(OSEK/VDX Tasks)"]:::bsw
        DEM["Diagnostic Event Mgr<br/>(DEM / DTC Storage)"]:::bsw
        WDGM["Watchdog Mgr<br/>(WdgM / Alive/Deadline)"]:::bsw
        SECOC["Secure Onboard Com<br/>(SecOC / AES-128 MAC)"]:::bsw
        MCAL["MCAL Drivers<br/>(ADC, PWM, CAN, ETH)"]:::bsw
    end

    Actuators["Vehicle Actuators & Hardware Power Stages<br/>Dual Permanent Magnet Traction Inverters<br/>Steer-by-Wire Dual Rack Motors<br/>Brake-by-Wire Electro-Hydraulic Plungers<br/>Matrix LED Headlamp Drivers & Squibs"]:::hw

    Sensors -->|Raw SENT/ADC/CAN-FD| DOM_ADAS
    Sensors -->|Chassis Dynamics Sensors| DOM_CHS
    Sensors -->|Battery & Phase Telemetry| DOM_PWR
    DOM_ADAS <-->|Trajectory & Target Accel| DOM_CHS
    DOM_CHS <-->|Torque & Regenerative Split| DOM_PWR
    DOM_PWR <-->|Power Limits & HV Interlocks| DOM_BDY
    DOM_CONN <-->|SecOC Protected Bus Frames| DOM_ADAS
    DOM_CHS -->|Steering & Braking Setpoints| Actuators
    DOM_PWR -->|Inverter Phase Current Vectors| Actuators
    DOM_BDY -->|Solid-State Relay Drives| Actuators
    VFB <-->|RTE Service Ports| BSW_STACK
"""

features_json_str = json.dumps(features_data, ensure_ascii=False)

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AUTOSAR SWC Architecture Block Diagram Explorer</title>
  <meta name="description" content="Single-Page Interactive Automotive Software Component (SWC) Architecture Block Diagram Explorer with Live Mermaid Rendering, Port Data Flow, and Component Inspection">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    :root {
      --bg-primary: #070a12;
      --bg-secondary: #0c1222;
      --bg-surface: #141e36;
      --bg-surface-hover: #1e2c4f;
      --border-color: #26365b;
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
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      line-height: 1.5;
      min-height: 100vh;
      overflow-x: hidden;
    }

    header.app-header {
      background: linear-gradient(180deg, #0e172e 0%, rgba(12, 18, 34, 0.95) 100%);
      border-bottom: 1px solid var(--border-color);
      padding: 1.15rem 2rem;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(14px);
    }

    .header-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .brand-title-wrap {
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }

    .logo-badge {
      background: linear-gradient(135deg, #2563eb, #38bdf8);
      color: #fff;
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      font-size: 1.1rem;
      padding: 0.35rem 0.75rem;
      border-radius: 8px;
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.4);
    }

    h1.app-title {
      font-family: 'Outfit', sans-serif;
      font-size: 1.35rem;
      font-weight: 700;
      color: #ffffff;
    }

    .app-subtitle {
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-top: 0.15rem;
    }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }

    .nav-btn {
      font-size: 0.76rem;
      font-weight: 600;
      padding: 0.3rem 0.7rem;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      background: var(--bg-surface);
      color: var(--text-muted);
      text-decoration: none;
      transition: all 0.2s ease;
    }

    .nav-btn:hover {
      color: #ffffff;
      border-color: #64748b;
    }

    .nav-btn.active {
      background: rgba(56, 189, 248, 0.15);
      border-color: var(--accent-blue);
      color: var(--accent-blue);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
    }

    main.app-main {
      max-width: 1720px;
      margin: 0 auto;
      padding: 1.25rem 2rem;
    }

    .controls-panel {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1rem 1.25rem;
      margin-bottom: 1.25rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .controls-left {
      display: flex;
      align-items: center;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .mode-pills {
      display: flex;
      background: var(--bg-surface);
      padding: 0.25rem;
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }

    .mode-pill-btn {
      padding: 0.35rem 0.85rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 600;
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .mode-pill-btn.active {
      background: var(--accent-blue);
      color: #090e1a;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }

    .feature-selector-wrap {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    select.feature-select {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      color: #ffffff;
      padding: 0.45rem 0.85rem;
      border-radius: 8px;
      font-size: 0.85rem;
      font-family: inherit;
      cursor: pointer;
      min-width: 320px;
    }

    .controls-right {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .btn {
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
    }

    .btn:hover { background: var(--bg-surface-hover); border-color: #64748b; }

    .diagram-stage-container {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.5rem;
      min-height: 550px;
      position: relative;
      overflow-x: auto;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    }

    .stage-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stage-title {
      font-family: 'Outfit', sans-serif;
      font-size: 1.15rem;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .legend-bar {
      display: flex;
      align-items: center;
      gap: 0.85rem;
      flex-wrap: wrap;
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }

    .legend-dot {
      width: 10px;
      height: 10px;
      border-radius: 3px;
    }

    .diagram-render-area {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      min-height: 480px;
      background: #090d18;
      border: 1px solid rgba(255, 255, 255, 0.04);
      border-radius: 8px;
      padding: 1.5rem;
      overflow-x: auto;
    }

    .swc-details-grid {
      margin-top: 1.5rem;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1rem;
    }

    .swc-block-card {
      background: rgba(20, 30, 54, 0.6);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 0.85rem 1rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .swc-block-card:hover {
      background: rgba(30, 44, 79, 0.8);
      border-color: var(--accent-blue);
      transform: translateY(-2px);
    }

    .swc-card-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.4rem;
    }

    .swc-name {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      font-weight: 700;
      color: #ffffff;
    }

    .swc-badge {
      font-size: 0.68rem;
      font-weight: 700;
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      font-family: 'JetBrains Mono', monospace;
    }

    .swc-signals-list {
      font-size: 0.76rem;
      color: var(--text-muted);
      margin-top: 0.4rem;
    }

    .swc-signals-list b { color: #e2e8f0; }

    .modal-overlay {
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(8px);
      display: none;
      justify-content: center;
      align-items: center;
      z-index: 1000;
    }

    .modal-dialog {
      background: #0d1424;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      width: 90%;
      max-width: 850px;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
    }

    .modal-header {
      padding: 1rem 1.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .modal-body {
      padding: 1.25rem 1.5rem;
      overflow-y: auto;
      flex: 1;
    }

    footer.app-footer {
      border-top: 1px solid var(--border-color);
      padding: 2rem;
      text-align: center;
      margin-top: 3rem;
      color: var(--text-dim);
      font-size: 0.8rem;
    }
  </style>
</head>
<body>

  <!-- Top Navigation Header -->
  <header class="app-header">
    <div class="header-top">
      <div class="brand-title-wrap">
        <div class="logo-badge">AUTOSAR VFB</div>
        <div>
          <h1 class="app-title">SWC Architecture Block Diagram Explorer</h1>
          <p class="app-subtitle">Interactive AUTOSAR Software Component Architecture, Virtual Functional Bus Interconnections & Data Flow</p>
        </div>
      </div>
      <div class="nav-links">
        <a href="requirements_traceability_matrix.html" class="nav-btn">📋 Requirements Traceability Matrix</a>
        <a href="software_architecture_design.html" class="nav-btn">🧩 Component Catalog & ARXML</a>
        <a href="swc_architecture_block_diagram.html" class="nav-btn active">📊 Architecture Block Diagram (One-Page)</a>
      </div>
    </div>
  </header>

  <main class="app-main">
    <!-- Controls Toolbar -->
    <section class="controls-panel">
      <div class="controls-left">
        <div class="mode-pills">
          <button class="mode-pill-btn active" id="mode-feature-btn" onclick="switchScopeMode('feature')">🔍 Feature-Level SWC Pipeline</button>
          <button class="mode-pill-btn" id="mode-platform-btn" onclick="switchScopeMode('platform')">🌐 Full SDV Platform VFB Backbone</button>
        </div>

        <div class="feature-selector-wrap" id="feature-selector-wrap">
          <label for="feature-select" style="font-size:0.78rem; font-weight:600; color:var(--text-muted);">Select Vehicle Feature:</label>
          <select id="feature-select" class="feature-select" onchange="onFeatureSelected(this.value)">
          </select>
        </div>
      </div>

      <div class="controls-right">
        <button class="btn" onclick="exportDiagramSource()">📜 View Mermaid Code</button>
        <button class="btn" onclick="toggleFullscreen()">⛶ Fullscreen</button>
      </div>
    </section>

    <!-- Diagram Canvas Stage -->
    <section class="diagram-stage-container" id="diagram-stage">
      <div class="stage-header">
        <div class="stage-title" id="stage-title">
          <span>⚡ FEAT-ADAS-01: Adaptive Cruise Control with Stop & Go (ACC)</span>
        </div>
        <div class="legend-bar">
          <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div> Sensor SWC</div>
          <div class="legend-item"><div class="legend-dot" style="background:#3b82f6;"></div> Core Algorithm SWC</div>
          <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div> State Supervisor</div>
          <div class="legend-item"><div class="legend-dot" style="background:#f43f5e;"></div> Actuator Driver</div>
          <div class="legend-item"><div class="legend-dot" style="background:#a855f7;"></div> Basic Software (BSW / DEM)</div>
        </div>
      </div>

      <div class="diagram-render-area" id="diagram-render-area">
        <div id="mermaid-target"></div>
      </div>

      <div id="feature-swc-details-area">
        <h3 style="font-family:'Outfit',sans-serif; font-size:1rem; color:#ffffff; margin: 1.5rem 0 0.75rem 0;">🧩 Pipeline Component Inspector (Click any card to inspect interface specifications):</h3>
        <div class="swc-details-grid" id="swc-cards-grid">
        </div>
      </div>
    </section>

    <!-- Modal -->
    <div id="inspector-modal" class="modal-overlay" onclick="closeModal()">
      <div class="modal-dialog" onclick="event.stopPropagation()">
        <div class="modal-header">
          <h3 id="modal-title" style="font-family:'Outfit',sans-serif; color:#ffffff;">Component Specification</h3>
          <button class="btn" onclick="closeModal()">✕ Close</button>
        </div>
        <div class="modal-body" id="modal-body">
        </div>
      </div>
    </div>
  </main>

  <footer class="app-footer">
    <p>AUTOSAR SWC Architecture Block Diagram Explorer | ASPICE PAM v3.1 (SWE.2 & SWE.3) & ISO 26262:2018 Part 6</p>
    <p style="margin-top:0.4rem; color:#475569;">Interactive Virtual Functional Bus (VFB) Data Flow Modeling | 40 Features & 766 AUTOSAR Software Components</p>
  </footer>

  <script>
    const FEATURES = __FEATURES_JSON__;
    const GLOBAL_MERMAID = `__GLOBAL_MERMAID__`;

    let currentMode = "feature";
    let selectedFeatureId = "FEAT-ADAS-01";

    if (window.mermaid) {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        securityLevel: 'loose',
        themeVariables: {
          darkMode: true,
          background: '#090d18',
          primaryColor: '#1e3a8a',
          primaryTextColor: '#f8fafc',
          primaryBorderColor: '#38bdf8',
          lineColor: '#38bdf8',
          secondaryColor: '#1e293b',
          tertiaryColor: '#111827'
        }
      });
    }

    function initFeatureSelector() {
      const select = document.getElementById("feature-select");
      select.innerHTML = "";
      FEATURES.forEach(f => {
        const opt = document.createElement("option");
        opt.value = f.id;
        opt.textContent = f.id + ": " + f.name + " (" + f.domain + ")";
        select.appendChild(opt);
      });
    }

    function switchScopeMode(mode) {
      currentMode = mode;
      document.getElementById("mode-feature-btn").classList.toggle("active", mode === "feature");
      document.getElementById("mode-platform-btn").classList.toggle("active", mode === "platform");
      document.getElementById("feature-selector-wrap").style.display = mode === "feature" ? "flex" : "none";
      document.getElementById("feature-swc-details-area").style.display = mode === "feature" ? "block" : "none";

      renderDiagram();
    }

    function onFeatureSelected(featId) {
      selectedFeatureId = featId;
      renderDiagram();
    }

    function renderDiagram() {
      const renderArea = document.getElementById("diagram-render-area");
      const stageTitle = document.getElementById("stage-title");
      const uniqueId = "mermaid-canvas-" + Date.now();

      let diagramCode = "";

      if (currentMode === "feature") {
        const feat = FEATURES.find(f => f.id === selectedFeatureId) || FEATURES[0];
        stageTitle.innerHTML = "<span>⚡ " + feat.id + ": " + feat.name + "</span> <span style='font-size:0.8rem; color:var(--text-muted); font-weight:normal;'>(" + feat.domain + " | Target ASIL: " + feat.asil + ")</span>";
        diagramCode = feat.mermaid_diagram;
        renderSWCCards(feat.swcs);
      } else {
        stageTitle.innerHTML = "<span>🌐 Full Software-Defined Vehicle (SDV) Virtual Functional Bus (VFB) Architecture</span>";
        diagramCode = GLOBAL_MERMAID;
      }

      renderArea.innerHTML = '<div style="color:var(--text-muted); font-size:0.85rem; padding:2rem; text-align:center;">Rendering SWC Architecture Pipeline...</div>';

      if (window.mermaid) {
        const renderId = "mermaid_svg_" + Math.random().toString(36).substring(2, 11);
        mermaid.render(renderId, diagramCode).then(res => {
          renderArea.innerHTML = res.svg;
          if (res.bindFunctions) res.bindFunctions(renderArea);
        }).catch(err => {
          console.warn("Mermaid async render error, using fallback:", err);
          renderArea.innerHTML = '<pre class="mermaid" id="' + uniqueId + '">' + diagramCode + '</pre>';
          try {
            mermaid.run({ nodes: [document.getElementById(uniqueId)] });
          } catch(e) {
            console.error("Mermaid fallback run error:", e);
          }
        });
      } else {
        renderArea.innerHTML = '<pre class="mermaid" id="' + uniqueId + '">' + diagramCode + '</pre>';
      }
    }

    function renderSWCCards(swcs) {
      const grid = document.getElementById("swc-cards-grid");
      if (!swcs || swcs.length === 0) {
        grid.innerHTML = "<p style='color:var(--text-muted);'>No SWC blocks available.</p>";
        return;
      }

      grid.innerHTML = swcs.map(s => `
        <div class="swc-block-card" onclick="inspectComponent('${s.name}')">
          <div class="swc-card-top">
            <span class="swc-name">${s.name}</span>
            <span class="swc-badge" style="background:rgba(56,189,248,0.15); color:var(--accent-blue);">${s.type}</span>
          </div>
          <div style="font-size:0.75rem; color:var(--text-dim);">
            Rate: <b style="color:#ffffff;">${s.period}</b> | WCET: <b style="color:var(--accent-rose);">${s.wcet}</b> | Core: <b style="color:${s.core_color};">${s.core}</b>
          </div>
          <div class="swc-signals-list">
            <div>📥 In: <b>${s.in_signals.slice(0, 2).join(", ") || "Physical Driver"}</b></div>
            <div>📤 Out: <b>${s.out_signals.slice(0, 2).join(", ") || "Actuator Command"}</b></div>
          </div>
        </div>
      `).join("");
    }

    window.inspectComponent = function(swcName) {
      const feat = FEATURES.find(f => f.id === selectedFeatureId);
      if (!feat) return;
      const swc = feat.swcs.find(s => s.name === swcName);
      if (!swc) return;

      document.getElementById("modal-title").textContent = "Component Inspection: " + swc.name + " (" + swc.type + ")";
      document.getElementById("modal-body").innerHTML = `
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:0.75rem; margin-bottom:1rem; background:rgba(21,31,56,0.6); padding:0.85rem; border-radius:8px;">
          <div><span style="font-size:0.7rem; color:var(--text-dim); text-transform:uppercase;">Execution Rate</span><div style="font-weight:700; color:#fff;">${swc.period}</div></div>
          <div><span style="font-size:0.7rem; color:var(--text-dim); text-transform:uppercase;">WCET Budget</span><div style="font-weight:700; color:var(--accent-rose);">${swc.wcet}</div></div>
          <div><span style="font-size:0.7rem; color:var(--text-dim); text-transform:uppercase;">Safety Rating</span><div style="font-weight:700; color:var(--accent-amber);">${swc.asil}</div></div>
          <div><span style="font-size:0.7rem; color:var(--text-dim); text-transform:uppercase;">Target Core</span><div style="font-weight:700; color:var(--accent-cyan);">${swc.core}</div></div>
        </div>

        <div style="margin-bottom:1rem;">
          <h4 style="font-size:0.85rem; color:var(--accent-blue); margin-bottom:0.35rem;">📥 Inbound Required Ports (R-Ports):</h4>
          <div style="background:#090d18; padding:0.6rem; border-radius:6px; font-family:'JetBrains Mono',monospace; font-size:0.8rem; color:#cbd5e1;">
            ${swc.in_signals.map(s => `<div>• ${s}</div>`).join("") || "None"}
          </div>
        </div>

        <div style="margin-bottom:1rem;">
          <h4 style="font-size:0.85rem; color:var(--accent-emerald); margin-bottom:0.35rem;">📤 Outbound Provided Ports (P-Ports):</h4>
          <div style="background:#090d18; padding:0.6rem; border-radius:6px; font-family:'JetBrains Mono',monospace; font-size:0.8rem; color:#cbd5e1;">
            ${swc.out_signals.map(s => `<div>• ${s}</div>`).join("") || "None"}
          </div>
        </div>

        <div style="margin-bottom:1rem;">
          <h4 style="font-size:0.85rem; color:#f1f5f9; margin-bottom:0.35rem;">⚡ Algorithmic Logic & Mathematical Law:</h4>
          <div style="background:#090d18; padding:0.6rem; border-radius:6px; font-size:0.83rem; color:#94a3b8; line-height:1.45;">
            ${swc.algorithm}
          </div>
        </div>

        <div>
          <h4 style="font-size:0.85rem; color:var(--accent-rose); margin-bottom:0.35rem;">🛡 Safety Gatekeeper & Plausibility Bounds:</h4>
          <div style="background:#090d18; padding:0.6rem; border-radius:6px; font-size:0.83rem; color:#94a3b8; line-height:1.45;">
            ${swc.safety_mechanism}
          </div>
        </div>
      `;
      document.getElementById("inspector-modal").style.display = "flex";
    };

    window.closeModal = function() {
      document.getElementById("inspector-modal").style.display = "none";
    };

    window.exportDiagramSource = function() {
      const feat = FEATURES.find(f => f.id === selectedFeatureId);
      const code = currentMode === "feature" ? feat.mermaid_diagram : GLOBAL_MERMAID;
      document.getElementById("modal-title").textContent = "Mermaid Diagram Source Code";
      document.getElementById("modal-body").innerHTML = `
        <pre style="background:#060913; padding:1rem; border-radius:8px; font-family:'JetBrains Mono',monospace; font-size:0.8rem; color:#a5b4fc; white-space:pre-wrap;">${code}</pre>
      `;
      document.getElementById("inspector-modal").style.display = "flex";
    };

    window.toggleFullscreen = function() {
      const stage = document.getElementById("diagram-stage");
      if (!document.fullscreenElement) {
        stage.requestFullscreen().catch(err => alert("Fullscreen error: " + err.message));
      } else {
        document.exitFullscreen();
      }
    };

    initFeatureSelector();
    renderDiagram();
  </script>
</body>
</html>
"""

html_final = html_template.replace("__FEATURES_JSON__", features_json_str).replace("__GLOBAL_MERMAID__", global_mermaid)

output_path = os.path.join(BASE_DIR, "swc_architecture_block_diagram.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_final)

print(f"Single-page SWC Architecture Block Diagram Explorer saved at: {output_path}")
print(f"File size: {round(os.path.getsize(output_path) / 1024, 1)} KB")

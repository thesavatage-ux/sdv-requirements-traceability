# -*- coding: utf-8 -*-
import features_chs_full
import pprint

# 1. Update FEAT-CHS-01 from expand_domain_chs_mass
import expand_domain_chs_mass
expand_domain_chs_mass.expand_chs()

# 2. Update FEAT-CHS-02 with the 20 SYS and 50 SWR
import generate_sbw_sysreq
# We will load the 20 SYS and 50 SWR for SbW
from build_full_swreq_entries import swr_list

feats = {f["id"]: f for f in features_chs_full.full_chs_features}
f2 = feats["FEAT-CHS-02"]

# We have 20 SYS for SbW in FEAT-CHS-02_SbW_SysReq.md
# Let's inspect them or parse them from FEAT-CHS-02_SbW_SysReq.md
import re
with open(r"c:\Workset\AntiGravityProjects\TestOptimisationExperiement\system_requirements\FEAT-CHS-02_SbW_SysReq.md", "r", encoding="utf-8") as f:
    text = f.read()

# Parse the table in FEAT-CHS-02_SbW_SysReq.md
# Schema: | SysReq ID | Requirement Description | Operational Mode / Trigger | Performance & Timing Threshold | Functional Safety (ASIL) | Target Allocation |
sys_table_matches = re.findall(r'\|\s*`(SYS-CHS-02-\d+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|', text)

f2["sys_reqs"] = []
for m in sys_table_matches:
    s_id, desc, mode, thresh, asil, alloc = [x.strip() for x in m]
    # find child SWRs in swr_list
    children = [s["id"] for s in swr_list if s["parent"] == s_id]
    f2["sys_reqs"].append({
        "id": s_id,
        "title": desc.split(" across ")[0].split(" with ")[0],
        "asil": asil,
        "statement": f"The System SHALL {desc}.",
        "activation": mode,
        "ftti": thresh.split(";")[0],
        "safe_state": "Secondary redundant motor takes over or graceful safe-stop executed.",
        "failure_reaction": "Isolate channel within FTTI and log DEM diagnostic trouble code.",
        "inputs": "Sensor signals and bus inputs via RTE.",
        "outputs": "Inverter PWM duty cycles, feedback torque, and diagnostic flags.",
        "verification": "HiL bench testing and hardware dynamometer validation.",
        "downstream": children
    })

f2["sw_reqs"] = []
for s in swr_list:
    f2["sw_reqs"].append({
        "id": s["id"],
        "title": s.get("title", s["statement"][:60]),
        "parent": s["parent"],
        "asil": s["asil"],
        "swc": s["swc"],
        "period": s["runnable"].split("@")[-1].strip(),
        "wcet": "0.35 ms",
        "activation": f"Executed cyclically every {s['runnable'].split('@')[-1].strip()}.",
        "algorithm": s["statement"],
        "safety_mechanism": s["diagnostic"].split(";")[0],
        "failure_reaction": s["diagnostic"],
        "inputs": s["inputs"],
        "outputs": s["outputs"],
        "verification": s["acceptance"]
    })

print(f"FEAT-CHS-02 updated: {len(f2['sys_reqs'])} SYS, {len(f2['sw_reqs'])} SWR.")

with open(r"c:\Workset\AntiGravityProjects\TestOptimisationExperiement\features_chs_full.py", "w", encoding="utf-8") as f_out:
    f_out.write("# Auto-expanded full Chassis features\n\n")
    f_out.write("full_chs_features = ")
    pprint.pprint(features_chs_full.full_chs_features, stream=f_out, width=120)
    f_out.write("\n")

print("Saved updated features_chs_full.py.")

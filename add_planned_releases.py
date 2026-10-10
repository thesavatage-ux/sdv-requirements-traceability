# -*- coding: utf-8 -*-
"""
Script to assign Planned Release (R100 to R500) across all 40 SDV features in an incremental, testable way.
"""

import pprint
import features_adas_full
import features_pwr_full
import features_chs_full
import features_bdy_full
import features_cpt_full
import features_conn_full

def assign_releases_to_features(features_list):
    for f in features_list:
        sys_reqs = f.get("sys_reqs", [])
        num_sys = len(sys_reqs)
        if num_sys == 0:
            continue
            
        sys_release_map = {}
        
        for idx, sreq in enumerate(sys_reqs):
            # Calculate release based on index fraction
            # 5 planned releases: R100, R200, R300, R400, R500
            frac = idx / num_sys
            if frac < 0.20:
                rel = "R100"
            elif frac < 0.40:
                rel = "R200"
            elif frac < 0.60:
                rel = "R300"
            elif frac < 0.80:
                rel = "R400"
            else:
                rel = "R500"
                
            # If requirement explicitly mentions DEM, DTC, UDS, FOTA, SecOC, or freeze-frame, ensure it is R500
            s_title = sreq.get("title", "").lower()
            s_stmt = sreq.get("statement", "").lower()
            if any(k in s_title or k in s_stmt for k in ["dem", "dtc", "freeze-frame", "freeze frame", "uds", "obd", "audit", "sums"]):
                rel = "R500"
            elif any(k in s_title or k in s_stmt for k in ["lockstep", "safing", "watchdog", "failover", "brownout", "thermal derating", "ftti"]):
                rel = "R400"
            elif any(k in s_title or k in s_stmt for k in ["hmi", "cluster", "hud", "overtake", "curve preview", "mode selection"]):
                if rel not in ["R400", "R500"]:
                    rel = "R300"
            elif any(k in s_title or k in s_stmt for k in ["sensor", "acquisition", "sampling", "adc", "sent", "spi", "resolver"]):
                if idx < 4:
                    rel = "R100"
                    
            sreq["planned_release"] = rel
            sys_release_map[sreq["id"]] = rel
            
        # Assign to child software requirements
        for swreq in f.get("sw_reqs", []):
            parent_id = swreq.get("parent")
            swreq["planned_release"] = sys_release_map.get(parent_id, "R100")

def process_all():
    modules = [
        ("ADAS", features_adas_full, "adas_features", "features_adas_full.py"),
        ("PWR", features_pwr_full, "full_pwr_features", "features_pwr_full.py"),
        ("CHS", features_chs_full, "full_chs_features", "features_chs_full.py"),
        ("BDY", features_bdy_full, "full_bdy_features", "features_bdy_full.py"),
        ("CPT", features_cpt_full, "full_cpt_features", "features_cpt_full.py"),
        ("CONN", features_conn_full, "full_conn_features", "features_conn_full.py")
    ]
    
    release_counts_sys = {"R100": 0, "R200": 0, "R300": 0, "R400": 0, "R500": 0}
    release_counts_sw = {"R100": 0, "R200": 0, "R300": 0, "R400": 0, "R500": 0}
    
    for dom_name, mod, attr_name, filename in modules:
        feats = getattr(mod, attr_name)
        assign_releases_to_features(feats)
        
        for f in feats:
            for s in f["sys_reqs"]:
                release_counts_sys[s["planned_release"]] += 1
            for w in f["sw_reqs"]:
                release_counts_sw[w["planned_release"]] += 1
                
        # Write back to file
        with open(filename, "w", encoding="utf-8") as f_out:
            f_out.write(f"# Auto-expanded full {dom_name} features with Planned Releases (R100-R500)\n\n")
            f_out.write(f"{attr_name} = ")
            pprint.pprint(feats, stream=f_out, width=120)
            f_out.write("\n")
            
        print(f"Updated {filename} with planned release tags.")
        
    print("\n=== SYSTEM REQUIREMENTS RELEASE DISTRIBUTION ===")
    for rel, count in release_counts_sys.items():
        print(f"  {rel}: {count} SYS_REQs ({(count / sum(release_counts_sys.values()) * 100):.1f}%)")
        
    print("\n=== SOFTWARE REQUIREMENTS RELEASE DISTRIBUTION ===")
    for rel, count in release_counts_sw.items():
        print(f"  {rel}: {count} SWR_REQs ({(count / sum(release_counts_sw.values()) * 100):.1f}%)")

if __name__ == "__main__":
    process_all()

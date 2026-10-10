import json
import os
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

# Build flattened dataset and structured mapping
dataset = []
all_swcs = set()

for f in all_features:
    f_id = f["id"]
    f_name = f["name"]
    domain = f["domain"]
    f_asil = f["asil"]
    slug = f["slug"]
    
    # Index sw_reqs by ID for fast lookup
    sw_dict = {sw["id"]: sw for sw in f.get("sw_reqs", [])}
    for sw in f.get("sw_reqs", []):
        if sw.get("swc"):
            all_swcs.add(sw["swc"])
            
    for sr in f.get("sys_reqs", []):
        sr_id = sr["id"]
        # Retrieve mapped child sw reqs
        children = []
        for cid in sr.get("downstream", []):
            if cid in sw_dict:
                children.append(sw_dict[cid])
            else:
                # Fallback if not found directly
                children.append({
                    "id": cid,
                    "title": f"Software Component for {cid}",
                    "asil": sr.get("asil", "QM"),
                    "swc": "SWC",
                    "period": "10 ms",
                    "wcet": "0.5 ms",
                    "planned_release": sr.get("planned_release", "R100"),
                    "algorithm": "Deterministic processing",
                    "safety_mechanism": "Standard check",
                    "failure_reaction": "Log fault",
                    "verification": "Unit test",
                    "inputs": "RTE",
                    "outputs": "RTE"
                })
                
        dataset.append({
            "feature_id": f_id,
            "feature_name": f_name,
            "domain": domain,
            "feature_asil": f_asil,
            "slug": slug,
            "sys_id": sr_id,
            "sys_title": sr["title"],
            "sys_asil": sr.get("asil", "QM"),
            "sys_release": sr.get("planned_release", "R100"),
            "sys_statement": sr.get("statement", ""),
            "sys_activation": sr.get("activation", ""),
            "sys_ftti": sr.get("ftti", "N/A"),
            "sys_safe_state": sr.get("safe_state", "N/A"),
            "sys_failure_reaction": sr.get("failure_reaction", "N/A"),
            "sys_inputs": sr.get("inputs", ""),
            "sys_outputs": sr.get("outputs", ""),
            "sys_verification": sr.get("verification", ""),
            "children": children
        })

print(f"Total System Requirements mapped: {len(dataset)}")
print(f"Total Unique SWCs identified: {len(all_swcs)}")

# Prepare domains and features list for filters
domains_list = sorted(list(set(d["domain"] for d in dataset)))
features_list = []
seen_feats = set()
for d in dataset:
    if d["feature_id"] not in seen_feats:
        seen_feats.add(d["feature_id"])
        features_list.append({
            "id": d["feature_id"],
            "name": d["feature_name"],
            "domain": d["domain"]
        })

data_json = json.dumps(dataset, ensure_ascii=False)
domains_json = json.dumps(domains_list, ensure_ascii=False)
features_json = json.dumps(features_list, ensure_ascii=False)
swcs_json = json.dumps(sorted(list(all_swcs)), ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Automotive Systems & Software Requirements Traceability Explorer</title>
  <meta name="description" content="Interactive ASPICE SYS.2 to SWE.1 & ISO 26262 System to Software Requirements Traceability Matrix with Dynamic Filtering">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-primary: #0a0e17;
      --bg-secondary: #0f172a;
      --bg-surface: #1e293b;
      --bg-surface-hover: #27354f;
      --bg-glass: rgba(15, 23, 42, 0.85);
      --border-color: #334155;
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

      --r100-color: #06b6d4;
      --r100-bg: rgba(6, 182, 212, 0.15);
      --r200-color: #10b981;
      --r200-bg: rgba(16, 185, 129, 0.15);
      --r300-color: #f59e0b;
      --r300-bg: rgba(245, 158, 11, 0.15);
      --r400-color: #f43f5e;
      --r400-bg: rgba(244, 63, 94, 0.15);
      --r500-color: #a855f7;
      --r500-bg: rgba(168, 85, 247, 0.15);

      --asil-d-color: #ef4444;
      --asil-d-bg: rgba(239, 68, 68, 0.2);
      --asil-c-color: #f97316;
      --asil-c-bg: rgba(249, 115, 22, 0.2);
      --asil-b-color: #eab308;
      --asil-b-bg: rgba(234, 179, 8, 0.2);
      --asil-a-color: #38bdf8;
      --asil-a-bg: rgba(56, 189, 248, 0.2);
      --asil-qm-color: #94a3b8;
      --asil-qm-bg: rgba(148, 163, 184, 0.15);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      line-height: 1.5;
      min-height: 100vh;
      overflow-x: hidden;
    }}

    /* Header & Branding */
    header.app-header {{
      background: linear-gradient(180deg, #111827 0%, rgba(15, 23, 42, 0.95) 100%);
      border-bottom: 1px solid var(--border-color);
      padding: 1.25rem 2rem;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(12px);
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
      gap: 0.75rem;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, #2563eb, #38bdf8);
      color: #fff;
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      font-size: 1.1rem;
      padding: 0.35rem 0.75rem;
      border-radius: 8px;
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.35);
      letter-spacing: 0.5px;
    }}

    h1.app-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.4rem;
      font-weight: 700;
      letter-spacing: -0.3px;
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
    }}

    /* Global Metrics KPI Bar */
    .kpi-bar {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 0.75rem;
    }}

    .kpi-card {{
      background: rgba(30, 41, 59, 0.7);
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
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
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

    /* Filters Control Panel */
    .filters-panel {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }}

    .filters-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 1rem;
      margin-bottom: 1.1rem;
    }}

    .filter-group {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }}

    .filter-label {{
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}

    .search-input-wrapper {{
      position: relative;
    }}

    .search-input {{
      width: 100%;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      color: var(--text-main);
      padding: 0.6rem 2.2rem 0.6rem 0.85rem;
      font-size: 0.9rem;
      font-family: inherit;
      transition: all 0.2s ease;
    }}

    .search-input:focus {{
      outline: none;
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    }}

    .search-clear-btn {{
      position: absolute;
      right: 0.6rem;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: var(--text-dim);
      font-size: 1.1rem;
      cursor: pointer;
      display: none;
    }}

    .search-clear-btn:hover {{
      color: var(--text-main);
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
      transition: all 0.2s ease;
    }}

    select.filter-select:focus {{
      outline: none;
      border-color: var(--border-focus);
    }}

    /* Pill Filter Bars */
    .pill-filter-bar {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-top: 0.5rem;
    }}

    .pill-title {{
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-right: 0.25rem;
    }}

    .filter-pill {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.78rem;
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

    .filter-pill.active.r100 {{ background: var(--r100-bg); color: var(--r100-color); border-color: var(--r100-color); }}
    .filter-pill.active.r200 {{ background: var(--r200-bg); color: var(--r200-color); border-color: var(--r200-color); }}
    .filter-pill.active.r300 {{ background: var(--r300-bg); color: var(--r300-color); border-color: var(--r300-color); }}
    .filter-pill.active.r400 {{ background: var(--r400-bg); color: var(--r400-color); border-color: var(--r400-color); }}
    .filter-pill.active.r500 {{ background: var(--r500-bg); color: var(--r500-color); border-color: var(--r500-color); }}

    .filter-pill.active.asild {{ background: var(--asil-d-bg); color: var(--asil-d-color); border-color: var(--asil-d-color); }}
    .filter-pill.active.asilc {{ background: var(--asil-c-bg); color: var(--asil-c-color); border-color: var(--asil-c-color); }}
    .filter-pill.active.asilb {{ background: var(--asil-b-bg); color: var(--asil-b-color); border-color: var(--asil-b-color); }}
    .filter-pill.active.asila {{ background: var(--asil-a-bg); color: var(--asil-a-color); border-color: var(--asil-a-color); }}
    .filter-pill.active.asilqm {{ background: var(--asil-qm-bg); color: var(--asil-qm-color); border-color: var(--asil-qm-color); }}

    /* View Controls Bar */
    .view-controls-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
      padding-top: 1rem;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }}

    .view-toggles {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
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

    .btn:hover {{
      background: var(--bg-surface-hover);
      border-color: #64748b;
    }}

    .btn.active {{
      background: var(--accent-blue);
      color: #0b1120;
      border-color: var(--accent-blue);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }}

    .btn-reset {{
      color: var(--accent-rose);
      border-color: rgba(244, 63, 94, 0.3);
      background: rgba(244, 63, 94, 0.08);
    }}

    .btn-reset:hover {{
      background: rgba(244, 63, 94, 0.2);
      border-color: var(--accent-rose);
    }}

    .btn-export {{
      color: var(--accent-emerald);
      border-color: rgba(16, 185, 129, 0.3);
      background: rgba(16, 185, 129, 0.08);
    }}

    .btn-export:hover {{
      background: rgba(16, 185, 129, 0.2);
      border-color: var(--accent-emerald);
    }}

    .results-summary {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    .results-summary b {{
      color: #ffffff;
      font-family: 'JetBrains Mono', monospace;
    }}

    /* Card View Layout */
    .requirements-list {{
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}

    .sys-card {{
      background: #111827;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
      transition: border-color 0.2s ease, transform 0.2s ease;
    }}

    .sys-card:hover {{
      border-color: rgba(56, 189, 248, 0.4);
    }}

    /* System Card Header */
    .sys-header {{
      padding: 1rem 1.25rem;
      background: linear-gradient(90deg, #162032 0%, #111827 100%);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      cursor: pointer;
      user-select: none;
    }}

    .sys-title-left {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      flex: 1;
    }}

    .sys-badge-row {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    .id-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.82rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
      letter-spacing: 0.2px;
    }}

    .id-badge.sys {{
      background: #1e3a8a;
      color: #93c5fd;
      border: 1px solid #3b82f6;
    }}

    .id-badge.swr {{
      background: #14532d;
      color: #86efac;
      border: 1px solid #22c55e;
    }}

    .badge-release {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
    }}

    .badge-release.r100 {{ background: var(--r100-bg); color: var(--r100-color); border: 1px solid var(--r100-color); }}
    .badge-release.r200 {{ background: var(--r200-bg); color: var(--r200-color); border: 1px solid var(--r200-color); }}
    .badge-release.r300 {{ background: var(--r300-bg); color: var(--r300-color); border: 1px solid var(--r300-color); }}
    .badge-release.r400 {{ background: var(--r400-bg); color: var(--r400-color); border: 1px solid var(--r400-color); }}
    .badge-release.r500 {{ background: var(--r500-bg); color: var(--r500-color); border: 1px solid var(--r500-color); }}

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

    .feature-tag {{
      font-size: 0.75rem;
      color: var(--text-dim);
    }}

    .feature-tag span {{
      color: var(--text-muted);
      font-weight: 500;
    }}

    h3.sys-title {{
      font-size: 1.05rem;
      font-weight: 600;
      color: #ffffff;
      line-height: 1.35;
    }}

    .sys-header-right {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .child-count-pill {{
      font-size: 0.78rem;
      font-weight: 600;
      background: rgba(34, 197, 94, 0.15);
      color: #4ade80;
      border: 1px solid rgba(34, 197, 94, 0.3);
      padding: 0.25rem 0.65rem;
      border-radius: 20px;
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .accordion-arrow {{
      color: var(--text-muted);
      font-size: 0.85rem;
      transition: transform 0.2s ease;
    }}

    .sys-card.collapsed .accordion-arrow {{
      transform: rotate(-90deg);
    }}

    .sys-card.collapsed .sys-body {{
      display: none;
    }}

    /* System Card Body */
    .sys-body {{
      padding: 1.25rem;
    }}

    .statement-box {{
      background: rgba(15, 23, 42, 0.7);
      border-left: 3px solid var(--accent-blue);
      border-radius: 0 8px 8px 0;
      padding: 0.85rem 1rem;
      margin-bottom: 1rem;
      font-size: 0.92rem;
      color: #e2e8f0;
      line-height: 1.5;
    }}

    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 0.75rem;
      margin-bottom: 1.25rem;
      background: rgba(30, 41, 59, 0.35);
      border-radius: 8px;
      padding: 0.85rem;
      border: 1px solid rgba(255, 255, 255, 0.04);
    }}

    .meta-item {{
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }}

    .meta-item .meta-k {{
      font-size: 0.7rem;
      font-weight: 600;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}

    .meta-item .meta-v {{
      font-size: 0.84rem;
      color: #cbd5e1;
      font-weight: 500;
    }}

    /* Downstream Software Requirements Container */
    .downstream-container {{
      border-top: 1px dashed rgba(255, 255, 255, 0.12);
      padding-top: 1rem;
      margin-top: 0.5rem;
    }}

    .downstream-title {{
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: var(--accent-emerald);
      margin-bottom: 0.75rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .swr-list {{
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      padding-left: 0.5rem;
      border-left: 2px solid rgba(34, 197, 94, 0.25);
    }}

    .swr-card {{
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 8px;
      padding: 0.85rem 1rem;
      transition: all 0.2s ease;
    }}

    .swr-card:hover {{
      background: rgba(30, 41, 59, 0.5);
      border-color: rgba(34, 197, 94, 0.35);
    }}

    .swr-header-row {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.75rem;
      flex-wrap: wrap;
      margin-bottom: 0.4rem;
    }}

    .swr-title-wrap {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    h4.swr-title {{
      font-size: 0.92rem;
      font-weight: 600;
      color: #f1f5f9;
    }}

    .swc-pill {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      font-weight: 600;
      background: rgba(99, 102, 241, 0.18);
      color: #a5b4fc;
      border: 1px solid rgba(99, 102, 241, 0.35);
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
    }}

    .period-pill {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      background: rgba(255, 255, 255, 0.06);
      color: var(--text-muted);
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
    }}

    .swr-algo-box {{
      font-size: 0.84rem;
      color: #94a3b8;
      background: rgba(0, 0, 0, 0.2);
      border-radius: 6px;
      padding: 0.6rem 0.75rem;
      margin: 0.4rem 0 0.6rem 0;
      line-height: 1.45;
    }}

    .swr-details-toggle {{
      font-size: 0.75rem;
      color: var(--accent-blue);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      user-select: none;
      font-weight: 500;
      margin-top: 0.2rem;
    }}

    .swr-details-toggle:hover {{
      text-decoration: underline;
    }}

    .swr-extra-details {{
      display: none;
      margin-top: 0.6rem;
      padding-top: 0.6rem;
      border-top: 1px dashed rgba(255, 255, 255, 0.08);
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 0.5rem;
    }}

    .swr-extra-details.hidden {{
      display: none !important;
    }}

    /* Table View Styling */
    .matrix-table-container {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow-x: auto;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
      display: none;
    }}

    table.matrix-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      text-align: left;
    }}

    table.matrix-table th {{
      background: #1e293b;
      padding: 0.85rem 1rem;
      color: #f1f5f9;
      font-weight: 600;
      border-bottom: 2px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 10;
      white-space: nowrap;
    }}

    table.matrix-table td {{
      padding: 0.85rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      vertical-align: top;
    }}

    table.matrix-table tr:hover {{
      background: rgba(30, 41, 59, 0.4);
    }}

    /* Pagination Bar */
    .pagination-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
      margin-top: 1.5rem;
      padding: 1rem 1.25rem;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 10px;
    }}

    .page-controls {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .page-btn {{
      padding: 0.35rem 0.75rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      color: var(--text-main);
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 600;
      font-family: inherit;
    }}

    .page-btn:hover:not(:disabled) {{
      background: var(--bg-surface-hover);
      border-color: #64748b;
    }}

    .page-btn:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}

    .page-info {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    /* Empty state */
    .empty-state {{
      text-align: center;
      padding: 4rem 2rem;
      background: var(--bg-secondary);
      border: 1px dashed var(--border-color);
      border-radius: 12px;
      margin: 2rem 0;
      display: none;
    }}

    .empty-icon {{
      font-size: 3rem;
      margin-bottom: 1rem;
      color: var(--text-dim);
    }}

    .empty-title {{
      font-size: 1.2rem;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 0.5rem;
    }}

    .empty-subtitle {{
      font-size: 0.9rem;
      color: var(--text-muted);
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

    /* Responsive */
    @media (max-width: 900px) {{
      header.app-header {{
        padding: 1rem;
      }}
      main.app-main {{
        padding: 1rem;
      }}
      .kpi-bar {{
        grid-template-columns: repeat(3, 1fr);
      }}
    }}
  </style>
</head>
<body>

  <!-- Top App Header -->
  <header class="app-header">
    <div class="header-top">
      <div class="brand-title-wrap">
        <div class="logo-badge">ASPICE & ISO 26262</div>
        <div>
          <h1 class="app-title">Automotive Systems & Software Requirements Traceability Explorer</h1>
          <p class="app-subtitle">Bi-Directional SYS.2 System Requirements ⇄ SWE.1 Software Requirements 1:N Verification Matrix</p>
        </div>
      </div>
      <div class="compliance-badges">
        <span class="tag-badge">ISO 26262:2018 ASIL A-D</span>
        <span class="tag-badge">ASPICE PAM v3.1</span>
        <span class="tag-badge">AUTOSAR Classic & Adaptive</span>
        <span class="tag-badge">40 SDV Features</span>
        <span class="tag-badge">5 Planned Releases</span>
      </div>
    </div>

    <!-- Live KPI Summary Bar -->
    <div class="kpi-bar" id="kpi-summary-bar">
      <div class="kpi-card">
        <span class="kpi-label">Matched SysReqs</span>
        <span class="kpi-value cyan" id="kpi-sys-count">621</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Matched SwReqs</span>
        <span class="kpi-value emerald" id="kpi-sw-count">1,244</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Total Requirements</span>
        <span class="kpi-value purple" id="kpi-total-reqs">1,865</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Split Ratio</span>
        <span class="kpi-value amber" id="kpi-split-ratio">1 : 2.00</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">ASIL D Safety Reqs</span>
        <span class="kpi-value rose" id="kpi-asil-d-count">--</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Active Features</span>
        <span class="kpi-value" id="kpi-features-count">40 / 40</span>
      </div>
    </div>
  </header>

  <main class="app-main">
    <!-- Filter Controls Panel -->
    <section class="filters-panel" aria-label="Requirements Filter Toolbar">
      <div class="filters-grid">
        <!-- Text Search -->
        <div class="filter-group">
          <label class="filter-label" for="search-input">Search Requirements</label>
          <div class="search-input-wrapper">
            <input type="text" id="search-input" class="search-input" placeholder="Search ID, title, text, SWC, FTTI..." autocomplete="off">
            <button id="search-clear-btn" class="search-clear-btn" title="Clear Search">✕</button>
          </div>
        </div>

        <!-- Domain Filter -->
        <div class="filter-group">
          <label class="filter-label" for="domain-filter">Engineering Domain</label>
          <select id="domain-filter" class="filter-select">
            <option value="ALL">All Domains (6 Domains)</option>
          </select>
        </div>

        <!-- Feature Filter -->
        <div class="filter-group">
          <label class="filter-label" for="feature-filter">Vehicle Feature Module</label>
          <select id="feature-filter" class="filter-select">
            <option value="ALL">All Features (40 Features)</option>
          </select>
        </div>

        <!-- AUTOSAR SWC Filter -->
        <div class="filter-group">
          <label class="filter-label" for="swc-filter">Allocated AUTOSAR SWC</label>
          <select id="swc-filter" class="filter-select">
            <option value="ALL">All SWCs (All Software Components)</option>
          </select>
        </div>
      </div>

      <!-- Quick Release Filter Pills -->
      <div class="pill-filter-bar">
        <span class="pill-title">Planned Release:</span>
        <button class="filter-pill active" data-filter="release" data-value="ALL">All Releases</button>
        <button class="filter-pill r100" data-filter="release" data-value="R100">R100 (Foundation)</button>
        <button class="filter-pill r200" data-filter="release" data-value="R200">R200 (Core Closed-Loop)</button>
        <button class="filter-pill r300" data-filter="release" data-value="R300">R300 (Extended ODD)</button>
        <button class="filter-pill r400" data-filter="release" data-value="R400">R400 (Safety & Safing)</button>
        <button class="filter-pill r500" data-filter="release" data-value="R500">R500 (Diag & Homologation)</button>
      </div>

      <!-- Quick ASIL Filter Pills -->
      <div class="pill-filter-bar">
        <span class="pill-title">Safety ASIL Rating:</span>
        <button class="filter-pill active" data-filter="asil" data-value="ALL">All ASILs</button>
        <button class="filter-pill asild" data-filter="asil" data-value="ASIL D">ASIL D</button>
        <button class="filter-pill asilc" data-filter="asil" data-value="ASIL C">ASIL C</button>
        <button class="filter-pill asilb" data-filter="asil" data-value="ASIL B">ASIL B</button>
        <button class="filter-pill asila" data-filter="asil" data-value="ASIL A">ASIL A</button>
        <button class="filter-pill asilqm" data-filter="asil" data-value="QM">QM</button>
      </div>

      <!-- View Controls & Action Buttons -->
      <div class="view-controls-bar">
        <div class="view-toggles">
          <button id="view-cards-btn" class="btn active" title="Switch to Hierarchy Cards View">🗂 Hierarchy Card View</button>
          <button id="view-table-btn" class="btn" title="Switch to Compact Traceability Table View">▦ Matrix Table View</button>
          <button id="toggle-expand-all" class="btn" title="Expand or Collapse All Cards">⊟ Collapse All</button>
        </div>

        <div class="view-toggles">
          <span class="results-summary" id="results-count-text">Showing <b>621</b> System Requirements</span>
          <button id="export-csv-btn" class="btn btn-export" title="Export Current Filtered Results to CSV">📥 Export CSV</button>
          <button id="reset-filters-btn" class="btn btn-reset" title="Reset All Filters">↺ Reset Filters</button>
        </div>
      </div>
    </section>

    <!-- Card Hierarchy View Container -->
    <section id="cards-view-container" class="requirements-list" aria-label="System and Software Requirements Hierarchy List">
      <!-- Dynamically Rendered by JS -->
    </section>

    <!-- Matrix Table View Container -->
    <section id="table-view-container" class="matrix-table-container" aria-label="Traceability Matrix Table">
      <table class="matrix-table">
        <thead>
          <tr>
            <th>System Req ID</th>
            <th>Planned Release</th>
            <th>ASIL</th>
            <th>System Requirement Title</th>
            <th>Domain & Feature</th>
            <th>Mapped Software Requirements (1:N)</th>
            <th>Allocated AUTOSAR SWC</th>
            <th>SW Execution Rate</th>
          </tr>
        </thead>
        <tbody id="table-view-body">
          <!-- Dynamically Rendered by JS -->
        </tbody>
      </table>
    </section>

    <!-- Empty State -->
    <div id="empty-state" class="empty-state">
      <div class="empty-icon">🔍</div>
      <h3 class="empty-title">No Matching Requirements Found</h3>
      <p class="empty-subtitle">Try adjusting your search criteria, clearing filters, or selecting a different release.</p>
    </div>

    <!-- Pagination Controls -->
    <div class="pagination-bar" id="pagination-container">
      <div class="page-info">
        Page <span id="current-page-num" style="color:#fff; font-weight:700;">1</span> of <span id="total-page-num" style="color:#fff; font-weight:700;">1</span>
        (<span id="page-item-range" style="color:var(--text-muted);">1-50</span> of <span id="total-filtered-count">621</span>)
      </div>
      <div class="page-controls">
        <label for="page-size-select" style="font-size:0.8rem; color:var(--text-muted); margin-right:0.35rem;">Items per page:</label>
        <select id="page-size-select" class="filter-select" style="width:auto; padding:0.25rem 0.6rem; font-size:0.8rem; margin-right:0.75rem;">
          <option value="25">25</option>
          <option value="50" selected>50</option>
          <option value="100">100</option>
          <option value="ALL">All (621)</option>
        </select>
        <button id="btn-first-page" class="page-btn">« First</button>
        <button id="btn-prev-page" class="page-btn">‹ Prev</button>
        <button id="btn-next-page" class="page-btn">Next ›</button>
        <button id="btn-last-page" class="page-btn">Last »</button>
      </div>
    </div>
  </main>

  <footer class="app-footer">
    <p>Automotive Systems & Software Requirements Specification Traceability Matrix | ASPICE PAM v3.1 (SYS.2, SYS.3, SWE.1) & ISO 26262:2018 (Part 4 & Part 6)</p>
    <p style="margin-top:0.4rem; color:#475569;">Generated automatically for 40 Next-Generation SDV Feature Modules | 100% Bi-Directional Traceability Coverage Verified</p>
  </footer>

  <script>
    // Embedded Master Dataset
    const RAW_DATASET = {data_json};
    const DOMAINS_LIST = {domains_json};
    const FEATURES_LIST = {features_json};
    const SWCS_LIST = {swcs_json};

    // State
    let state = {{
      search: "",
      domain: "ALL",
      feature: "ALL",
      swc: "ALL",
      release: "ALL",
      asil: "ALL",
      viewMode: "cards", // 'cards' | 'table'
      pageSize: 50,
      currentPage: 1,
      allExpanded: true
    }};

    // DOM Elements
    const searchInput = document.getElementById("search-input");
    const searchClearBtn = document.getElementById("search-clear-btn");
    const domainFilter = document.getElementById("domain-filter");
    const featureFilter = document.getElementById("feature-filter");
    const swcFilter = document.getElementById("swc-filter");
    const cardsContainer = document.getElementById("cards-view-container");
    const tableContainer = document.getElementById("table-view-container");
    const tableBody = document.getElementById("table-view-body");
    const emptyState = document.getElementById("empty-state");
    const resultsCountText = document.getElementById("results-count-text");
    const viewCardsBtn = document.getElementById("view-cards-btn");
    const viewTableBtn = document.getElementById("view-table-btn");
    const toggleExpandAllBtn = document.getElementById("toggle-expand-all");
    const resetFiltersBtn = document.getElementById("reset-filters-btn");
    const exportCsvBtn = document.getElementById("export-csv-btn");
    const pageSizeSelect = document.getElementById("page-size-select");
    const btnFirstPage = document.getElementById("btn-first-page");
    const btnPrevPage = document.getElementById("btn-prev-page");
    const btnNextPage = document.getElementById("btn-next-page");
    const btnLastPage = document.getElementById("btn-last-page");
    const currentPageNum = document.getElementById("current-page-num");
    const totalPageNum = document.getElementById("total-page-num");
    const pageItemRange = document.getElementById("page-item-range");
    const totalFilteredCount = document.getElementById("total-filtered-count");

    // KPI elements
    const kpiSysCount = document.getElementById("kpi-sys-count");
    const kpiSwCount = document.getElementById("kpi-sw-count");
    const kpiTotalReqs = document.getElementById("kpi-total-reqs");
    const kpiSplitRatio = document.getElementById("kpi-split-ratio");
    const kpiAsilDCount = document.getElementById("kpi-asil-d-count");
    const kpiFeaturesCount = document.getElementById("kpi-features-count");

    // Initialize Dropdowns
    function initDropdowns() {{
      DOMAINS_LIST.forEach(d => {{
        const opt = document.createElement("option");
        opt.value = d;
        opt.textContent = d;
        domainFilter.appendChild(opt);
      }});

      populateFeatureDropdown("ALL");

      SWCS_LIST.forEach(swc => {{
        const opt = document.createElement("option");
        opt.value = swc;
        opt.textContent = swc;
        swcFilter.appendChild(opt);
      }});
    }}

    function populateFeatureDropdown(selectedDomain) {{
      featureFilter.innerHTML = '<option value="ALL">All Features (40 Features)</option>';
      const filtered = selectedDomain === "ALL" 
        ? FEATURES_LIST 
        : FEATURES_LIST.filter(f => f.domain === selectedDomain);
      
      filtered.forEach(f => {{
        const opt = document.createElement("option");
        opt.value = f.id;
        opt.textContent = `${{f.id}}: ${{f.name}}`;
        featureFilter.appendChild(opt);
      }});
    }}

    // Filter Logic
    function getFilteredData() {{
      const q = state.search.toLowerCase().trim();
      
      return RAW_DATASET.filter(item => {{
        // Domain
        if (state.domain !== "ALL" && item.domain !== state.domain) return false;
        
        // Feature
        if (state.feature !== "ALL" && item.feature_id !== state.feature) return false;
        
        // Release
        if (state.release !== "ALL" && item.sys_release !== state.release) return false;
        
        // ASIL
        if (state.asil !== "ALL") {{
          if (!item.sys_asil.toUpperCase().includes(state.asil.toUpperCase())) return false;
        }}
        
        // SWC Filter
        if (state.swc !== "ALL") {{
          const hasSwc = item.children.some(c => c.swc === state.swc);
          if (!hasSwc) return false;
        }}
        
        // Free Text Search
        if (q) {{
          const matchSys = 
            item.sys_id.toLowerCase().includes(q) ||
            item.sys_title.toLowerCase().includes(q) ||
            item.sys_statement.toLowerCase().includes(q) ||
            item.sys_ftti.toLowerCase().includes(q) ||
            item.sys_safe_state.toLowerCase().includes(q) ||
            item.feature_id.toLowerCase().includes(q) ||
            item.feature_name.toLowerCase().includes(q);

          const matchSwr = item.children.some(c => 
            c.id.toLowerCase().includes(q) ||
            c.title.toLowerCase().includes(q) ||
            (c.swc && c.swc.toLowerCase().includes(q)) ||
            (c.algorithm && c.algorithm.toLowerCase().includes(q)) ||
            (c.verification && c.verification.toLowerCase().includes(q))
          );

          if (!matchSys && !matchSwr) return false;
        }}
        
        return true;
      }});
    }}

    // KPI Updater
    function updateKPIs(filtered) {{
      const sysCount = filtered.length;
      let swCount = 0;
      let asilDCount = 0;
      const feats = new Set();

      filtered.forEach(item => {{
        swCount += item.children.length;
        if (item.sys_asil.toUpperCase().includes("ASIL D")) {{
          asilDCount++;
        }}
        feats.add(item.feature_id);
      }});

      const totalReqs = sysCount + swCount;
      const ratio = sysCount > 0 ? (swCount / sysCount).toFixed(2) : "0.00";

      kpiSysCount.textContent = sysCount.toLocaleString();
      kpiSwCount.textContent = swCount.toLocaleString();
      kpiTotalReqs.textContent = totalReqs.toLocaleString();
      kpiSplitRatio.textContent = `1 : ${{ratio}}`;
      kpiAsilDCount.textContent = asilDCount.toLocaleString();
      kpiFeaturesCount.textContent = `${{feats.size}} / 40`;

      resultsCountText.innerHTML = `Showing <b>${{sysCount}}</b> System Requirements with <b>${{swCount}}</b> Mapped Child Software Requirements`;
    }}

    // Helper for ASIL Class
    function getAsilClass(asilStr) {{
      const str = (asilStr || "").toUpperCase();
      if (str.includes("ASIL D")) return "d";
      if (str.includes("ASIL C")) return "c";
      if (str.includes("ASIL B")) return "b";
      if (str.includes("ASIL A")) return "a";
      return "qm";
    }}

    function getReleaseClass(relStr) {{
      return (relStr || "R100").toLowerCase();
    }}

    // Render Cards
    function renderCards(pageData) {{
      if (pageData.length === 0) {{
        cardsContainer.innerHTML = "";
        emptyState.style.display = "block";
        return;
      }}
      emptyState.style.display = "none";

      const html = pageData.map(item => {{
        const asilCls = getAsilClass(item.sys_asil);
        const relCls = getReleaseClass(item.sys_release);
        const isCollapsed = !state.allExpanded;

        // Render downstream children
        const childrenHtml = item.children.map(child => {{
          const cAsilCls = getAsilClass(child.asil);
          const cRelCls = getReleaseClass(child.planned_release || item.sys_release);

          return `
            <div class="swr-card">
              <div class="swr-header-row">
                <div class="swr-title-wrap">
                  <span class="id-badge swr">${{child.id}}</span>
                  <span class="badge-release ${{cRelCls}}">${{child.planned_release || item.sys_release}}</span>
                  <span class="badge-asil ${{cAsilCls}}">${{child.asil || item.sys_asil}}</span>
                  <span class="swc-pill">${{child.swc || "SWC"}}</span>
                  <span class="period-pill">⏱ ${{child.period || "10 ms"}}</span>
                  <span class="period-pill">WCET: ${{child.wcet || "0.5 ms"}}</span>
                </div>
              </div>
              <h4 class="swr-title">${{child.title}}</h4>
              <div class="swr-algo-box">
                <b>Algorithmic Control Law:</b> ${{child.algorithm || "Deterministic software law"}}
              </div>
              <span class="swr-details-toggle" onclick="toggleSwrDetails(this)">▶ View Safety Mechanism & Port Interfaces</span>
              <div class="swr-extra-details hidden">
                <div class="meta-item">
                  <span class="meta-k">Software Safety Mechanism</span>
                  <span class="meta-v">${{child.safety_mechanism || "Range and gradient checks"}}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-k">DEM Failure Event & Diagnostic Action</span>
                  <span class="meta-v">${{child.failure_reaction || "DEM event logged"}}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-k">Software Input Ports</span>
                  <span class="meta-v"><code>${{child.inputs || "RTE In"}}</code></span>
                </div>
                <div class="meta-item">
                  <span class="meta-k">Software Output Ports</span>
                  <span class="meta-v"><code>${{child.outputs || "RTE Out"}}</code></span>
                </div>
                <div class="meta-item" style="grid-column: 1 / -1;">
                  <span class="meta-k">Software Verification Method</span>
                  <span class="meta-v">${{child.verification || "Unit test and SIL"}}</span>
                </div>
              </div>
            </div>
          `;
        }}).join("");

        return `
          <article class="sys-card ${{isCollapsed ? 'collapsed' : ''}}" id="card-${{item.sys_id}}">
            <div class="sys-header" onclick="toggleCard('${{item.sys_id}}')">
              <div class="sys-title-left">
                <div class="sys-badge-row">
                  <span class="id-badge sys">${{item.sys_id}}</span>
                  <span class="badge-release ${{relCls}}">${{item.sys_release}}</span>
                  <span class="badge-asil ${{asilCls}}">${{item.sys_asil}}</span>
                  <span class="feature-tag"><span>${{item.domain}}</span> • ${{item.feature_id}} (${{item.feature_name}})</span>
                </div>
                <h3 class="sys-title">${{item.sys_title}}</h3>
              </div>
              <div class="sys-header-right">
                <span class="child-count-pill"><b>${{item.children.length}}</b> Child SwReqs</span>
                <span class="accordion-arrow">▼</span>
              </div>
            </div>
            <div class="sys-body">
              <div class="statement-box">
                <b>Requirement Statement:</b><br>${{item.sys_statement}}
              </div>
              <div class="meta-grid">
                <div class="meta-item">
                  <span class="meta-k">FTTI (Fault Tolerant Time Interval)</span>
                  <span class="meta-v" style="color:var(--accent-rose); font-weight:700;">${{item.sys_ftti}}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-k">Safe State Action</span>
                  <span class="meta-v">${{item.sys_safe_state}}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-k">Failure Detection & Reaction</span>
                  <span class="meta-v">${{item.sys_failure_reaction}}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-k">System Verification Method</span>
                  <span class="meta-v">${{item.sys_verification}}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-k">Input Interfaces</span>
                  <span class="meta-v"><code>${{item.sys_inputs}}</code></span>
                </div>
                <div class="meta-item">
                  <span class="meta-k">Output Interfaces</span>
                  <span class="meta-v"><code>${{item.sys_outputs}}</code></span>
                </div>
              </div>
              <div class="downstream-container">
                <div class="downstream-title">
                  <span>↳ Mapped Downstream Software Requirements (1:N ASPICE SWE.1 Partitioning):</span>
                </div>
                <div class="swr-list">
                  ${{childrenHtml}}
                </div>
              </div>
            </div>
          </article>
        `;
      }}).join("");

      cardsContainer.innerHTML = html;
    }}

    // Render Table
    function renderTable(pageData) {{
      if (pageData.length === 0) {{
        tableBody.innerHTML = "";
        emptyState.style.display = "block";
        return;
      }}
      emptyState.style.display = "none";

      const rowsHtml = pageData.map(item => {{
        const asilCls = getAsilClass(item.sys_asil);
        const relCls = getReleaseClass(item.sys_release);

        const childrenList = item.children.map(c => `
          <div style="margin-bottom:0.4rem; padding-bottom:0.4rem; border-bottom:1px dashed rgba(255,255,255,0.06);">
            <span class="id-badge swr" style="font-size:0.7rem; padding:0.1rem 0.35rem;">${{c.id}}</span>
            <span style="font-weight:600; color:#f1f5f9; font-size:0.8rem;">${{c.title}}</span>
          </div>
        `).join("");

        const swcList = item.children.map(c => `
          <div style="margin-bottom:0.4rem; font-size:0.75rem;">
            <span class="swc-pill" style="font-size:0.7rem;">${{c.swc}}</span>
          </div>
        `).join("");

        const periodList = item.children.map(c => `
          <div style="margin-bottom:0.4rem; font-size:0.75rem; color:var(--text-muted); font-family:'JetBrains Mono',monospace;">
            ${{c.period || "10 ms"}}
          </div>
        `).join("");

        return `
          <tr>
            <td>
              <span class="id-badge sys">${{item.sys_id}}</span>
            </td>
            <td>
              <span class="badge-release ${{relCls}}">${{item.sys_release}}</span>
            </td>
            <td>
              <span class="badge-asil ${{asilCls}}">${{item.sys_asil}}</span>
            </td>
            <td>
              <div style="font-weight:600; color:#ffffff; margin-bottom:0.25rem;">${{item.sys_title}}</div>
              <div style="font-size:0.8rem; color:var(--text-muted); line-height:1.4;">${{item.sys_statement.substring(0, 160)}}...</div>
            </td>
            <td>
              <div style="font-weight:600; color:var(--accent-blue);">${{item.feature_id}}</div>
              <div style="font-size:0.75rem; color:var(--text-dim);">${{item.domain}}</div>
            </td>
            <td>
              ${{childrenList}}
            </td>
            <td>
              ${{swcList}}
            </td>
            <td>
              ${{periodList}}
            </td>
          </tr>
        `;
      }}).join("");

      tableBody.innerHTML = rowsHtml;
    }}

    // Render Master View with Pagination
    function render() {{
      const filtered = getFilteredData();
      updateKPIs(filtered);

      const totalItems = filtered.length;
      totalFilteredCount.textContent = totalItems.toLocaleString();

      let pageItems = filtered;
      let totalPages = 1;

      if (state.pageSize !== "ALL") {{
        const size = parseInt(state.pageSize, 10);
        totalPages = Math.max(1, Math.ceil(totalItems / size));
        if (state.currentPage > totalPages) state.currentPage = totalPages;
        const start = (state.currentPage - 1) * size;
        const end = Math.min(start + size, totalItems);
        pageItems = filtered.slice(start, end);

        currentPageNum.textContent = state.currentPage;
        totalPageNum.textContent = totalPages;
        pageItemRange.textContent = totalItems === 0 ? "0-0" : `${{start + 1}}-${{end}}`;
      }} else {{
        currentPageNum.textContent = "1";
        totalPageNum.textContent = "1";
        pageItemRange.textContent = totalItems === 0 ? "0-0" : `1-${{totalItems}}`;
      }}

      // Update Pagination Button States
      btnFirstPage.disabled = state.currentPage <= 1;
      btnPrevPage.disabled = state.currentPage <= 1;
      btnNextPage.disabled = state.currentPage >= totalPages;
      btnLastPage.disabled = state.currentPage >= totalPages;

      if (state.viewMode === "cards") {{
        cardsContainer.style.display = "flex";
        tableContainer.style.display = "none";
        renderCards(pageItems);
      }} else {{
        cardsContainer.style.display = "none";
        tableContainer.style.display = "block";
        renderTable(pageItems);
      }}
    }}

    // Toggle SWR Extra Details
    window.toggleSwrDetails = function(element) {{
      const extra = element.nextElementSibling;
      if (extra.classList.contains("hidden")) {{
        extra.classList.remove("hidden");
        element.textContent = "▼ Hide Safety Mechanism & Port Interfaces";
      }} else {{
        extra.classList.add("hidden");
        element.textContent = "▶ View Safety Mechanism & Port Interfaces";
      }}
    }};

    // Toggle Sys Card Accordion
    window.toggleCard = function(sysId) {{
      const card = document.getElementById(`card-${{sysId}}`);
      if (card) {{
        card.classList.toggle("collapsed");
      }}
    }};

    // Event Listeners
    searchInput.addEventListener("input", (e) => {{
      state.search = e.target.value;
      searchClearBtn.style.display = state.search ? "block" : "none";
      state.currentPage = 1;
      render();
    }});

    searchClearBtn.addEventListener("click", () => {{
      searchInput.value = "";
      state.search = "";
      searchClearBtn.style.display = "none";
      state.currentPage = 1;
      render();
    }});

    domainFilter.addEventListener("change", (e) => {{
      state.domain = e.target.value;
      populateFeatureDropdown(state.domain);
      state.feature = "ALL";
      state.currentPage = 1;
      render();
    }});

    featureFilter.addEventListener("change", (e) => {{
      state.feature = e.target.value;
      state.currentPage = 1;
      render();
    }});

    swcFilter.addEventListener("change", (e) => {{
      state.swc = e.target.value;
      state.currentPage = 1;
      render();
    }});

    // Pill Filters
    document.querySelectorAll(".filter-pill").forEach(pill => {{
      pill.addEventListener("click", () => {{
        const filterType = pill.dataset.filter;
        const val = pill.dataset.value;

        // Deselect siblings
        document.querySelectorAll(`.filter-pill[data-filter="${{filterType}}"]`).forEach(p => p.classList.remove("active"));
        pill.classList.add("active");

        if (filterType === "release") {{
          state.release = val;
        }} else if (filterType === "asil") {{
          state.asil = val;
        }}
        state.currentPage = 1;
        render();
      }});
    }});

    // View Mode Toggle
    viewCardsBtn.addEventListener("click", () => {{
      state.viewMode = "cards";
      viewCardsBtn.classList.add("active");
      viewTableBtn.classList.remove("active");
      render();
    }});

    viewTableBtn.addEventListener("click", () => {{
      state.viewMode = "table";
      viewTableBtn.classList.add("active");
      viewCardsBtn.classList.remove("active");
      render();
    }});

    // Expand / Collapse All
    toggleExpandAllBtn.addEventListener("click", () => {{
      state.allExpanded = !state.allExpanded;
      toggleExpandAllBtn.textContent = state.allExpanded ? "⊟ Collapse All" : "⊞ Expand All";
      document.querySelectorAll(".sys-card").forEach(c => {{
        if (state.allExpanded) {{
          c.classList.remove("collapsed");
        }} else {{
          c.classList.add("collapsed");
        }}
      }});
    }});

    // Reset Filters
    resetFiltersBtn.addEventListener("click", () => {{
      state.search = "";
      state.domain = "ALL";
      state.feature = "ALL";
      state.swc = "ALL";
      state.release = "ALL";
      state.asil = "ALL";
      state.currentPage = 1;

      searchInput.value = "";
      searchClearBtn.style.display = "none";
      domainFilter.value = "ALL";
      populateFeatureDropdown("ALL");
      featureFilter.value = "ALL";
      swcFilter.value = "ALL";

      document.querySelectorAll('.filter-pill[data-filter="release"]').forEach(p => {{
        p.classList.toggle("active", p.dataset.value === "ALL");
      }});
      document.querySelectorAll('.filter-pill[data-filter="asil"]').forEach(p => {{
        p.classList.toggle("active", p.dataset.value === "ALL");
      }});

      render();
    }});

    // Pagination
    pageSizeSelect.addEventListener("change", (e) => {{
      state.pageSize = e.target.value;
      state.currentPage = 1;
      render();
    }});

    btnFirstPage.addEventListener("click", () => {{ state.currentPage = 1; render(); window.scrollTo({{top: 250, behavior: 'smooth'}}); }});
    btnPrevPage.addEventListener("click", () => {{ if (state.currentPage > 1) state.currentPage--; render(); window.scrollTo({{top: 250, behavior: 'smooth'}}); }});
    btnNextPage.addEventListener("click", () => {{ state.currentPage++; render(); window.scrollTo({{top: 250, behavior: 'smooth'}}); }});
    btnLastPage.addEventListener("click", () => {{ 
      const totalItems = getFilteredData().length;
      const size = parseInt(state.pageSize, 10);
      state.currentPage = Math.ceil(totalItems / size);
      render();
      window.scrollTo({{top: 250, behavior: 'smooth'}});
    }});

    // Export to CSV
    exportCsvBtn.addEventListener("click", () => {{
      const filtered = getFilteredData();
      if (filtered.length === 0) {{
        alert("No records to export.");
        return;
      }}

      let csv = "Feature ID,Feature Name,Domain,SysReq ID,SysReq Title,SysReq Release,SysReq ASIL,SysReq FTTI,SwReq ID,SwReq Title,SwReq Release,SwReq ASIL,Allocated SWC,Execution Rate\\n";
      
      filtered.forEach(item => {{
        item.children.forEach(child => {{
          const row = [
            `"${{item.feature_id}}"`,
            `"${{item.feature_name.replace(/"/g, '""')}}"`,
            `"${{item.domain}}"`,
            `"${{item.sys_id}}"`,
            `"${{item.sys_title.replace(/"/g, '""')}}"`,
            `"${{item.sys_release}}"`,
            `"${{item.sys_asil}}"`,
            `"${{item.sys_ftti}}"`,
            `"${{child.id}}"`,
            `"${{child.title.replace(/"/g, '""')}}"`,
            `"${{child.planned_release || item.sys_release}}"`,
            `"${{child.asil || item.sys_asil}}"`,
            `"${{child.swc || ""}}"`,
            `"${{child.period || ""}}"`
          ];
          csv += row.join(",") + "\\n";
        }});
      }});

      const blob = new Blob([csv], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `Automotive_Requirements_Traceability_${{new Date().toISOString().slice(0,10)}}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }});

    // Initial load
    initDropdowns();
    render();
  </script>
</body>
</html>
"""

output_file = os.path.join(BASE_DIR, "requirements_traceability_matrix.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Interactive HTML Traceability Matrix successfully created at: {output_file}")
print(f"File size: {round(os.path.getsize(output_file) / 1024, 1)} KB")

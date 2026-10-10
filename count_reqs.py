import os, glob, re

sys_files = sorted(glob.glob('system_requirements/*.md'))

domain_map = {
    'ADAS': 'ADAS & Autonomous Driving',
    'PWR': 'Electric Powertrain & Energy Management',
    'CHS': 'Vehicle Motion & Chassis Control',
    'BDY': 'Body, Lighting & Restraints',
    'CPT': 'Digital Cockpit, HMI & Cabin Sensing',
    'TEL': 'Connectivity, Security & Diagnostics',
    'SEC': 'Connectivity, Security & Diagnostics',
    'DIA': 'Connectivity, Security & Diagnostics',
}

domain_counts = {}
for d in set(domain_map.values()):
    domain_counts[d] = {'features': 0, 'sys': 0, 'sw': 0}

feat_details = []

for sf in sys_files:
    feat_base = os.path.basename(sf).replace('_SysReq.md', '')
    sw_file = os.path.join('software_requirements', feat_base + '_SwReq.md')
    
    with open(sf, 'r', encoding='utf-8') as f:
        sys_matches = set(re.findall(r'SYS-[A-Z0-9]+-[0-9]+-[0-9]+', f.read()))
    
    sw_matches = set()
    if os.path.exists(sw_file):
        with open(sw_file, 'r', encoding='utf-8') as f:
            sw_matches = set(re.findall(r'SWR-[A-Z0-9]+-[0-9]+-[0-9]+', f.read()))
            
    prefix = feat_base.split('-')[1]
    domain_name = domain_map.get(prefix, 'Other')
    
    domain_counts[domain_name]['features'] += 1
    domain_counts[domain_name]['sys'] += len(sys_matches)
    domain_counts[domain_name]['sw'] += len(sw_matches)
    
    feat_details.append((feat_base, domain_name, len(sys_matches), len(sw_matches)))

print("DOMAIN BREAKDOWN:")
total_features = 0
total_sys = 0
total_sw = 0
for d in sorted(domain_counts.keys()):
    c = domain_counts[d]
    tot = c['sys'] + c['sw']
    total_features += c['features']
    total_sys += c['sys']
    total_sw += c['sw']
    print(f"- {d}: {c['features']} Features | {c['sys']} SYS_REQs | {c['sw']} SWR_REQs | Subtotal: {tot}")

print(f"\nOVERALL TOTALS:")
print(f"Total Features: {total_features}")
print(f"Total SYS_REQs: {total_sys}")
print(f"Total SWR_REQs: {total_sw}")
print(f"Grand Total Requirements: {total_sys + total_sw}")
print(f"Global Decomposition Ratio: 1 : {(total_sw / total_sys):.2f}")

print("\nTOP FEATURES BY VOLUME:")
for fb, dom, sc, swc in sorted(feat_details, key=lambda x: x[2]+x[3], reverse=True)[:10]:
    print(f"- {fb} ({dom}): {sc} SYS + {swc} SWR = {sc+swc} Reqs")

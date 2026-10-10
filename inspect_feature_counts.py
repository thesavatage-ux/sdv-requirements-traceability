import features_adas_full, features_pwr_full, features_chs_full, features_bdy_full, features_cpt_full, features_conn_full

modules = [
    ('ADAS', features_adas_full, 'adas_features'),
    ('PWR', features_pwr_full, 'full_pwr_features'),
    ('CHS', features_chs_full, 'full_chs_features'),
    ('BDY', features_bdy_full, 'full_bdy_features'),
    ('CPT', features_cpt_full, 'full_cpt_features'),
    ('CONN', features_conn_full, 'full_conn_features')
]

for name, mod, attr in modules:
    feats = getattr(mod, attr)
    print(f"=== {name} ({len(feats)} features) ===")
    for f in feats:
        s_count = len(f.get('sys_reqs', []))
        sw_count = len(f.get('sw_reqs', []))
        print(f"  {f['id']} ({f['name']}): {s_count} SYS, {sw_count} SWR")

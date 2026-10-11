"""WP2 robustness: do the parcel-level tests survive crop rotation? Same tests as parcel_resilience.py, but
(a) only seasons where the parcel was in cereals (CROME) in both t-1 and t, and
(b) effects absorbed within cell x season x crop (CROME LUCODE of season t), so parcels are compared with others
    growing the same crop in the same weather cell and season. CROME covers 2016-2025, so 2026 drops out."""
import os, numpy as np, pandas as pd
import parcel_resilience as pr

def main():
    p = pr.load(); p['D'] = pr.add_debt(p, pr.LAM)
    crop = pd.read_parquet(os.path.join(pr.D, 'parcels', 'parcel_panel.parquet'),
                           columns=['parcref'] + [f'crop_{y}' for y in range(2016, 2026)] + [f'cereal_{y}' for y in range(2016, 2026)])
    long = []
    for y in range(2016, 2026):
        long.append(pd.DataFrame({'parcref': crop.parcref, 'year': y, 'crop': crop[f'crop_{y}'], 'cereal': crop[f'cereal_{y}'].fillna(False)}))
    c = pd.concat(long); p = p.merge(c, on=['parcref', 'year'], how='inner')
    g = p.groupby('parcref')
    p['S_lag'] = g.S.shift(1); p['D_lag'] = g.D.shift(1); p['S_next'] = g.S.shift(-1); p['shock_next'] = g.shock.shift(-1)
    p['cereal_lag'] = g.cereal.shift(1); p['cereal_next'] = g.cereal.shift(-1)
    p['grp'] = p.cell_id_data.astype(str) + '_' + p.year.astype(str) + '_' + p.crop.astype(str)
    rows = []
    a = p[(p.cereal == True) & (p.cereal_lag == True)].dropna(subset=['S', 'S_lag', 'cell_id_data'])
    w = pr.within(a, ['S', 'S_lag'], 'grp'); b, se, pv, G = pr.ols_cluster(w.S, w[['S_lag']], a.cell_id_data)
    rows.append(('T1 legacy', b[0], se[0], pv[0], len(a)))
    s = a[a.shock]
    w = pr.within(s, ['S', 'S_lag'], 'grp'); b, se, pv, G = pr.ols_cluster(w.S, w[['S_lag']], s.cell_id_data)
    rows.append(('T2 hit harder', b[0], se[0], pv[0], len(s)))
    r = p[p.shock & (p.shock_next == False) & (p.cereal == True) & (p.cereal_next == True)].dropna(subset=['S', 'S_next', 'D_lag', 'cell_id_data']).copy()
    r['rebound'] = r.S_next - r.S
    w = pr.within(r, ['rebound', 'D_lag', 'S'], 'grp'); b, se, pv, G = pr.ols_cluster(w.rebound, w[['D_lag', 'S']], r.cell_id_data)
    rows.append(('T3 debt slows rebound', b[0], se[0], pv[0], len(r)))
    t = pd.DataFrame(rows, columns=['test', 'coef', 'se', 'p', 'n'])
    print(t.round(4).to_string(index=False))
    with open(os.path.join(pr.OUT, 'wp2_resilience_summary.md'), 'a') as fh:
        fh.write('\n## Robustness to crop rotation\n\nCereal in both seasons (CROME), effects absorbed within cell × season × crop; 2026 excluded (no CROME).\n\n'
                 + t.assign(coef=t.coef.round(3), se=t.se.round(3), p=t.p.map(lambda v: '<0.001' if v < 0.001 else f'{v:.3f}')).to_markdown(index=False) + '\n')

if __name__ == '__main__':
    main()

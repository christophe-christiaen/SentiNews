"""WP2 additions W1 and W2 (paper/outline.md, specified 17 October 2026 before running).

W1  Flood Zone 3 / deep peat vs other fields on the MODIS long-baseline panel (16-season normal, 2002-2026):
    stress gap within cell x season in shock and in other seasons; within-field carry-over (Anderson-Hsiao) per group.
W2  Sentinel-1 winter wetness -> crop condition: Sentinel-2 stress S on winter VH anomaly (per-orbit panel),
    2017-2025, field and cell x season effects, overall and in wet-shock winters; errors clustered by ERA5 cell.

Output  wp2_resilience/results/wp2_supporting.md, wp2_supporting.json
"""
import json, os
import numpy as np, pandas as pd
import parcel_resilience as pr
import within_field_check as wf
import modis_long_baseline_check as mlb

RES = os.path.join(pr.ROOT, 'wp2_resilience', 'results')


def w1():
    p = mlb.load()
    p = p[p.year >= 2002]
    r = pd.read_parquet(os.path.join(pr.D, 'parcels', 'parcel_risk.parquet'))
    r['fp'] = ((r.flood_zone.fillna(0).astype(int) == 3) | r.peat_class.fillna('').str.lower().str.contains('deep')).astype(float)
    p = p.merge(r[['parcref', 'fp']], on='parcref')
    out = {'fields': {'flood zone 3 or deep peat': int(p.drop_duplicates('parcref').fp.sum()),
                      'other': int((1 - p.drop_duplicates('parcref').fp).sum())}}
    a = p.dropna(subset=['S', 'cell_id_data']).copy()
    a['fp_shock'] = a.fp * a.shock
    wdm = pr.within(a, ['S', 'fp', 'fp_shock'], 'cy')
    b, se, pv, G = pr.ols_cluster(wdm.S, wdm[['fp', 'fp_shock']], a.cell_id_data)
    out['stress gap, other seasons (fp minus other)'] = dict(coef=float(b[0]), se=float(se[0]), p=float(pv[0]), n=int(len(a)))
    out['extra gap in shock seasons'] = dict(coef=float(b[1]), se=float(se[1]), p=float(pv[1]), n=int(len(a)))
    q = p.assign(dS=p.S - p.S_l1, dS_l1=p.S_l1 - p.S_l2)
    for lab, g in (('flood zone 3 or deep peat', 1.0), ('other', 0.0)):
        bq = q[q.fp == g].dropna(subset=['dS', 'dS_l1', 'S_l2', 'cell_id_data'])
        wq = pr.within(bq, ['dS', 'dS_l1', 'S_l2'], 'cy')
        out[f'carry-over within field (Anderson-Hsiao), {lab}'] = wf.iv(wq.dS, wq.dS_l1, wq.S_l2, bq.cell_id_data)
    return out


def w2():
    p = pr.load()[['parcref', 'year', 'S', 'cell_id_data']]
    s1 = pd.read_parquet(os.path.join(pr.D, 's1', 's1_orbit_parcel_season.parquet'), columns=['parcref', 'season', 'winter_vh_anom', 'wet_shock'])
    s1 = s1[s1.season <= 2025].rename(columns={'season': 'year'})
    p = p.merge(s1, on=['parcref', 'year']).dropna(subset=['S', 'winter_vh_anom', 'cell_id_data'])
    p['cy'] = p.cell_id_data.astype(str) + '_' + p.year.astype(str)
    p['wet_vh'] = p.winter_vh_anom * p.wet_shock.fillna(False).astype(float)
    out = {}
    wdm = wf.demean2(p, ['S', 'winter_vh_anom', 'wet_vh'])
    out['all winters: S per dB of winter VH anomaly'] = wf.ols(wdm.S, wdm[['winter_vh_anom', 'wet_vh']], p.cell_id_data)
    b, se, pv, G = pr.ols_cluster(wdm.S, wdm[['winter_vh_anom', 'wet_vh']], p.cell_id_data)
    out['extra slope in wet-shock winters'] = dict(coef=float(b[1]), se=float(se[1]), p=float(pv[1]), n=int(len(p)))
    return out


def main():
    res = {'W1_flood_peat': w1()}
    print('W1 done', flush=True)
    res['W2_sentinel1'] = w2()
    json.dump(res, open(os.path.join(RES, 'wp2_supporting.json'), 'w'), indent=1, default=float)
    f = lambda v: f"{v['coef']:+.3f} | {v['se']:.3f} | {v['p']:.3g} | {v['n']:,}"
    L = ['# WP2 additions: flood zone and peat, Sentinel-1 winter wetness', '',
         'Specified in paper/outline.md on 17 October 2026 before running. Errors clustered by ERA5 cell.', '',
         '## W1. Flood Zone 3 or deep peat vs other cereal fields (MODIS, 16-season normal, 2002–2026)', '',
         f"Fields: {res['W1_flood_peat']['fields']['flood zone 3 or deep peat']:,} in Flood Zone 3 or on deep peat; "
         f"{res['W1_flood_peat']['fields']['other']:,} other.", '',
         '| Measure | estimate | SE | p | n |', '|---|---|---|---|---|'] + \
        [f'| {k} | {f(v)} |' for k, v in res['W1_flood_peat'].items() if k != 'fields']
    L += ['', '## W2. Does winter radar wetness show up in the crop? (Sentinel-2 stress on Sentinel-1 winter VH, 2017–2025)', '',
          'Within each field (field and cell × season effects). Positive = wetter-than-usual winter radar goes with a '
          'better-than-usual crop for that field.', '', '| Measure | estimate | SE | p | n |', '|---|---|---|---|---|'] + \
         [f'| {k} | {f(v)} |' for k, v in res['W2_sentinel1'].items()]
    open(os.path.join(RES, 'wp2_supporting.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

"""W2-1b (wp2_resilience/results/w2_1b_landsat7_protocol.md, written before any diagnostic was run): why the Landsat
7-only version of the W2-1 carry-over tests disagrees with the all-sensor version.

D1 same fields and seasons; D2 all-sensor plus noise of L7's excess variance; D3a both windows present; D3b at least 12
baseline seasons; D4 tests outside the normal (2017-2023). Loader, lags and estimators as in W2-1.

Input   shared/data/landsat_parcels/landsat_<square>.csv (existing); weather as in W2-1
Output  wp2_resilience/results/w2_1b_landsat7.md, .json
"""
import json, os
import numpy as np, pandas as pd
import within_field_check as wf
import parcel_resilience as pr
import modis_long_baseline_check as mlb
from w2_1_landsat import load, RES

REF_ALL, REF_L7 = -0.020, -0.083
LAGCOLS = ['S_l1', 'S_l2', 'S_l3', 'S_next', 'shock_next', 'cy', 'D', 'D_l1']


def relag(p):
    p = p.drop(columns=[c for c in LAGCOLS if c in p.columns]).sort_values(['parcref', 'year']).reset_index(drop=True)
    p = wf.lags(p)
    p['D'] = pr.add_debt(p[['parcref', 'S']], 0.5); p['D_l1'] = p.groupby('parcref').D.shift(1)
    return p


def baseline_seasons(p):
    b = p[p.year.between(2001, 2016)]
    return b.groupby('parcref').july.count()


def main():
    out, desc = {}, {}
    pa = load((2001, 2016))
    p7 = load((2001, 2016), prefix='l7', years=range(2001, 2024))
    desc['baseline seasons, median (all-sensor, L7)'] = [float(baseline_seasons(pa).median()), float(baseline_seasons(p7).median())]
    t7 = p7[p7.year >= 2002]
    desc['L7 field-seasons 2002-2023 with both windows (share)'] = float((t7.july.notna() & t7.peak.notna()).mean())
    ta = pa[pa.year.between(2002, 2023)]
    desc['all-sensor field-seasons 2002-2023 with both windows (share)'] = float((ta.july.notna() & ta.peak.notna()).mean())

    # D1: identical field-seasons
    key = p7[['parcref', 'year', 'S']].rename(columns={'S': 'S7'})
    d1 = pa[pa.year <= 2023].merge(key, on=['parcref', 'year'], how='inner')
    d1 = d1[d1.parcref.isin(p7.dropna(subset=['S']).parcref.unique())]
    d1['S'] = d1.S.where(d1.S7.notna())
    d1 = relag(d1.drop(columns='S7'))
    mlb.run(d1[d1.year >= 2002].copy(), 'D1 · all-sensor on L7 field-seasons', out)
    print('D1 done', flush=True)

    # D2: excess noise of L7
    c = d1[['parcref', 'year', 'S']].merge(key, on=['parcref', 'year']).dropna(subset=['S', 'S7'])
    c = c[c.year.between(2002, 2023)]
    dm = lambda v: v - v.groupby(c.parcref).transform('mean')
    s2 = float(dm(c.S7).var() - dm(c.S).var())
    desc['D2 excess variance of L7 (within field)'] = s2
    if s2 > 0:
        d2 = d1.copy()
        rng = np.random.default_rng(30)
        d2['S'] = (d2.S + rng.normal(0, np.sqrt(s2), len(d2))).clip(-6, 6).where(d2.S.notna())
        d2 = relag(d2)
        mlb.run(d2[d2.year >= 2002].copy(), 'D2 · all-sensor plus L7 excess noise', out)
    print('D2 done', flush=True)

    # D3a: both windows present
    d3a = p7.copy(); d3a['S'] = d3a.S.where(d3a.july_z.notna() & d3a.peak_z.notna())
    d3a = relag(d3a)
    mlb.run(d3a[d3a.year >= 2002].copy(), 'D3a · L7, both windows', out)
    # D3b: at least 12 baseline seasons
    d3b = load((2001, 2016), prefix='l7', min_seasons=12, years=range(2001, 2024))
    desc['D3b fields with >= 12 L7 baseline seasons'] = int(d3b.dropna(subset=['S']).parcref.nunique())
    mlb.run(d3b[d3b.year >= 2002].copy(), 'D3b · L7, >= 12 baseline seasons', out)
    # D4: tests outside the normal
    mlb.run(p7[p7.year >= 2017].copy(), 'D4 · L7, tests 2017-2023', out)
    print('D3, D4 done', flush=True)

    g = lambda lab: out.get(f'{lab} | T1 | Anderson-Hsiao', {}).get('coef', np.nan)
    v = {k: g(k) for k in ('D1 · all-sensor on L7 field-seasons', 'D2 · all-sensor plus L7 excess noise', 'D3a · L7, both windows',
                           'D3b · L7, >= 12 baseline seasons', 'D4 · L7, tests 2017-2023')}
    k1, k2, k3a, k3b, k4 = v.keys()
    R1 = bool(abs(v[k1] - REF_ALL) <= 0.05)
    R2 = bool(np.isfinite(v[k2]) and abs(v[k2] - REF_L7) <= 0.03)
    R3 = {k: bool(abs(v[k] - REF_ALL) <= 0.05) for k in (k3a, k3b, k4)}
    concl = bool(R1 and (R2 or any(R3.values())))
    res = dict(anderson_hsiao_T1=v, R1_sample_not_cause=R1, R2_noise_reproduces=R2, R3_density_removes=R3, attributed_to_L7_data=concl,
               descriptive=desc, tests=out)
    json.dump(res, open(os.path.join(RES, 'w2_1b_landsat7.json'), 'w'), indent=1, default=float)

    L = ['# W2-1b: why the Landsat 7-only version disagrees', '',
         'Protocol: [w2_1b_landsat7_protocol.md](w2_1b_landsat7_protocol.md), written before any diagnostic was run. '
         f'Reference Anderson–Hsiao T1: all-sensor {REF_ALL:+.3f} (2002–2026), Landsat 7 only {REF_L7:+.3f} (2002–2023).', '',
         '| Version | test | estimator | coefficient | SE | p | n |', '|---|---|---|---|---|---|---|']
    for k, r in out.items():
        if 'without' in k:
            continue
        lab, t, e = k.split(' | ')
        L.append(f"| {lab} | {t} | {e} | {r['coef']:+.3f} | {r['se']:.3f} | {r['p']:.3g} | {r['n']:,} |")
    L += ['', '## Descriptive', ''] + [f'- {k}: {val}' for k, val in desc.items()]
    L += ['', '## Reading (rules fixed in advance; Anderson–Hsiao T1)', '',
          f'- **R1 · sample and period not the cause** (D1 within ±0.05 of {REF_ALL:+.3f}): D1 {v[k1]:+.3f} → **{"yes" if R1 else "no"}**.',
          f'- **R2 · L7-sized noise reproduces the gap** (D2 within ±0.03 of {REF_L7:+.3f}): D2 ' + (f'{v[k2]:+.3f}' if np.isfinite(v[k2]) else 'not applicable') + f' → **{"yes" if R2 else "no"}**.']
    for k in (k3a, k3b, k4):
        L.append(f'- **R3 · {k.split(" · ")[1]} removes the gap** (within ±0.05 of {REF_ALL:+.3f}): {v[k]:+.3f} → **{"yes" if R3[k] else "no"}**.')
    L += ['', f'**Conclusion:** ' + ('the flag is attributed to Landsat 7\'s data, not to the sensor or to carry-over.' if concl
                                     else 'the limit stands as stated in W2-1.')]
    open(os.path.join(RES, 'w2_1b_landsat7.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L[-8:]))


if __name__ == '__main__':
    main()

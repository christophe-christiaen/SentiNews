"""Addendum 6 Part F: GFM validation within Flood Zone 3 and without repeat-flag parcels (protocol:
w3_z_addendum6_hazards_protocol.md, record row of 4 November 2026, part B). Reads the merged tables written by
w3_z_gfm_validate.py.

Output: wp3_elms_effect/results/w3_z_gfm_validation_strata.md and .json (aggregates only; public).
Contains modified Copernicus Emergency Management Service information 2015-2026. EA data: Open Government Licence.
"""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w3_z_gfm_validate as v

RES, DATA, ROOT = v.RES, v.DATA, v.ROOT
REPEAT, DRAWS, SQ = 5, 2000, 10_000
WINTERS = ['all', 2016, 2020, 2024]
VERS = {'point': ('pt_obs_days', 'pt_flood_days'), 'outline': ('ol_obs_days', 'ol_flood_days')}


def ratio(n):
    """n: [flagged in EA, flagged, unflagged observed in EA, unflagged observed]."""
    return (n[..., 0] / n[..., 1]) / (n[..., 2] / n[..., 3])


def table(d, obs, fl, rng):
    ob, fd = d[obs] > 0, d[fl] > 0
    x = pd.DataFrame({'sq': d.sq, 'a': fd & d.ea, 'st': fd & d.strict, 'b': fd, 'c': ob & ~fd & d.ea, 'd': ob & ~fd,
                      'e': d.ea & ob, 'f': d.ea & fd}).groupby('sq').sum()
    n = x[['a', 'b', 'c', 'd']].values.astype(float)
    t = n.sum(0)
    idx = rng.integers(0, len(n), (DRAWS, len(n)))
    with np.errstate(divide='ignore', invalid='ignore'):
        rs = ratio(n[idx].sum(1)); r = float(ratio(t))
    lo, hi = np.nanpercentile(rs, [2.5, 97.5]) if np.isfinite(rs).any() else (np.nan, np.nan)
    return dict(parcel_seasons=len(d), observed=int(ob.sum()), flooded=int(t[1]), flooded_in_ea=t[0] / max(t[1], 1),
                flooded_in_ea_strict=x.st.sum() / max(t[1], 1), base_rate=t[2] / max(t[3], 1), ratio=r, ratio_lo=float(lo),
                ratio_hi=float(hi), undefined_draws=float(np.mean(~np.isfinite(rs))), ea_observed=int(x.e.sum()),
                ea_flooded_share=x.f.sum() / max(x.e.sum(), 1), squares=len(n))


def main():
    rng = np.random.default_rng(20261104)
    c = pd.read_parquet(os.path.join(DATA, 'w3_z_gfm_parcel_season.parquet'))
    e = pd.read_parquet(os.path.join(DATA, 'w3_z_gfm_events.parquet'))
    h, _ = v.ea_hits()
    c = c.merge(h[['parcref', 'season']].drop_duplicates().assign(ea=True), on=['parcref', 'season'], how='left')
    c['ea'] = c.ea.fillna(False).astype(bool)
    P = pd.read_parquet(os.path.join(ROOT, 'shared', 'data', 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y'])
    P['sq'] = (P.x // SQ).astype(int) * 100_000 + (P.y // SQ).astype(int)
    r = pd.read_parquet(os.path.join(ROOT, 'shared', 'data', 'parcels', 'parcel_risk.parquet'), columns=['parcref', 'flood_zone'])
    c = c.merge(P[['parcref', 'sq']], on='parcref').merge(r, on='parcref', how='left')
    s = e.merge(h, on=['parcref', 'season'])
    s = s[(s.date >= s.start_date) & (s.date <= s.end_date + v.LAG)][['parcref', 'season', 'version']].drop_duplicates()
    rows = []
    for ver, (obs, fl) in VERS.items():
        d = c[c[obs].notna()]
        d = d.merge(s[s.version == ver][['parcref', 'season']].assign(strict=True), on=['parcref', 'season'], how='left')
        d['strict'] = d.strict.fillna(False).astype(bool)
        winters = (d[fl] > 0).groupby(d.parcref).transform('sum')
        for name, sub in (('Flood Zone 3', d[d.flood_zone.astype(str).isin(['3', '3.0'])]), ('Without repeat-flag parcels', d[winters < REPEAT])):
            for w in WINTERS:
                rows.append(dict(version=ver, stratum=name, winter=w, **table(sub if w == 'all' else sub[sub.season == w], obs, fl, rng)))
    R = pd.DataFrame(rows)
    json.dump(R.to_dict('records'), open(os.path.join(RES, 'w3_z_gfm_validation_strata.json'), 'w'), indent=1, default=float)
    pc = lambda x, k=1: '' if pd.isna(x) else f'{100 * x:.{k}f}%'
    L = ['# Addendum 6 Part F: GFM validation within Flood Zone 3 and without repeat-flag parcels', '',
         'Protocol: [w3_z_addendum6_hazards_protocol.md](w3_z_addendum6_hazards_protocol.md), record row of 4 November 2026, part B. '
         'Aggregates only. Ratio: flagged share inside a same-winter EA outline over the base rate; 95% interval by bootstrap over '
         '10 km squares. Neither table measures GFM\'s false-alarm rate. Winters are labelled by the March year.', '',
         'Contains modified Copernicus Emergency Management Service information 2015–2026. EA Recorded Flood Outlines: Open Government Licence.', '']
    for st in R.stratum.unique():
        for ver in VERS:
            L += [f'## {st}, {ver} version', '', '| Winter | Observed | Flagged | Flagged inside EA outline | Stricter | Base rate | Ratio (95% interval) | Inside outline, observed | Of those, flagged |',
                  '|---|---|---|---|---|---|---|---|---|']
            for x in R[(R.stratum == st) & (R.version == ver)].itertuples():
                L.append(f'| {x.winter} | {x.observed:,} | {x.flooded:,} | {pc(x.flooded_in_ea)} | {pc(x.flooded_in_ea_strict)} | {pc(x.base_rate, 2)} | '
                         f'{x.ratio:.1f} ({x.ratio_lo:.1f}–{x.ratio_hi:.1f}) | {x.ea_observed:,} | {pc(x.ea_flooded_share)} |')
            L.append('')
    open(os.path.join(RES, 'w3_z_gfm_validation_strata.md'), 'w').write('\n'.join(L))
    print(R.drop(columns=['parcel_seasons', 'squares']).round(4).to_string())


if __name__ == '__main__':
    main()

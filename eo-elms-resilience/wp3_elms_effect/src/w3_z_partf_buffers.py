"""Addendum 6 Part F follow-up: do buffer strips carry a wet-winter cost? (protocol: w3_z_addendum6_hazards_protocol.md,
record row of 4 November 2026; post hoc). Design 2 within agreements decides; design 3 within CS contracts is reported.

Output: wp3_elms_effect/results/w3_z_partf_buffers.md, .json (aggregates only).
"""
import json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
import wp3_within_cohort as wc
from w3_z_partf import members, S

DRAWS = 2000


def long_panel(d, keep, buf, extra=None):
    Y, out = d.Y['ndvi_july_z'], []
    for g in sorted(set(d.G[keep]) & set(S)):
        idx = np.flatnonzero(keep & (d.G == g)); jb = g - 1 - S[0]
        if jb < 0: continue
        for t in S:
            if t == g - 1: continue
            dy = Y[idx, t - S[0]] - Y[idx, jb]; ok = ~np.isnan(dy)
            df = dict(i=idx[ok], g=g, t=t, dy=dy[ok], buf=buf[idx[ok]], cell=d.cell[idx[ok]])
            out.append(pd.DataFrame(df))
    x = pd.concat(out, ignore_index=True); x['e'] = x.t - x.g
    if extra is not None: x['contract'] = extra[x.i.values]
    return x


def contrast(x, by, wet, rng):
    s = x.groupby(by + ['buf']).dy.agg(['size', 'sum']).unstack('buf').dropna()
    s.columns = ['no', 'so', 'nb', 'sb']; s = s.reset_index()
    if s.empty: return None
    s['tau'] = s.sb / s.nb - s.so / s.no
    s['wet'] = wet.reindex(pd.MultiIndex.from_arrays([s.cell, s.t])).fillna(False).astype(bool).values
    s['A'], s['W'] = s.tau * s.nb, s.nb
    p = s.pivot_table(index='cell', columns='wet', values=['A', 'W'], aggfunc='sum', fill_value=0)
    if ('A', True) not in p or ('A', False) not in p: return None
    a1, w1, a0, w0 = (p[k].values.astype(float) for k in [('A', True), ('W', True), ('A', False), ('W', False)])
    th = a1.sum() / w1.sum() - a0.sum() / w0.sum()
    n = len(p); D = rng.multinomial(n, np.ones(n) / n, DRAWS).astype(float)
    with np.errstate(all='ignore'):
        b = (D @ a1) / (D @ w1) - (D @ a0) / (D @ w0)
    lo, hi = np.nanpercentile(b, [2.5, 97.5])
    return dict(est=float(th), se=float(np.nanstd(b)), lo=float(lo), hi=float(hi), wet_effect=float(a1.sum() / w1.sum()), other_effect=float(a0.sum() / w0.sum()),
                n_buffer=int(s.nb.sum()), n_other=int(s.no.sum()), n_wet=int(w1.sum()), clusters=n, strata=len(s))


def windows(x, by, wet, rng):
    post, pre = x[x.e >= 0], x[np.isin(x.e, wc.PRE) & (x.t <= 2020)]
    return dict(after=contrast(post, by, wet, rng), placebo=contrast(pre, by, wet, rng))


def main():
    rng = np.random.default_rng(20261104)
    d = w.Data(); t = d.t
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    M = ms.in_matched_sample.values
    buf = members(t)['Buffer strips']
    sh = w.shock_table()
    wet = pd.Series(sh.wet.reindex(pd.MultiIndex.from_product([d.cells, S])).fillna(False).values,
                    index=pd.MultiIndex.from_product([np.arange(len(d.cells)), S]))
    fp = (t.fz3 | t.deep_peat).values
    keep = M & (d.G > 0) & (d.G <= 2026)
    res = {'design2': windows(long_panel(d, keep, buf), ['g', 't', 'cell'], wet, rng),
           'design2_fz3_peat': windows(long_panel(d, keep & fp, buf), ['g', 't', 'cell'], wet, rng),
           'design2_neither': windows(long_panel(d, keep & ~fp, buf), ['g', 't', 'cell'], wet, rng)}
    o = pd.read_csv(os.path.join(w.ROOT, 'shared', 'data', 'schemes', 'national', 'cs_options.csv'), dtype=str, usecols=['PARCREF', 'CONTRACT_ID', 'STARTDATE'])
    o['start'] = pd.to_datetime(o.STARTDATE, errors='coerce')
    o = o[o.start >= '2021-01-01'].sort_values('start').drop_duplicates('PARCREF')
    con = pd.Series(o.CONTRACT_ID.values, index=o.PARCREF.values).reindex(t.parcref.values)
    code = pd.factorize(con)[0]
    res['design3'] = windows(long_panel(d, keep & (code >= 0), buf, code), ['contract', 'g', 't', 'cell'], wet, rng)
    a, p = res['design2']['after'], res['design2']['placebo']
    res['design2_holds'] = bool(a and a['hi'] < 0); res['placebo_includes_zero'] = bool(p and p['lo'] <= 0 <= p['hi'])
    res['cost_indicated'] = res['design2_holds'] and res['placebo_includes_zero']
    json.dump(res, open(os.path.join(w.RES, 'w3_z_partf_buffers.json'), 'w'), indent=1, default=float)
    c = lambda x: '' if not x else f"{x['est']:+.3f} ({x['lo']:+.3f}, {x['hi']:+.3f})"
    L = ['# Addendum 6 Part F follow-up: buffer strips in wet winters', '',
         'Protocol: [w3_z_addendum6_hazards_protocol.md](w3_z_addendum6_hazards_protocol.md), record row of 4 November 2026. Post hoc and exploratory: '
         'buffer strips were picked out of 20 contrasts. July NDVI z-score; wet-shock seasons minus other seasons; 95% percentile bootstrap over ERA5 cells.', '',
         f"**Cost indicated (registered reading): {'yes' if res['cost_indicated'] else 'no'}.**", '',
         '| Design | Contrast | Placebo | Buffer parcel-seasons | Other parcel-seasons | Effect in wet seasons | Effect in other seasons |', '|---|---|---|---|---|---|---|']
    for k, n in [('design2', 'Design 2: within agreements (decides)'), ('design2_fz3_peat', 'Design 2, Flood Zone 3 or deep peat'), ('design2_neither', 'Design 2, neither'), ('design3', 'Design 3: within CS contract')]:
        r = res[k]; x = r['after']
        L.append(f"| {n} | {c(x)} | {c(r['placebo'])} | {x['n_buffer'] if x else 0:,} | {x['n_other'] if x else 0:,} | {x['wet_effect'] if x else float('nan'):+.3f} | {x['other_effect'] if x else float('nan'):+.3f} |")
    open(os.path.join(w.RES, 'w3_z_partf_buffers.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

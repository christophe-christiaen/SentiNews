"""WP3 exploratory X2 (decisions record, 18 October 2026, specified before running): the frozen-plan test with
long-baseline normals. Same estimator, matched sample, shocks and seasons; only the outcome changes:
  V0 Sentinel-2 July NDVI z against 2017-2020 (the frozen outcome)
  V1 MODIS July NDVI z against each field's 2017-2020 seasons
  V2 MODIS July NDVI z against each field's 2001-2016 seasons
Per version: H1 and components, placebo H1 (entry two seasons early), event-study pre-trend Wald tests (e = -4..-1).

Output  wp3_elms_effect/results/wp3_x2_long_baseline.md, .json
"""
import glob, json, os
import numpy as np, pandas as pd
from scipy import stats
import wp3_did as w

OUT = os.path.join(w.W3, 'results')


def modis_july(t, base):
    m = pd.concat([pd.read_csv(f, usecols=lambda c: c == 'parcref' or c.startswith('july_'))
                   for f in sorted(glob.glob(os.path.join(w.D, 'modis_parcels', 'modis_*.csv')))], ignore_index=True)
    m = m.drop_duplicates('parcref').set_index('parcref').reindex(t.parcref)
    yrs = [int(c[-4:]) for c in m.columns]
    v = m.values.astype('float64')
    b = v[:, [i for i, y in enumerate(yrs) if base[0] <= y <= base[1]]]
    mu, sd = np.nanmean(b, 1, keepdims=True), np.nanstd(b, 1, ddof=1, keepdims=True)
    z = (v - mu) / np.where(sd > 1e-4, sd, np.nan)
    return np.column_stack([z[:, yrs.index(s)] if s in yrs else np.full(len(t), np.nan) for s in w.SEASONS])


def version(d, M, Y, label):
    E = d.est(Ymat=Y, pmask=M)
    W = w.h1(E)
    th, V, G, _ = E.run(W)
    res = {'H1': w.row('H1 shock minus non-shock', th, V, 0, G, w.n_obs(E, W[3])),
           'shock': w.row('effect in shock seasons', th, V, 1, G), 'calm': w.row('effect in non-shock seasons', th, V, 2, G),
           'all': w.row('effect, all post-entry seasons', th, V, 3, G)}
    Gp = np.where(d.G > 0, d.G - 2, 0); tmax = np.where(d.G > 0, d.G, 9999)
    Ep = d.est(Ymat=Y, G=Gp, tmax=tmax, pmask=M)
    a, Va, Ga, _ = Ep.run(w.h1(Ep)[:1])
    res['placebo'] = w.row('placebo H1, entry two seasons early', a, Va, 0, Ga)
    TR = E.TR; es = list(range(-4, 4))
    We = [E.weights(TR.e == e) for e in es] + [E.weights((TR.e == e) & TR.shock, (TR.e == e) & ~TR.shock) for e in es]
    the, Ve, _, _ = E.run(We)
    def wald(ix):
        b = the[ix]; v = Ve[np.ix_(ix, ix)]
        ok = np.isfinite(b) & (np.diag(v) > 0); b, v = b[ok], v[np.ix_(ok, ok)]
        s = float(b @ np.linalg.pinv(v) @ b); return dict(stat=s, df=int(ok.sum()), p=float(stats.chi2.sf(s, ok.sum())))
    res['pretrend_effect'], res['pretrend_contrast'] = wald([0, 1, 2, 3]), wald([8, 9, 10, 11])
    res['event'] = [dict(e=e, att=float(the[k]), se=float(np.sqrt(Ve[k, k]))) for k, e in enumerate(es)]
    w.log(label, 'H1', round(res['H1']['est'], 4), 'placebo', round(res['placebo']['est'], 4), 'pretrend p', round(res['pretrend_effect']['p'], 4))
    return res


def main():
    d = w.Data()
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet')).set_index('parcref').in_matched_sample
    M = ms.reindex(d.t.parcref).fillna(False).values.astype(bool)
    vers = {'V0 · Sentinel-2, normal 2017–2020 (frozen)': d.Y['ndvi_july_z'],
            'V1 · MODIS, normal 2017–2020': modis_july(d.t, (2017, 2020)),
            'V2 · MODIS, normal 2001–2016': modis_july(d.t, (2001, 2016))}
    out = {k: version(d, M, Y, k) for k, Y in vers.items()}
    v1, v2 = out['V1 · MODIS, normal 2017–2020'], out['V2 · MODIS, normal 2001–2016']
    shrink = abs(v2['placebo']['est']) <= 0.5 * abs(v1['placebo']['est'])
    ci0 = v2['placebo']['lo'] <= 0 <= v2['placebo']['hi']
    pt = v1['pretrend_effect']['p'] < 0.05 and v2['pretrend_effect']['p'] >= 0.05
    out['reading'] = dict(placebo_shrinks_by_half=bool(shrink), placebo_ci_includes_zero=bool(ci0), pretrend_passes_in_V2=bool(pt),
                          baseline_mechanism_supported=bool((shrink and ci0) or pt))
    json.dump(out, open(os.path.join(OUT, 'wp3_x2_long_baseline.json'), 'w'), indent=1, default=float)
    f = lambda r: f"{r['est']:+.3f} ({r['se']:.3f})"
    L = ['# WP3 X2: the frozen-plan test with long-baseline normals (exploratory)', '',
         'Specified in the decisions record before running. Frozen-plan estimator, matched sample, main shock definition; '
         'only the outcome changes. Estimates in SD of each field\'s normal; SE clustered by ERA5 cell.', '',
         '| Version | H1 (shock − non-shock) | effect, shock seasons | effect, other seasons | placebo H1 (entry 2 seasons early) | pre-trend p (effect) | pre-trend p (contrast) |',
         '|---|---|---|---|---|---|---|']
    for k in vers:
        r = out[k]
        L.append(f"| {k} | {f(r['H1'])} | {f(r['shock'])} | {f(r['calm'])} | {f(r['placebo'])} | {r['pretrend_effect']['p']:.3g} | {r['pretrend_contrast']['p']:.3g} |")
    L += ['', '## Event study (effect by event time, before entry)', '', '| Version | ' + ' | '.join(f'e = {e}' for e in range(-4, 0)) + ' |', '|---' * 5 + '|']
    for k in vers:
        L.append(f'| {k} | ' + ' | '.join(f"{x['att']:+.3f}" for x in out[k]['event'][:4]) + ' |')
    rd = out['reading']
    L += ['', '## Reading (fixed in advance)', '',
          f"- Placebo from V1 to V2: {v1['placebo']['est']:+.3f} → {v2['placebo']['est']:+.3f}; shrinks by half: "
          f"{'yes' if rd['placebo_shrinks_by_half'] else 'no'}; V2 interval includes zero: {'yes' if rd['placebo_ci_includes_zero'] else 'no'}.",
          f"- Pre-trend test on the effect: V1 p = {v1['pretrend_effect']['p']:.3g}, V2 p = {v2['pretrend_effect']['p']:.3g}; "
          f"passes only in V2: {'yes' if rd['pretrend_passes_in_V2'] else 'no'}.",
          '- **' + ('The baseline mechanism is supported:** the failed placebo was largely the short normal.' if rd['baseline_mechanism_supported']
                    else 'The baseline mechanism is not supported:** the failed placebo is read as selection, not the short normal.') ,
          '', f"Long-baseline H1 (V2, exploratory, beside the frozen estimate): {f(v2['H1'])}.", '',
          'Limits: MODIS pixels (250 m) mix neighbouring fields; a 2001–2016 normal can drift by 2017–2026.']
    open(os.path.join(OUT, 'wp3_x2_long_baseline.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

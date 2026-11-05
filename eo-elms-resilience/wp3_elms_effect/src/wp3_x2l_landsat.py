"""WP3 X2-L (protocol: wp3_x2l_landsat_protocol.md): H1 with a Landsat 30 m field-centre long baseline, as X2 with MODIS.
Same estimator, shocks and seasons; only the outcome changes. X2's matched sample decides; the E3 matched sample is reported.

Input   as wp3_did.py, plus matched_sample.parquet, matched_sample_e3.parquet, shared/data/landsat_parcels/landsat_*.csv
Output  wp3_elms_effect/results/wp3_x2l_landsat.md, .json (aggregates only)
"""
import glob, json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
import wp3_within_cohort as wc
import wp3_trend_adjusted as ta
from wp3_x2_long_baseline import modis_july, version

OUT = os.path.join(w.W3, 'results')
X2 = dict(H1=0.104, placebo=0.061)
DIFF = 0.05


def landsat_july(t, base, min_seasons, prefix=''):
    m = pd.concat([pd.read_csv(f, usecols=lambda c: c == 'parcref' or c.startswith(prefix + 'july_'))
                   for f in sorted(glob.glob(os.path.join(w.D, 'landsat_parcels', 'landsat_*.csv')))], ignore_index=True)
    m = m.drop_duplicates('parcref').set_index('parcref').reindex(t.parcref)
    yrs = [int(c[-4:]) for c in m.columns]
    v = m.values.astype('float64')
    b = v[:, [i for i, y in enumerate(yrs) if base[0] <= y <= base[1]]]
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        mu, sd = np.nanmean(b, 1, keepdims=True), np.nanstd(b, 1, ddof=1, keepdims=True)
    n = (~np.isnan(b)).sum(1, keepdims=True)
    mu, sd = np.where(n >= min_seasons, mu, np.nan), np.where(n >= min_seasons, sd, np.nan)
    z = (v - mu) / np.where(sd > 1e-4, sd, np.nan)
    return np.column_stack([z[:, yrs.index(s)] if s in yrs else np.full(len(t), np.nan) for s in w.SEASONS])


def extras(d, M, Y):
    """Trend-adjusted, within cohort and wet seasons dropped: reported, do not decide."""
    Eu = d.est(Ymat=Y, pmask=M, universal=True)
    Wt = ta.contrasts(Eu, 'H1')
    th, V, G, _ = Eu.run(Wt)
    out = {'trend_before': w.row('', th, V, 0, G), 'trend_after': w.row('', th, V, 1, G), 'trend_adjusted': w.row('', th, V, 2, G)}
    TR = Eu.TR
    def wcon(win):
        v, k = wc.within(Eu, win & TR.shock.values, win & ~TR.shock.values, ['g'])
        a, Va, Ga, _ = Eu.run([v])
        return w.row('', a, Va, 0, Ga) | dict(cohorts=k)
    out['within'] = wcon(TR.e.values >= 0)
    out['within_before'] = wcon(np.isin(TR.e.values, wc.PRE) & (TR.t.values <= 2020))
    E = d.est(Ymat=Y, pmask=M)
    p = (E.TR.e.values >= 0) & ~E.TR.wet.values
    a, Va, Ga, _ = E.run([E.weights(p & E.TR.shock.values, p & ~E.TR.shock.values)])
    out['no_wet'] = w.row('', a, Va, 0, Ga)
    Gp, tmax = np.where(d.G > 0, d.G - 2, 0), np.where(d.G > 0, d.G, 9999)
    Ep = d.est(Ymat=Y, G=Gp, tmax=tmax, pmask=M)
    q = (Ep.TR.e.values >= 0) & ~Ep.TR.wet.values
    a, Va, Ga, _ = Ep.run([Ep.weights(q & Ep.TR.shock.values, q & ~Ep.TR.shock.values)])
    out['no_wet_placebo'] = w.row('', a, Va, 0, Ga)
    return out


def l7(d, M, Y):
    S = range(2017, 2024)
    E = d.est(Ymat=Y, pmask=M, seasons=S)
    th, V, G, _ = E.run(w.h1(E)[:1])
    r = w.row('', th, V, 0, G, w.n_obs(E, w.h1(E)[3]))
    Gp, tmax = np.where(d.G > 0, d.G - 2, 0), np.where(d.G > 0, d.G, 9999)
    Ep = d.est(Ymat=Y, G=Gp, tmax=tmax, pmask=M, seasons=S)
    a, Va, Ga, _ = Ep.run(w.h1(Ep)[:1])
    return dict(H1=r, placebo=w.row('', a, Va, 0, Ga))


def coverage(d, M, Y):
    sh = w.shock_table(**w.MAIN_SHOCK).shock.reindex(pd.MultiIndex.from_product([d.cells, w.SEASONS])).fillna(False).values.reshape(len(d.cells), len(w.SEASONS))[d.cell].astype(bool)
    rows = []
    for lab, m in (('treated', M & (d.G > 0)), ('never treated', M & (d.G == 0))):
        for wv, wn in ((True, 'shock'), (False, 'other')):
            mask = np.zeros_like(sh); mask[np.ix_(m, range(9))] = True; mask &= sh == wv
            rows.append(dict(group=lab, season=wn, parcel_seasons=int(mask.sum()), share=float((~np.isnan(Y[mask])).mean())))
    return rows


def main():
    d = w.Data(); t = d.t
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet')).set_index('parcref').in_matched_sample
    M = ms.reindex(t.parcref).fillna(False).values.astype(bool)
    e3 = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (e3.parcref.values == t.parcref.values).all()
    ME = e3.in_matched_sample.values
    L1, L2 = landsat_july(t, (2017, 2020), 3), landsat_july(t, (2001, 2016), 8)
    V2 = modis_july(t, (2001, 2016))
    vers = {'V0 · Sentinel-2, normal 2017–2020 (frozen)': d.Y['ndvi_july_z'], 'V2 · MODIS, normal 2001–2016': V2,
            'L1 · Landsat, normal 2017–2020': L1, 'L2 · Landsat, normal 2001–2016': L2}
    main_ = {k: version(d, M, Y, k) for k, Y in vers.items()}
    side = {k: version(d, ME, Y, 'E3 ' + k) for k, Y in vers.items()}
    v2, l1, l2, v0 = (main_[k] for k in ('V2 · MODIS, normal 2001–2016', 'L1 · Landsat, normal 2017–2020', 'L2 · Landsat, normal 2001–2016', 'V0 · Sentinel-2, normal 2017–2020 (frozen)'))
    rep = dict(H1=v2['H1']['est'] - X2['H1'], placebo=v2['placebo']['est'] - X2['placebo'])
    rep['within_0005'] = bool(abs(rep['H1']) <= .005 and abs(rep['placebo']) <= .005)
    pix = bool(abs(l2['H1']['est'] - v2['H1']['est']) > DIFF or abs(l2['placebo']['est'] - v2['placebo']['est']) > DIFF)
    shrink = abs(l2['placebo']['est']) <= .5 * abs(l1['placebo']['est'])
    ci0 = l2['placebo']['lo'] <= 0 <= l2['placebo']['hi']
    pt = l1['pretrend_effect']['p'] < .05 and l2['pretrend_effect']['p'] >= .05
    base = bool((shrink and ci0) or pt)
    cush = bool(l2['H1']['lo'] > 0 and ci0)
    ex = {'L2': extras(d, M, L2), 'V0': extras(d, M, d.Y['ndvi_july_z']), 'V2': extras(d, M, V2)}
    seven = l7(d, M, landsat_july(t, (2001, 2016), 8, prefix='l7'))
    cov = {k: coverage(d, M, Y) for k, Y in (('L2', L2), ('V2 MODIS', V2), ('V0 Sentinel-2', d.Y['ndvi_july_z']))}
    era = {k: {int(s): float(np.nanmean(~np.isnan(L2[M][:, j]))) for j, s in enumerate(w.SEASONS)} for k in ['L2']}
    json.dump(dict(main=main_, e3=side, reproduction=rep, reading=dict(pixel_size_matters=pix, placebo_shrinks_by_half=bool(shrink), placebo_ci_includes_zero=bool(ci0), pretrend_passes_only_in_L2=bool(pt),
                                                                       baseline_mechanism_supported=base, cushion_holds_at_field_scale=cush),
                   extras=ex, landsat7=seven, coverage=cov, share_with_value_by_season=era), open(os.path.join(OUT, 'wp3_x2l_landsat.json'), 'w'), indent=1, default=float)
    f = lambda r: f"{r['est']:+.3f} ({r['lo']:+.3f}, {r['hi']:+.3f})"
    yn = lambda b: 'yes' if b else 'no'
    L = ['# X2-L: the drought test with a Landsat long baseline (exploratory)', '',
         'Protocol: [wp3_x2l_landsat_protocol.md](wp3_x2l_landsat_protocol.md). Frozen-plan estimator, main dry-or-heat shock, seasons 2017–2025; only the outcome changes. Estimates in SD of each field\'s normal, (95% interval); SE clustered by ERA5 cell. Reported beside the frozen H1, never instead of it.', '',
         f"**Reproduction:** recomputed MODIS H1 {v2['H1']['est']:+.3f} and placebo {v2['placebo']['est']:+.3f}, against X2's +0.104 and +0.061; within 0.005: {yn(rep['within_0005'])}.", '',
         "## X2's matched sample (decides)", '', '| Version | H1 | Placebo | Placebo ÷ H1 | Effect, shock seasons | Effect, other seasons | Pre-trend p (effect) | Pre-trend p (contrast) | Parcel-seasons |', '|---|---|---|---:|---:|---:|---:|---:|---:|']
    row = lambda k, r: f"| {k} | {f(r['H1'])} | {f(r['placebo'])} | {r['placebo']['est'] / r['H1']['est']:.0%} | {r['shock']['est']:+.3f} | {r['calm']['est']:+.3f} | {r['pretrend_effect']['p']:.3g} | {r['pretrend_contrast']['p']:.3g} | {r['H1']['n']:,} |"
    L += [row(k, main_[k]) for k in vers]
    L += ['', '## E3 matched sample (reported)', '', '| Version | H1 | Placebo | Placebo ÷ H1 | Effect, shock seasons | Effect, other seasons | Pre-trend p (effect) | Pre-trend p (contrast) | Parcel-seasons |', '|---|---|---|---:|---:|---:|---:|---:|---:|']
    L += [row(k, side[k]) for k in vers]
    L += ['', '## Event study (effect by event time, before entry)', '', '| Version | ' + ' | '.join(f'e = {e}' for e in range(-4, 0)) + ' |', '|---' * 5 + '|']
    L += [f'| {k} | ' + ' | '.join(f"{x['att']:+.3f}" for x in main_[k]['event'][:4]) + ' |' for k in vers]
    L += ['', '## Reading (fixed in advance)', '',
          f"1. **Pixel size matters** (L2 and MODIS differ by more than {DIFF} SD in H1 or placebo): {yn(pix)}. H1 {l2['H1']['est']:+.3f} against {v2['H1']['est']:+.3f}; placebo {l2['placebo']['est']:+.3f} against {v2['placebo']['est']:+.3f}.",
          f"2. **Baseline mechanism supported:** {yn(base)}. Placebo from L1 to L2: {l1['placebo']['est']:+.3f} → {l2['placebo']['est']:+.3f}; shrinks by half: {yn(shrink)}; L2 interval includes zero: {yn(ci0)}; pre-trend p {l1['pretrend_effect']['p']:.3g} → {l2['pretrend_effect']['p']:.3g}, passes only in L2: {yn(pt)}.",
          f"3. **Drought cushion holds at field scale:** {yn(cush)}.", '',
          '## Reported, does not decide', '', '| Version | Before entry | After entry | Trend-adjusted | Within cohort | Within cohort, before entry | H1, wet seasons dropped | Its placebo |', '|---|---|---|---|---|---|---|---|']
    for k, x in ex.items():
        L.append(f"| {k} | {f(x['trend_before'])} | {f(x['trend_after'])} | {f(x['trend_adjusted'])} | {f(x['within'])} | {f(x['within_before'])} | {f(x['no_wet'])} | {f(x['no_wet_placebo'])} |")
    L += ['', f"**Landsat 7 only,** normal 2001–2016, seasons 2017–2023: H1 {f(seven['H1'])}, placebo {f(seven['placebo'])}, {seven['H1']['n']:,} parcel-seasons. Stops before most treated fields enter.", '',
          '## Coverage: share of parcel-seasons with a value, 2017–2025', '', '| Source | Group | Season | Parcel-seasons | With a value |', '|---|---|---|---:|---:|']
    for k, rows in cov.items():
        L += [f"| {k} | {x['group']} | {x['season']} | {x['parcel_seasons']:,} | {x['share']:.1%} |" for x in rows]
    L += ['', 'L2 share with a value by season: ' + ', '.join(f'{s}: {v:.0%}' for s, v in era['L2'].items()) + '.', '',
          'Limits: the normal rests mostly on Landsat 5 and 7 and after-entry seasons on Landsat 8 and 9; the window runs to 15 August, wider than MODIS\'s July; a field-centre pixel can touch the edge of a small field; a 2001–2016 normal can drift. Greenness only.', '']
    open(os.path.join(OUT, 'wp3_x2l_landsat.md'), 'w').write('\n'.join(L))
    w.log('done')


if __name__ == '__main__':
    main()

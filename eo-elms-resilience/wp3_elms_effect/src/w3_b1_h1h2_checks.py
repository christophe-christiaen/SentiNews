"""W3-B1 checks on H1 and H2 (protocol: w3_b1_h1h2_checks_protocol.md): what seasons H2's comparison side holds and whether it leans on wet
seasons; H1 under raw, ratio, pooled-SD and capped z-score outcomes.

Input   as wp3_did.py, plus data/matched_sample.parquet, data/matched_sample_e3.parquet
Output  wp3_elms_effect/results/w3_b1_h1h2_checks.json (aggregates only)
"""
import json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w


def raw(t, col):
    s = pd.read_parquet(os.path.join(w.D, 's2', 's2_parcel_year.parquet'), columns=['parcref', 'year', col])
    s = s[s.parcref.isin(t.parcref)]
    M = np.full((len(t), len(w.SEASONS)), np.nan)
    M[pd.Series(np.arange(len(t)), index=t.parcref).reindex(s.parcref).values, s.year.values - w.SEASONS[0]] = s[col].values.astype('float64')
    return M


def scalings(M, cell):
    b = M[:, :4]; n = (~np.isnan(b)).sum(1)
    with np.errstate(all='ignore'):
        import warnings; warnings.simplefilter('ignore')
        mu, sd = np.nanmean(b, 1), np.nanstd(b, 1, ddof=1)
    mu[n < 2], sd[n < 2] = np.nan, np.nan
    pooled = pd.Series(sd).groupby(cell).transform('median').values
    z = (M - mu[:, None]) / np.clip(sd, .02, None)[:, None]
    return {'raw': M, 'ratio': 100 * M / mu[:, None], 'pooled_sd_z': (M - mu[:, None]) / pooled[:, None], 'z_capped_5': np.clip(z, -5, 5), 'z_frozen_rebuilt': z}, sd


def main():
    d = w.Data(); t = d.t
    m0 = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet')).set_index('parcref').in_matched_sample
    M0 = m0.reindex(t.parcref).fillna(False).values.astype(bool)
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    ME = ms.in_matched_sample.values

    def con(E, a, b):
        th, V, G, _ = E.run([E.weights(a, b)]); se = float(np.sqrt(V[0, 0]))
        return dict(est=float(th[0]), se=se, lo=float(th[0] - 1.96 * se), hi=float(th[0] + 1.96 * se), t=float(th[0] / se))
    out = {}

    # Check 1: H2
    for lab, pm in (('X2 sample (frozen)', M0), ('E3 sample', ME)):
        E = d.est('ndvi_peak_z', pmask=pm); TR = E.TR
        calm = (TR.e.values >= 0) & ~TR.shock.values
        a, b = calm & TR.prev.values, calm & ~TR.prev.values
        nT, tau, yr, wet = TR.nT.values, TR.tau_sum.values, TR.t.values, TR.wet.values
        side = lambda m: {str(y): dict(weight=float(nT[m & (yr == y)].sum() / nT[m].sum()), wet_share=float(nT[m & (yr == y) & wet].sum() / nT[m & (yr == y)].sum()),
                                       mean_effect=float(tau[m & (yr == y)].sum() / nT[m & (yr == y)].sum())) for y in sorted(set(yr[m]))}
        r = dict(main=con(E, a, b), after_shock=side(a), after_calm=side(b), wet_share_after_shock=float(nT[a & wet].sum() / nT[a].sum()),
                 wet_share_after_calm=float(nT[b & wet].sum() / nT[b].sum()), no_wet_cells=con(E, a & ~wet, b & ~wet),
                 leave_one_season_out={str(y): con(E, a & (yr != y), b & (yr != y)) for y in sorted(set(yr[a | b])) if (a & (yr != y)).any() and (b & (yr != y)).any()})
        r['label_dominated_by_wet'] = r['wet_share_after_calm'] >= .5
        m, q = r['main'], r['no_wet_cells']
        r['label_depends_on_wet'] = bool(abs(q['est'] - m['est']) > m['se'] or ((m['lo'] <= 0 <= m['hi']) != (q['lo'] <= 0 <= q['hi'])))
        out.setdefault('H2', {})[lab] = r
        w.log('H2', lab, m, 'no wet', q, r['wet_share_after_shock'], r['wet_share_after_calm'])
    assert abs(out['H2']['X2 sample (frozen)']['main']['est'] - .035) < .0006

    # Check 2: H1 scalings
    diag = {}
    for var, zcol in (('July NDVI', 'ndvi_july_z'), ('Seasonal integral', 'integral_z')):
        S, sd = scalings(raw(t, var.replace('July NDVI', 'ndvi_july').replace('Seasonal integral', 'integral')), d.cell)
        Zf = d.Y[zcol]
        ok = ~np.isnan(Zf) & ~np.isnan(S['z_frozen_rebuilt'])
        diag[var] = dict(rebuilt_z_matches_frozen_max_abs_diff=float(np.nanmax(np.abs(Zf[ok] - S['z_frozen_rebuilt'][ok]))),
                         share_sd_at_floor=float(np.mean(sd[~np.isnan(sd)] <= .02)),
                         share_abs_z_over_5_by_season={str(y): float(np.mean(np.abs(Zf[:, j][~np.isnan(Zf[:, j])]) > 5)) for j, y in enumerate(w.SEASONS)})
        for lab, pm in (('X2 sample (frozen)', M0), ('E3 sample', ME)):
            res = {}
            for k, Y in [('z_frozen', Zf)] + [(k, S[k]) for k in ('raw', 'ratio', 'pooled_sd_z', 'z_capped_5')]:
                E = d.est(Ymat=Y, pmask=pm); TR = E.TR; post = TR.e.values >= 0
                res[k] = con(E, post & TR.shock.values, post & ~TR.shock.values)
            alt = [res[k] for k in ('raw', 'ratio', 'pooled_sd_z', 'z_capped_5')]
            s0 = np.sign(res['z_frozen']['est'])
            res['label'] = 'depends on scaling' if any(x['lo'] <= 0 <= x['hi'] or np.sign(x['est']) != s0 for x in alt) else 'holds across scalings'
            out.setdefault('H1', {}).setdefault(var, {})[lab] = res
            w.log('H1', var, lab, {k: (round(v['est'], 4), round(v['lo'], 4), round(v['hi'], 4)) for k, v in res.items() if k != 'label'}, res['label'])
    assert abs(out['H1']['July NDVI']['X2 sample (frozen)']['z_frozen']['est'] - .082) < .0006
    out['diagnostics'] = diag
    json.dump(out, open(os.path.join(w.RES, 'w3_b1_h1h2_checks.json'), 'w'), indent=1)
    w.log('done')


if __name__ == '__main__':
    main()

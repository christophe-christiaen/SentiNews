"""WP3 exploratory additions E1 and E2 (decisions record, 17 October 2026, specified before running).

E1  MODIS history 2002-2016 (and 2017-2020 as a bridge): in the matched sample, does land that later entered an
    agreement already differ from never-treated land in shock seasons vs other seasons, within ERA5 cell x season?
    S ~ treated + treated x shock, cell x season effects absorbed, errors clustered by cell. A long placebo for H1.
E2  Sentinel-1 waterlogging: winter VH anomaly (per-orbit panel, 2017-2025), the H1-type contrast with wet winters
    in place of dry/heat shocks, same Callaway-Sant'Anna estimator, strata (cell x season x crop), matched sample
    and clustering as wp3_did.py. Also the overall post-entry effect on winter VH and the pre-entry contrast.

Output  wp3_elms_effect/results/wp3_supporting.md, wp3_supporting.json
"""
import json, os, sys
import numpy as np, pandas as pd
import wp3_did as w

ROOT = w.ROOT
sys.path.insert(0, os.path.join(ROOT, 'wp2_resilience', 'src'))
import parcel_resilience as pr                       # noqa: E402
import modis_long_baseline_check as mlb              # noqa: E402


def e1(t, M):
    p = mlb.load()
    flag = pd.DataFrame({'parcref': t.parcref, 'treated': (t.G > 0).astype(float), 'M': M})
    p = p.merge(flag, on='parcref')
    p = p[p.M & p.S.notna()]
    out = {}
    for lab, yrs in (('2002–2016 (before any agreement in the sample)', (2002, 2016)), ('2017–2020 (bridge, still pre-entry)', (2017, 2020))):
        a = p[p.year.between(*yrs)].copy()
        a['tx'] = a.treated * a.shock
        wdm = pr.within(a, ['S', 'treated', 'tx'], 'cy')
        b, se, pv, G = pr.ols_cluster(wdm.S, wdm[['tx', 'treated']], a.cell_id_data)
        out[lab] = dict(shock_contrast=float(b[0]), se=float(se[0]), p=float(pv[0]), level_gap=float(b[1]),
                        level_se=float(se[1]), n=int(len(a)), clusters=int(G), shock_share=float(a.shock.mean()))
        w.log('E1', lab, round(b[0], 4), round(se[0], 4))
    return out


def e2(d, M):
    s1 = pd.read_parquet(os.path.join(w.D, 's1', 's1_orbit_parcel_season.parquet'), columns=['parcref', 'season', 'winter_vh_anom'])
    s1 = s1[s1.season <= 2025]
    idx = pd.Series(np.arange(len(d.t)), index=d.t.parcref)
    Y = np.full((len(d.t), len(w.SEASONS)), np.nan)
    i = idx.reindex(s1.parcref).values; ok = ~np.isnan(i)
    Y[i[ok].astype(int), s1.season.values[ok] - w.SEASONS[0]] = s1.winter_vh_anom.values[ok]
    E = d.est(Ymat=Y, pmask=M, seasons=range(2017, 2026))
    TR = E.TR; post, pre = (TR.e >= 0).values, (TR.e < 0).values
    wet = TR.wet.values
    W = [E.weights(post & wet, post & ~wet), E.weights(post), E.weights(pre & wet, pre & ~wet)]
    th, V, G, _ = E.run(W)
    names = ['wet-winter contrast after entry (dB)', 'overall effect after entry (dB)', 'wet-winter contrast before entry (placebo, dB)']
    out = {n: w.row(n, th, V, k, G, int(TR.nT.values[W[k] != 0].sum())) for k, n in enumerate(names)}
    w.log('E2', {k: round(v['est'], 3) for k, v in out.items()})
    return out


def main():
    d = w.Data()
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet'))
    assert (ms.parcref.values == d.t.parcref.values).all()
    M = ms.in_matched_sample.values
    res = {'E1_modis_history': e1(d.t, M), 'E2_sentinel1_waterlogging': e2(d, M)}
    json.dump(res, open(os.path.join(w.RES, 'wp3_supporting.json'), 'w'), indent=1, default=float)
    L = ['# WP3 exploratory additions: MODIS history and Sentinel-1 waterlogging', '',
         'Specified in the decisions record on 17 October 2026 before running; exploratory, no multiple-testing '
         'correction. Matched sample; errors clustered by ERA5 cell.', '',
         '## E1. Did future agreement land already respond differently to shocks, years before entry? (MODIS)', '',
         'Shock contrast = (agreement-land minus never-treated stress) in shock seasons minus the same in other seasons, '
         'within cell × season; stress in SD of each field\'s 2001–2016 normal. The frozen-plan placebo (Sentinel-2) was +0.079.', '',
         '| Period | shock contrast | SE | p | level gap (all seasons) | SE | field-seasons | share in shock |', '|---|---|---|---|---|---|---|---|']
    for k, v in res['E1_modis_history'].items():
        L.append(f"| {k} | {v['shock_contrast']:+.3f} | {v['se']:.3f} | {v['p']:.3f} | {v['level_gap']:+.3f} | {v['level_se']:.3f} | {v['n']:,} | {v['shock_share']:.0%} |")
    L += ['', '## E2. Waterlogging: winter radar wetness (Sentinel-1, 2017–2025)', '',
          'Winter (December–February) VH backscatter anomaly; higher = wetter soil. Wet winter = October–March rainfall '
          '≥ 30% above normal. Same estimator as the frozen plan.', '',
          '| Contrast | estimate (dB) | SE | 95% CI | p | field-seasons |', '|---|---|---|---|---|---|'] + \
         [f"| {k} | {v['est']:+.3f} | {v['se']:.3f} | [{v['lo']:+.3f}, {v['hi']:+.3f}] | {v['p']:.3f} | {v['n']:,} |"
          for k, v in res['E2_sentinel1_waterlogging'].items()]
    open(os.path.join(w.RES, 'wp3_supporting.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

"""W3-B1 #9 (wp3_elms_effect/results/w3_b1_block_bootstrap_protocol.md, registered before any statistic): Paper B's
four-model I* comparison with intervals from a block bootstrap (10 km BNG squares within held-out regions; 5 and 20 km
as sensitivity) instead of single parcels. Point estimates must reproduce the published JSON first.

Output  wp3_elms_effect/results/w3_b1_block_bootstrap.md, .json (aggregates only)
"""
import itertools, json, os, pickle, sys
import numpy as np, pandas as pd
import option_detection as od
import w3_4_model_comparison as mc

RES = mc.RES
B = 1000
SIZES = [10_000, 5_000, 20_000]
CACHE = sys.argv[1] if len(sys.argv) > 1 else None          # optional folder for cached predictions (not published)


def preds(fam, df, F):
    f = CACHE and os.path.join(CACHE, f'pred_{fam.replace(" ", "_")}.pkl')
    if f and os.path.exists(f):
        return pickle.load(open(f, 'rb'))
    P = mc.preds_for(df, F)
    if f:
        pickle.dump(P, open(f, 'wb'))
    return P


def interval(df, P, xy, size):
    y = df.y.values
    ok = np.all([np.isfinite(v) for mp in P.values() for v in mp.values()], axis=0)
    idx = np.where(ok)[0]; reg = df.region.values[idx]
    bx = (xy.loc[df.parcref.values[idx], 'x'].values // size).astype(int)
    by = (xy.loc[df.parcref.values[idx], 'y'].values // size).astype(int)
    key = pd.Series(reg).astype(str) + '|' + pd.Series(bx).astype(str) + '_' + pd.Series(by).astype(str)
    blocks = {}
    for r in np.unique(reg):
        m = reg == r
        blocks[r] = [idx[m][g] for g in pd.Series(np.arange(m.sum())).groupby(key.values[m]).indices.values()]
    rng = np.random.default_rng(29)
    draws = {n: [] for n in mc.MODELS}; skipped = 0
    for _ in range(B):
        ix = np.concatenate([np.concatenate([bl[i] for i in rng.integers(0, len(bl), len(bl))]) for bl in blocks.values()])
        if y[ix].min() == y[ix].max():
            skipped += 1; continue
        for n in mc.MODELS:
            draws[n].append(mc.istar(y, P[n], ix)[0])
    draws = {n: np.array(v) for n, v in draws.items()}
    res = {'blocks': int(sum(len(b) for b in blocks.values())), 'parcels_per_block_median': float(np.median([len(g) for b in blocks.values() for g in b])),
           'skipped': skipped, 'Istar_ci': {n: [float(np.quantile(draws[n], 0.025)), float(np.quantile(draws[n], 0.975))] for n in mc.MODELS}, 'pairs': {}}
    point = {n: mc.istar(y, P[n], idx)[0] for n in mc.MODELS}
    for a, b in itertools.combinations(mc.MODELS, 2):
        d = draws[a] - draws[b]
        p = float(min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean())))
        res['pairs'][f'{a} vs {b}'] = dict(diff=point[a] - point[b], ci=[float(np.quantile(d, 0.025)), float(np.quantile(d, 0.975))], p=p)
    return res


def verdicts(out, key):
    """Published rule (w3_4_model_comparison.py), applied to the intervals under `key`."""
    ks = [(f, pr) for f in mc.OPTIONS for pr in out[f][key]['pairs']]
    adj = mc.holm(np.array([out[f][key]['pairs'][pr]['p'] for f, pr in ks]))
    for (f, pr), a in zip(ks, adj):
        out[f][key]['pairs'][pr]['p_holm'] = float(a)
    V = {}
    for f in mc.OPTIONS:
        r = out[f]; ci = r[key]['Istar_ci']
        det = [n for n in mc.MODELS if ci[n][0] > 0.02]
        if not det:
            V[f] = dict(detecting=[], verdict='not detectable by any model'); continue
        better = {n: set() for n in mc.MODELS}
        for pr, v in r[key]['pairs'].items():
            a, b = pr.split(' vs ')
            if v['p_holm'] < 0.05:
                (better[a] if v['diff'] > 0 else better[b]).add(b if v['diff'] > 0 else a)
        best = [n for n in mc.MODELS if len(better[n]) == 3]
        top = max(mc.MODELS, key=lambda n: r['Istar'][n])
        lead = [n for n in mc.MODELS if n == top or top not in better or n not in better[top]]
        V[f] = dict(detecting=det, verdict=f'best suited: {best[0]}' if best else f'no single best; leading group: {", ".join(lead)}')
    return V


def main():
    pub = json.load(open(os.path.join(RES, 'w3_4_model_comparison.json')))
    agr, never, mgmt = od.load()
    keep = set(agr.parcref) | set(never.parcref)
    xy = pd.read_parquet(os.path.join(od.D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y']).drop_duplicates('parcref').set_index('parcref')
    F = mc.features(keep)
    out = {}
    for fam, cs in od.FAMILIES.items():
        cs = set(cs)
        pos = agr[agr.codes.map(lambda c: len(c & cs) > 0)]
        comp = never if fam in mc.CONTROLS else mgmt[~mgmt.parcref.isin(pos.parcref)]
        df = od.sample(pos, comp).reset_index(drop=True)
        P = preds(fam, df, F)
        y = df.y.values
        ok = np.all([np.isfinite(v) for mp in P.values() for v in mp.values()], axis=0); idx = np.where(ok)[0]
        pt = {n: mc.istar(y, P[n], idx) for n in mc.MODELS}
        gap = max(max(abs(pt[n][0] - pub['results'][fam]['Istar'][n]), abs(pt[n][1] - pub['results'][fam]['auc_post'][n])) for n in mc.MODELS)
        if gap > 1e-9 or int(len(idx)) != pub['results'][fam]['n']:
            raise SystemExit(f'reproduction failed for {fam}: max gap {gap}, n {len(idx)} vs {pub["results"][fam]["n"]}')
        r = {'n': int(len(idx)), 'comparison': pub['results'][fam]['comparison'], 'Istar': {n: pt[n][0] for n in mc.MODELS},
             'parcel': {'Istar_ci': pub['results'][fam]['Istar_ci'], 'pairs': pub['results'][fam]['pairs']}, 'reproduced_max_gap': gap}
        for s in SIZES:
            r[f'block_{s // 1000}km'] = interval(df, P, xy, s)
        out[fam] = r
        print(fam, 'reproduced', f'{gap:.1e}', {n: [round(v, 3) for v in r['block_10km']['Istar_ci'][n]] for n in mc.MODELS}, flush=True)
    V = {'parcel': {f: dict(detecting=[n for n in mc.MODELS if out[f]['parcel']['Istar_ci'][n][0] > 0.02], verdict=pub['verdict'][f]) for f in mc.OPTIONS}}
    for s in SIZES:
        V[f'block_{s // 1000}km'] = verdicts(out, f'block_{s // 1000}km')
    labels = {}
    for f in mc.OPTIONS:
        a, b = V['parcel'][f], V['block_10km'][f]
        labels[f] = ('holds under clustering' if a == b else 'detection holds, ranking changes' if a['detecting'] == b['detecting'] else 'depends on clustering')
    json.dump({'results': out, 'verdicts': V, 'labels': labels}, open(os.path.join(RES, 'w3_b1_block_bootstrap.json'), 'w'), indent=1, default=float)
    report(out, V, labels)


def report(out, V, labels):
    c = lambda v: f'{v[0]:+.3f} to {v[1]:+.3f}'
    L = ['# W3-B1 #9: Paper B intervals with clustered resampling', '',
         'Run of [w3_b1_block_bootstrap_protocol.md](w3_b1_block_bootstrap_protocol.md) (registered before any statistic). '
         'Point estimates reproduce [w3_4_model_comparison.md](w3_4_model_comparison.md) exactly (largest gap '
         f'{max(r["reproduced_max_gap"] for r in out.values()):.0e}). Intervals: 1,000 resamples of 10 km British National Grid blocks within held-out regions '
         '(5 and 20 km as sensitivity), against the published resampling of single parcels. Detectable beyond selection: interval lower end above 0.02.', '',
         '## Labels (10 km blocks, primary)', '', '| Family | Models detecting (parcels → 10 km) | Verdict, parcels | Verdict, 10 km | Label |', '|---|---|---|---|---|']
    for f in mc.OPTIONS:
        L.append(f"| {f} | {', '.join(V['parcel'][f]['detecting']) or 'none'} → {', '.join(V['block_10km'][f]['detecting']) or 'none'} | "
                 f"{V['parcel'][f]['verdict']} | {V['block_10km'][f]['verdict']} | **{labels[f]}** |")
    L += ['', '## Sensitivity: verdicts by block size', '', '| Family | 5 km | 10 km | 20 km |', '|---|---|---|---|']
    for f in mc.OPTIONS:
        L.append(f'| {f} | ' + ' | '.join(f"{', '.join(V[k][f]['detecting']) or 'none'}; {V[k][f]['verdict']}" for k in ('block_5km', 'block_10km', 'block_20km')) + ' |')
    L += ['', '## I* and 95% intervals', '', '| Family | comp. | Model | I* | parcels | 5 km | 10 km | 20 km | width ratio 10 km / parcels |', '|---|---|---|---|---|---|---|---|---|']
    for f, r in out.items():
        for n in mc.MODELS:
            p = r['parcel']['Istar_ci'][n]; t = r['block_10km']['Istar_ci'][n]
            L.append(f"| {f} | {r['comparison'][0]} | {n} | {r['Istar'][n]:+.3f} | {c(p)} | {c(r['block_5km']['Istar_ci'][n])} | {c(t)} | "
                     f"{c(r['block_20km']['Istar_ci'][n])} | {(t[1] - t[0]) / (p[1] - p[0]):.2f} |")
    L += ['', '## Blocks', '', '| Family | n parcels | blocks 5 / 10 / 20 km | median parcels per 10 km block | resamples skipped |', '|---|---|---|---|---|']
    for f, r in out.items():
        L.append(f"| {f} | {r['n']:,} | {r['block_5km']['blocks']:,} / {r['block_10km']['blocks']:,} / {r['block_20km']['blocks']:,} | "
                 f"{r['block_10km']['parcels_per_block_median']:.0f} | {sum(r[k]['skipped'] for k in ('block_5km', 'block_10km', 'block_20km'))} |")
    L += ['', 'Calibration (controls within ±0.02) is a point-estimate rule and is unchanged by this check.']
    open(os.path.join(RES, 'w3_b1_block_bootstrap.md'), 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()

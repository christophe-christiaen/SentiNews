"""W3-4 seasonal cover-crop test (wp3_elms_effect/results/w3_4_cover_seasonal_protocol.md, written 30 October 2026
before any winter feature, winter embedding or season-2026 input existed): does a winter view (December-February)
detect winter cover crops (SAM2, CSAM2) better beyond selection?

Versions: V1 Presto full season (AI, reference); V2 Presto winter months only (AI); V3 winter radar and optical values
(no AI: NDVI, NDMI, VV, VH, VH-VV per winter month); V4 winter radar only (no AI). I* as in W3-4 (pre = mean of seasons
2018-2019, I0 season 2020); post = season 2026 (primary) and 2025 (secondary). Paired bootstrap (1,000 resamples within
held-out regions), Holm over the four primary tests.

Output  wp3_elms_effect/results/w3_4_cover_seasonal.md, .json
"""
import glob, json, os
import numpy as np, pandas as pd
import option_detection as od
import w3_4_metric as m
import w3_4_metric_ext as ext
import w3_4_model_comparison as mc

RES = m.RES
B = 1000
RNG = np.random.default_rng(30)
VERSIONS = ['V1', 'V2', 'V3', 'V4']
NAME = {'V1': 'Presto, full season (AI)', 'V2': 'Presto, winter (AI)', 'V3': 'Winter radar and optical (no AI)', 'V4': 'Winter radar only (no AI)'}
FAMILIES = {'Winter cover': {'SAM2', 'CSAM2'}, 'Spring- and summer-sown cover': {'SOH2', 'SOH3'}}
CONTROLS = {k: set(v) for k, v in od.FAMILIES.items() if 'control' in k}
TESTS = [('T-a', 'V2', 'V1'), ('T-b', 'V2', 'V3'), ('T-c', 'V3', 'V1'), ('T-d', 'V4', 'V3')]
SPRING = {'AC01', 'AC16', 'AC19', 'AC24', 'AC30', 'AC32', 'AC34', 'AC36', 'LG03', 'LG07', 'AC17', 'AC03', 'AC44'}
WINTER = [3, 4, 5]


def winter_values(seasons, keep, radar_only):
    parts = []
    for s in seasons:
        for f in sorted(glob.glob(os.path.join(od.D, 'presto', 'inputs', f'i_*_{s}.parquet'))):
            d = pd.read_parquet(f); d = d[d.parcref.isin(keep)]
            o = pd.DataFrame({'parcref': d.parcref.values})
            for mo in WINTER:
                g = lambda b: d[f'{b}_m{mo:02d}'].values.astype(float)
                o[f'vv{mo}'], o[f'vh{mo}'] = g('VV'), g('VH'); o[f'cr{mo}'] = o[f'vh{mo}'] - o[f'vv{mo}']
                if not radar_only:
                    with np.errstate(invalid='ignore', divide='ignore'):
                        o[f'ndvi{mo}'] = (g('B8') - g('B4')) / (g('B8') + g('B4'))
                        o[f'ndmi{mo}'] = (g('B8') - g('B11')) / (g('B8') + g('B11'))
            parts.append(o)
    return pd.concat(parts, ignore_index=True).groupby('parcref').mean()


def winter_presto(seasons, keep):
    d = pd.concat([pd.read_parquet(f) for s in seasons for f in sorted(glob.glob(os.path.join(od.D, 'embeddings', 'presto_winter', f'w_*_{s}.parquet')))], ignore_index=True)
    d = d[d.parcref.isin(keep)]; cols = [c for c in d.columns if c.startswith('W')]
    d[cols] = d[cols].astype('float32')
    return d.groupby('parcref')[cols].mean()


def features(keep, post):
    load = {'V1': lambda s: ext.load('Presto', s, keep), 'V2': lambda s: winter_presto(s, keep),
            'V3': lambda s: winter_values(s, keep, False), 'V4': lambda s: winter_values(s, keep, True)}
    return {v: {'pre': f([2018, 2019]), 'y2020': f([2020]), 'post': f([post])} for v, f in load.items()}


def run(df, F):
    """I*, 95% intervals and paired differences for the four versions on one sample."""
    P = {}
    for v in VERSIONS:
        g = lambda k: F[v][k].reindex(df.parcref).values
        sets = {'pre': g('pre'), 'post': g('post'), 'pre+post': np.hstack([g('pre'), g('post')]), 'pre+2020': np.hstack([g('pre'), g('y2020')])}
        P[v] = {k: m.loro_pred(df, X) for k, X in sets.items()}
    y = df.y.values
    ok = np.all([np.isfinite(x) for mp in P.values() for x in mp.values()], axis=0)
    idx = np.where(ok)[0]; reg = df.region.values[idx]
    point = {v: mc.istar(y, P[v], idx) for v in VERSIONS}
    groups = [idx[reg == r] for r in np.unique(reg)]
    draws = {v: [] for v in VERSIONS}
    for _ in range(B):
        ix = np.concatenate([RNG.choice(g, len(g)) for g in groups])
        if y[ix].min() == y[ix].max():
            continue
        for v in VERSIONS:
            draws[v].append(mc.istar(y, P[v], ix)[0])
    draws = {v: np.array(x) for v, x in draws.items()}
    q = lambda x: [float(np.quantile(x, 0.025)), float(np.quantile(x, 0.975))]
    res = {'n': int(len(idx)), 'n_dropped': int((~ok).sum()), 'Istar': {v: point[v][0] for v in VERSIONS},
           'auc_post': {v: point[v][1] for v in VERSIONS}, 'Istar_ci': {v: q(draws[v]) for v in VERSIONS}, 'tests': {}}
    for t, a, b in TESTS:
        d = draws[a] - draws[b]
        res['tests'][t] = dict(a=a, b=b, diff=point[a][0] - point[b][0], ci=q(d), p=float(min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean()))))
    return res


def analysis(post, spring_only=False):
    agr, never, mgmt = od.load()
    if spring_only:
        crop = pd.read_parquet(os.path.join(od.D, 'parcels', 'crome', 'parcel_crop_2025.parquet'))
        sp = set(crop.parcref[crop.lucode.isin(SPRING)])
        agr, never, mgmt = (x[x.parcref.isin(sp)] for x in (agr, never, mgmt))
    keep = set(agr.parcref) | set(never.parcref)
    F = features(keep, post)
    out = {}
    fams = dict(FAMILIES, **CONTROLS)
    for fam, cs in fams.items():
        pos = agr[agr.codes.map(lambda c: len(c & cs) > 0)]
        comps = {'A': never} if fam in CONTROLS else {'B': mgmt[~mgmt.parcref.isin(pos.parcref)], 'A': never}
        if fam != 'Winter cover' and fam not in CONTROLS:
            comps = {'B': comps['B']}
        for clab, comp in comps.items():
            df = od.sample(pos, comp).reset_index(drop=True)
            out[f'{fam} | {clab}'] = r = run(df, F)
            print(post, 'spring' if spring_only else 'all', fam, clab, {v: round(r['Istar'][v], 3) for v in VERSIONS}, flush=True)
    return out


def read(out):
    """The reading fixed in advance: validity, detection, tests T-a..T-d (Holm over the four)."""
    w = out['Winter cover | B']
    valid = {}
    for v in VERSIONS:
        ctrl = {c: out[f'{c} | A']['Istar'][v] for c in CONTROLS}
        inv = abs(out['Winter cover | A']['Istar'][v] - w['Istar'][v])
        valid[v] = dict(controls=ctrl, calibration=bool(all(abs(x) <= 0.02 for x in ctrl.values())), invariance_gap=inv,
                        selection_invariant=bool(inv < 0.03), detected=bool(w['Istar_ci'][v][0] > 0.02))
    adj = mc.holm(np.array([w['tests'][t]['p'] for t, _, _ in TESTS]))
    verdict = {}
    for (t, a, b), pa in zip(TESTS, adj):
        r = w['tests'][t]; r['p_holm'] = float(pa)
        if t == 'T-d':
            v = ('radar alone is enough' if -0.02 < r['ci'][0] and r['ci'][1] < 0.02 else
                 'optical adds' if r['diff'] < 0 and pa < 0.05 else 'inconclusive')
        else:
            v = (f'{a} better' if r['diff'] > 0 and pa < 0.05 else f'{a} worse' if r['diff'] < 0 and pa < 0.05 else 'no difference shown')
            winner = a if v.endswith('better') else b if v.endswith('worse') else None
            if winner and not (valid[winner]['calibration'] and valid[winner]['selection_invariant']):
                v += ' (not established: the leading version fails a validity check)'
        verdict[t] = v
    return valid, verdict


def main():
    res = {}
    for key, post, spring in (('primary · post 2026', 2026, False), ('secondary · post 2025', 2025, False),
                              ('secondary · post 2025 · spring crops 2025', 2025, True)):
        out = analysis(post, spring)
        valid, verdict = read(out)
        res[key] = dict(results=out, validity=valid, verdict=verdict)
    json.dump(res, open(os.path.join(RES, 'w3_4_cover_seasonal.json'), 'w'), indent=1, default=float)
    report(res)


def report(res):
    f3 = lambda x: f'{x:+.3f}'
    L = ['# W3-4 seasonal cover-crop test: a winter view of winter cover crops', '',
         'Protocol: [w3_4_cover_seasonal_protocol.md](w3_4_cover_seasonal_protocol.md), written before any winter feature, winter '
         'embedding or season-2026 input existed. Winter = December–February. I* = [AUC(pre + post) − AUC(pre)] − [AUC(pre + 2020) − '
         'AUC(pre)]; pre = winters/seasons 2018–2019; 95% intervals from 1,000 paired bootstrap resamples within held-out regions.', '']
    for key, r in res.items():
        L += [f'## {key[0].upper() + key[1:]}', '', '| Family | comparison | n | ' + ' | '.join(NAME[v] for v in VERSIONS) + ' |',
              '|---|---|---|' + '---|' * len(VERSIONS)]
        for k, x in r['results'].items():
            fam, c = k.split(' | ')
            L.append(f'| {fam} | {c} | {x["n"]:,} | ' + ' | '.join(f'{f3(x["Istar"][v])} ({f3(x["Istar_ci"][v][0])} to {f3(x["Istar_ci"][v][1])})' for v in VERSIONS) + ' |')
        L += ['', '| Version | controls vs never-treated | calibration (±0.02) | |I*(A) − I*(B)| | selection-invariant (< 0.03) | winter cover detected |', '|---|---|---|---|---|---|']
        for v, x in r['validity'].items():
            L.append(f'| {NAME[v]} | ' + ', '.join(f3(c) for c in x['controls'].values()) + f' | {"pass" if x["calibration"] else "**fail**"} | '
                     f'{x["invariance_gap"]:.3f} | {"yes" if x["selection_invariant"] else "**no**"} | {"yes" if x["detected"] else "no"} |')
        w = r['results']['Winter cover | B']['tests']
        L += ['', '| Test | difference in I* | 95% interval | p | Holm p | reading |', '|---|---|---|---|---|---|']
        for t, a, b in TESTS:
            x = w[t]
            L.append(f'| {t}: {NAME[a]} − {NAME[b]} | {f3(x["diff"])} | {f3(x["ci"][0])} to {f3(x["ci"][1])} | {x["p"]:.3g} | {x["p_holm"]:.3g} | {r["verdict"][t]} |')
        L.append('')
    L += ['Primary reading = the first section (post winter 2025/26, all cereal land, comparison B). The other sections are secondary '
          'and do not change it. Spring-sown crops = 13 CROME codes listed in the protocol. Labels are declared, not verified.']
    open(os.path.join(RES, 'w3_4_cover_seasonal.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

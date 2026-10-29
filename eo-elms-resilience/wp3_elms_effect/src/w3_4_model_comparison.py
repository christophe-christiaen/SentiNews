"""W3-4 model comparison (wp3_elms_effect/results/w3_4_model_comparison_protocol.md, written 29 October 2026 before
any rerun result was read): which embedding detects which option best.

Four models on the same parcels and common years (pre = mean 2018-2019, I0 = 2020, post = 2025; Presto by farm season):
AlphaEarth, Sentinel-2 indices, TESSERA, Presto. I* per model; for each option family (comparison B) and model pair,
the difference in I* with a paired bootstrap (1,000 resamples within held-out regions, shared across models),
two-sided bootstrap p, Holm over the 36 tests. Controls (vs never-treated) and AUC(post) reported descriptively.

Output  wp3_elms_effect/results/w3_4_model_comparison.md, .json
"""
import itertools, json, os
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
import option_detection as od
import w3_4_metric as m
import w3_4_metric_ext as ext

RES = m.RES
B = 1000
RNG = np.random.default_rng(29)
MODELS = ['AlphaEarth', 'Sentinel-2', 'TESSERA', 'Presto']
OPTIONS = ['Herbal leys', 'Cover crops', 'No-till', 'In-field flower and bird-food plots', 'Margins and corners', 'Grassland options']
CONTROLS = ['Buffer strips (control)', 'Management only (control)']


def features(keep):
    F = {'AlphaEarth': {'pre': od.emb_year([2018, 2019], keep), 'y2020': od.emb_year([2020], keep), 'post': od.emb_year([2025], keep)},
         'Sentinel-2': {'pre': m.s2_years([2018, 2019], keep), 'y2020': m.s2_years([2020], keep), 'post': m.s2_years([2025], keep)}}
    for n in ('TESSERA', 'Presto'):
        F[n] = {'pre': ext.load(n, [2018, 2019], keep), 'y2020': ext.load(n, [2020], keep), 'post': ext.load(n, [2025], keep)}
    return F


def preds_for(df, F):
    out = {}
    for name in MODELS:
        g = lambda k: F[name][k].reindex(df.parcref).values
        sets = {'pre': g('pre'), 'post': g('post'), 'pre+post': np.hstack([g('pre'), g('post')]), 'pre+2020': np.hstack([g('pre'), g('y2020')])}
        out[name] = {k: m.loro_pred(df, X) for k, X in sets.items()}
    return out


def istar(y, p, ix):
    a = {k: roc_auc_score(y[ix], v[ix]) for k, v in p.items()}
    return (a['pre+post'] - a['pre']) - (a['pre+2020'] - a['pre']), a['post']


def compare(df, P):
    y = df.y.values
    ok = np.all([np.isfinite(v) for mp in P.values() for v in mp.values()], axis=0)
    idx = np.where(ok)[0]; reg = df.region.values[idx]
    point = {n: istar(y, P[n], idx) for n in MODELS}
    groups = [idx[reg == r] for r in np.unique(reg)]
    draws = {n: [] for n in MODELS}
    for _ in range(B):
        ix = np.concatenate([RNG.choice(g, len(g)) for g in groups])
        if y[ix].min() == y[ix].max():
            continue
        for n in MODELS:
            draws[n].append(istar(y, P[n], ix)[0])
    draws = {n: np.array(v) for n, v in draws.items()}
    res = {'n': int(len(idx)), 'Istar': {n: point[n][0] for n in MODELS}, 'auc_post': {n: point[n][1] for n in MODELS},
           'Istar_ci': {n: [float(np.quantile(draws[n], 0.025)), float(np.quantile(draws[n], 0.975))] for n in MODELS}, 'pairs': {}}
    for a, b in itertools.combinations(MODELS, 2):
        d = draws[a] - draws[b]
        p = float(min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean())))
        res['pairs'][f'{a} vs {b}'] = dict(diff=point[a][0] - point[b][0], ci=[float(np.quantile(d, 0.025)), float(np.quantile(d, 0.975))], p=p)
    return res


def holm(ps):
    order = np.argsort(ps); adj = np.empty(len(ps)); run = 0.0
    for r, i in enumerate(order):
        run = max(run, (len(ps) - r) * ps[i]); adj[i] = min(1.0, run)
    return adj


def main():
    agr, never, mgmt = od.load()
    keep = set(agr.parcref) | set(never.parcref)
    F = features(keep)
    out = {}
    for fam, cs in od.FAMILIES.items():
        cs = set(cs)
        pos = agr[agr.codes.map(lambda c: len(c & cs) > 0)]
        comp = never if fam in CONTROLS else mgmt[~mgmt.parcref.isin(pos.parcref)]
        df = od.sample(pos, comp).reset_index(drop=True)
        out[fam] = compare(df, preds_for(df, F))
        out[fam]['comparison'] = 'A (never-treated)' if fam in CONTROLS else 'B (management-only)'
        print(fam, {n: round(v, 3) for n, v in out[fam]['Istar'].items()}, flush=True)
    keys = [(f, pr) for f in OPTIONS for pr in out[f]['pairs']]
    adj = holm(np.array([out[f]['pairs'][pr]['p'] for f, pr in keys]))
    for (f, pr), a in zip(keys, adj):
        out[f]['pairs'][pr]['p_holm'] = float(a)
    verdict = {}
    for f in OPTIONS:
        r = out[f]
        detectable = [n for n in MODELS if r['Istar_ci'][n][0] > 0.02]
        if not detectable:
            verdict[f] = 'not detectable by any model'; continue
        better = {n: set() for n in MODELS}
        for pr, v in r['pairs'].items():
            a, b = pr.split(' vs ')
            if v['p_holm'] < 0.05:
                (better[a] if v['diff'] > 0 else better[b]).add(b if v['diff'] > 0 else a)
        best = [n for n in MODELS if len(better[n]) == 3]
        top = max(MODELS, key=lambda n: r['Istar'][n])
        lead = [n for n in MODELS if n == top or top not in better or n not in better[top]]
        verdict[f] = f'best suited: {best[0]}' if best else f'no single best; leading group: {", ".join(lead)}'
    json.dump({'results': out, 'verdict': verdict}, open(os.path.join(RES, 'w3_4_model_comparison.json'), 'w'), indent=1, default=float)
    report(out, verdict)


NAME = {'AlphaEarth': 'AlphaEarth (AI)', 'TESSERA': 'TESSERA (AI)', 'Presto': 'Presto (AI)', 'Sentinel-2': 'Sentinel-2 indices (no AI, baseline)'}
AI = ['AlphaEarth', 'TESSERA', 'Presto']


def report(out, verdict):
    """Presentation: question 1 compares the three AI embeddings with each other; question 2 compares each with the
    no-AI baseline (plain Sentinel-2 indices). The analysis and the Holm correction over all 36 tests are as fixed."""
    nm = lambda t: ' '.join(NAME[w.strip(',')] + (',' if w.endswith(',') else '') if w.strip(',') in NAME else w for w in t.split()) if t else t
    L = ['# W3-4 model comparison: which AI embedding sees which option, and does any beat the plain indices?', '',
         'Protocol: [w3_4_model_comparison_protocol.md](w3_4_model_comparison_protocol.md), written 29 October 2026 before any '
         'rerun result was read. Three AI embeddings (AlphaEarth, TESSERA, Presto) and one no-AI baseline (plain Sentinel-2 '
         'vegetation indices, the kind of satellite data the embeddings are learned from). Common years: pre = 2018–2019, '
         'I₀ = 2020, post = 2025 (Presto: farm seasons). I* = selection-corrected detection; options against management-only '
         f'scheme land, controls against never-treated land. Paired bootstrap ({B:,}), Holm over all 36 tests.', '',
         '## Selection-corrected detection I* (95% interval)', '',
         '| Option | ' + ' | '.join(NAME[n] for n in AI + ['Sentinel-2']) + ' | verdict (rule fixed in advance) |', '|---' * 6 + '|']
    for f in OPTIONS + CONTROLS:
        r = out[f]
        cells = [f"{r['Istar'][n]:+.3f} ({r['Istar_ci'][n][0]:+.3f} to {r['Istar_ci'][n][1]:+.3f})" for n in AI + ['Sentinel-2']]
        L.append(f'| {f} | ' + ' | '.join(cells) + f" | {nm(verdict.get(f, 'control (reported, not tested)'))} |")
    for title, keep in (('## Question 1: which AI embedding suits which option (AI vs AI)', lambda a, b: a in AI and b in AI),
                        ('## Question 2: does an AI embedding beat the plain indices (AI vs no-AI baseline)', lambda a, b: 'Sentinel-2' in (a, b))):
        L += ['', title, '', '| Option | pair | difference in I* (95% CI) | p (Holm, over 36) |', '|---|---|---|---|']
        for f in OPTIONS:
            for pr, v in out[f]['pairs'].items():
                a, b = pr.split(' vs ')
                if keep(a, b):
                    if b in AI and a == 'Sentinel-2':
                        a, b, d, ci = b, a, -v['diff'], [-v['ci'][1], -v['ci'][0]]
                    else:
                        d, ci = v['diff'], v['ci']
                    L.append(f"| {f} | {NAME[a]} vs {NAME[b]} | {d:+.3f} ({ci[0]:+.3f} to {ci[1]:+.3f}) | {v['p_holm']:.3g} |")
    L += ['', '## How well a single field can be classified: AUC with the 2025 record (descriptive)', '',
          '| Option | ' + ' | '.join(NAME[n] for n in AI + ['Sentinel-2']) + ' |', '|---' * 5 + '|']
    for f in OPTIONS + CONTROLS:
        L.append(f'| {f} | ' + ' | '.join(f"{out[f]['auc_post'][n]:.2f}" for n in AI + ['Sentinel-2']) + ' |')
    open(os.path.join(RES, 'w3_4_model_comparison.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

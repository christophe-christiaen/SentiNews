"""Pilot re-check (50 MODIS sites, 2001-2026, normal 2001-2015): do the legacy / hit-harder / debt effects survive
when each site is compared only with itself? Same diagnostics as wp2_resilience/src/within_field_check.py, plus a
simulation of this exact design (50 sites, 26 seasons, 15-season normal, year effects) to calibrate each estimator.

Tests (as in src/cumulative.py): T1 S_t on S_t-1 with year effects; T2 the same in national shock years (national mean
S <= -1); T3 rebound S_t+1 - S_t on debt D_t-1 controlling S_t, in shock years. Errors clustered by site.

Output  results/cumulative/pilot_within_check.md, pilot_within_check.json
"""
import json, os
import numpy as np, pandas as pd
from scipy.stats import norm

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
RES = os.path.join(ROOT, 'results', 'cumulative')
RNG = np.random.default_rng(2026)


def demean(df, cols, groups, it=10):
    out = df[cols].astype(float).copy()
    for _ in range(it if len(groups) > 1 else 1):
        for g in groups:
            out -= out.groupby(df[g]).transform('mean')
    return out


def ols_cl(y, X, cl):
    X = np.asarray(X, float).reshape(len(y), -1); y = np.asarray(y, float)
    XtXi = np.linalg.inv(X.T @ X); b = XtXi @ X.T @ y; e = y - X @ b
    codes = pd.factorize(cl)[0]; G = codes.max() + 1
    S = np.zeros((G, X.shape[1])); np.add.at(S, codes, X * e[:, None])
    V = XtXi @ (S.T @ S) @ XtXi * G / (G - 1); se = np.sqrt(np.diag(V))
    return dict(coef=float(b[0]), se=float(se[0]), p=float(2 * norm.sf(abs(b[0] / se[0]))), n=int(len(y)))


def iv_cl(y, x, z, cl):
    y, x, z = map(lambda a: np.asarray(a, float), (y, x, z))
    zx = (z * x).sum(); b = (z * y).sum() / zx; e = y - b * x
    codes = pd.factorize(cl)[0]; s = np.bincount(codes, weights=z * e)
    se = np.sqrt((s ** 2).sum() * len(s) / (len(s) - 1)) / abs(zx)
    return dict(coef=float(b), se=float(se), p=float(2 * norm.sf(abs(b / se))), n=int(len(y)), first_stage_r=float(np.corrcoef(z, x)[0, 1]))


def prep(p):
    p = p.sort_values(['site_id', 'year']).reset_index(drop=True)
    g = p.groupby('site_id')
    for k in (1, 2, 3):
        p[f'S_l{k}'] = g.S.shift(k)
    p['S_next'] = g.S.shift(-1)
    lam = 0.5; d = np.zeros(len(p)); prev = 0.0; first = p.site_id.values != np.roll(p.site_id.values, 1)
    for i, s in enumerate(p.S.fillna(0).values):
        prev = (0.0 if first[i] else prev) * lam + min(s, 0.0); d[i] = prev
    p['D'] = d; p['D_l1'] = p.groupby('site_id').D.shift(1)
    return p


def tests(p, shock_years):
    out = {}
    a = p.dropna(subset=['S', 'S_l1'])
    w = demean(a, ['S', 'S_l1'], ['year']); out['T1 | as reported (year effects)'] = ols_cl(w.S, w.S_l1, a.site_id)
    s = a[a.year.isin(shock_years)]
    w = demean(s, ['S', 'S_l1'], ['year']); out['T2 | as reported (year effects)'] = ols_cl(w.S, w.S_l1, s.site_id)
    w = demean(a, ['S', 'S_l1'], ['site_id', 'year']); out['T1 | site fixed effects'] = ols_cl(w.S, w.S_l1, a.site_id)
    w = demean(s, ['S', 'S_l1'], ['site_id', 'year']); out['T2 | site fixed effects'] = ols_cl(w.S, w.S_l1, s.site_id)
    b = p.assign(dS=p.S - p.S_l1, dl=p.S_l1 - p.S_l2).dropna(subset=['dS', 'dl', 'S_l2'])
    w = demean(b, ['dS', 'dl', 'S_l2'], ['year']); out['T1 | within each site (Anderson-Hsiao)'] = iv_cl(w.dS, w.dl, w.S_l2, b.site_id)
    bs = b[b.year.isin(shock_years)]
    w = demean(bs, ['dS', 'dl', 'S_l2'], ['year']); out['T2 | within each site (Anderson-Hsiao)'] = iv_cl(w.dS, w.dl, w.S_l2, bs.site_id)
    r = p[p.year.isin(shock_years)].dropna(subset=['S_next', 'D_l1']).copy(); r['rebound'] = r.S_next - r.S
    w = demean(r, ['rebound', 'D_l1', 'S'], ['year']); out['T3 | as reported (year effects)'] = ols_cl(w.rebound, w[['D_l1', 'S']], r.site_id)
    w = demean(r, ['rebound', 'D_l1', 'S'], ['site_id', 'year']); out['T3 | site fixed effects'] = ols_cl(w.rebound, w[['D_l1', 'S']], r.site_id)
    return out


def shuffled(p, shock_years, reps=200):
    vals = {'T1': [], 'T2': [], 'T3': []}
    for _ in range(reps):
        q = p[['site_id', 'year', 'S']].copy()
        q['S'] = q.groupby('site_id').S.transform(lambda v: RNG.permutation(v.values))
        t = tests(prep(q), shock_years)
        for k in vals:
            vals[k].append(t[f'{k} | as reported (year effects)']['coef'])
    return {k: dict(mean=float(np.mean(v)), sd=float(np.std(v))) for k, v in vals.items()}


def simulate(rho, reps=300, sites=50, seasons=26, n_base=15):
    est = {'pooled': [], 'site FE': [], 'Anderson-Hsiao': []}
    for _ in range(reps):
        a = RNG.normal(0, 1, sites)[:, None]; c = RNG.normal(0, 0.8, seasons)[None, :]
        e = np.zeros((sites, seasons)); prev = RNG.normal(0, 1, sites)
        for t in range(seasons):
            prev = rho * prev + np.sqrt(1 - rho ** 2) * RNG.normal(0, 1, sites); e[:, t] = prev
        y = a + c + e
        S = (y - y[:, :n_base].mean(1, keepdims=True)) / y[:, :n_base].std(1, ddof=1, keepdims=True)
        p = pd.DataFrame({'site_id': np.repeat(np.arange(sites), seasons), 'year': np.tile(np.arange(seasons), sites), 'S': S.ravel()})
        p = prep(p)
        a1 = p.dropna(subset=['S_l1'])
        w = demean(a1, ['S', 'S_l1'], ['year']); est['pooled'].append((w.S * w.S_l1).sum() / (w.S_l1 ** 2).sum())
        w = demean(a1, ['S', 'S_l1'], ['site_id', 'year']); est['site FE'].append((w.S * w.S_l1).sum() / (w.S_l1 ** 2).sum())
        b = p.assign(dS=p.S - p.S_l1, dl=p.S_l1 - p.S_l2).dropna(subset=['dS', 'dl', 'S_l2'])
        w = demean(b, ['dS', 'dl', 'S_l2'], ['year']); est['Anderson-Hsiao'].append((w.S_l2 * w.dS).sum() / (w.S_l2 * w.dl).sum())
    return {k: dict(mean=float(np.mean(v)), sd=float(np.std(v))) for k, v in est.items()}


def main():
    p = pd.read_csv(os.path.join(RES, 'site_stress_index.csv'))
    p['site_id'] = p.region + '_' + p.site.astype(str)
    p = prep(p[['site_id', 'region', 'year', 'S']])
    nat = p.groupby('year').S.mean(); shock_years = [int(y) for y in nat[nat <= -1].index]
    out = {'shock_years': shock_years, 'sites': int(p.site_id.nunique()), 'tests': tests(p, shock_years)}
    out['shuffled_placebo'] = shuffled(p, shock_years)
    out['simulation'] = {str(r): simulate(r) for r in (0.0, 0.1, 0.2, 0.3)}
    json.dump(out, open(os.path.join(RES, 'pilot_within_check.json'), 'w'), indent=1)
    t = out['tests']
    L = ['# Pilot re-check: do the compounding effects survive within each site?', '',
         f"50 MODIS sites, 2001–2026, each site's normal 2001–2015; national shock years {', '.join(map(str, shock_years))}. "
         'Errors clustered by site. Same diagnostics as the field-level check (wp2_resilience/results/within_field_check.md).', '',
         '| Test | version | coefficient | SE | p | n | note |', '|---|---|---|---|---|---|---|']
    for k, v in t.items():
        a, b = k.split(' | ')
        note = f"first-stage r {v['first_stage_r']:.2f}" if 'first_stage_r' in v else ''
        L.append(f"| {a} | {b} | {v['coef']:+.3f} | {v['se']:.3f} | {v['p']:.3g} | {v['n']:,} | {note} |")
    L += ['', '**Season-shuffling placebo** (200 shuffles of each site\'s seasons; what lasting site differences alone give, '
          'as-reported test): ' + '; '.join(f"{k} {v['mean']:+.3f} (SD {v['sd']:.3f})" for k, v in out['shuffled_placebo'].items()), '',
          '**Simulation of this design** (50 sites, 26 seasons, 15-season normal, year effects; 300 runs; mean (SD) of the T1 estimate):', '',
          '| true carry-over ρ | as reported (pooled) | site fixed effects | Anderson–Hsiao |', '|---|---|---|---|'] + \
         [f"| {r} | {v['pooled']['mean']:+.3f} ({v['pooled']['sd']:.3f}) | {v['site FE']['mean']:+.3f} ({v['site FE']['sd']:.3f}) | "
          f"{v['Anderson-Hsiao']['mean']:+.3f} ({v['Anderson-Hsiao']['sd']:.3f}) |" for r, v in out['simulation'].items()]
    open(os.path.join(RES, 'pilot_within_check.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

"""WP2 check A (Paper 2 outline): are the legacy / hit-harder / debt effects real dynamics, or an artefact of each
field's normal being estimated from only four seasons (an error in the normal shifts every season the same way)?

Versions of T1 (S_t on S_t-1) and T2 (the same in shock seasons), all with cell x season effects absorbed and errors
clustered by ERA5 cell:
  original        as in parcel_resilience.py (normal = 2017-2020)
  split normal    S_t and S_t-1 standardised against two *disjoint* random halves of the field's other seasons, so
                  errors in the normal cannot be shared between them (tests the artefact)
  field FE        field fixed effects (two-way demeaning): removes all stable field differences; biased towards zero
                  with ~9 seasons per field (Nickell), so a lower bound
  Anderson-Hsiao  first differences remove field effects; dS_t-1 instrumented by S_t-2 (and by S_t-3, robust to
                  season-specific measurement noise): consistent for the dynamic effect
  shuffled        each field's seasons randomly reordered: what stable field differences alone produce
T3 (rebound S_t+1 - S_t on debt D_t-1, controlling S_t; shock season followed by a calm one): original, field FE,
shuffled.

Output  wp2_resilience/results/within_field_check.md, within_field_check.json
"""
import json, os
import numpy as np, pandas as pd
import parcel_resilience as pr

RES = os.path.join(pr.ROOT, 'wp2_resilience', 'results')
RNG = np.random.default_rng(20261012)
YEARS = np.arange(2017, 2027)


def ols(y, x, cl):
    b, se, p, G = pr.ols_cluster(y, np.column_stack(x) if isinstance(x, (list, tuple)) else x, cl)
    return dict(coef=float(b[0]), se=float(se[0]), p=float(p[0]), n=int(len(y)), clusters=int(G))


def iv(y, x, z, cl):
    """Just-identified IV, one regressor, no intercept (data already demeaned); cluster-robust SE."""
    y, x, z = map(lambda a: np.asarray(a, float), (y, x, z))
    zx = (z * x).sum(); b = (z * y).sum() / zx; e = y - b * x
    codes = pd.factorize(cl)[0]; s = np.bincount(codes, weights=z * e)
    se = np.sqrt((s ** 2).sum() * len(s) / (len(s) - 1)) / abs(zx)
    from scipy.stats import norm
    first = np.corrcoef(z, x)[0, 1]
    return dict(coef=float(b), se=float(se), p=float(2 * (1 - norm.cdf(abs(b / se)))), n=int(len(y)),
                clusters=int(len(s)), first_stage_r=float(first))


def demean2(df, cols, a='parcref', b='cy', it=8):
    """Two-way demeaning (field and cell x season) by alternating projections."""
    out = df[cols].astype(float).copy()
    for _ in range(it):
        out -= out.groupby(df[a]).transform('mean')
        out -= out.groupby(df[b]).transform('mean')
    return out


def lags(p):
    g = p.groupby('parcref')
    for k in (1, 2, 3):
        p[f'S_l{k}'] = g.S.shift(k)
    p['S_next'], p['shock_next'] = g.S.shift(-1), g.shock.shift(-1)
    p['cy'] = p.cell_id_data.astype(str) + '_' + p.year.astype(str)
    return p


def t1t2(p, label, out):
    a = p.dropna(subset=['S', 'S_l1', 'cell_id_data'])
    w = pr.within(a, ['S', 'S_l1'], 'cy'); out[f'T1 | {label}'] = ols(w.S, w[['S_l1']], a.cell_id_data)
    s = a[a.shock]
    w = pr.within(s, ['S', 'S_l1'], 'cy'); out[f'T2 | {label}'] = ols(w.S, w[['S_l1']], s.cell_id_data)


def split_normal(p, raw):
    """S_t and S_t-1 against disjoint random halves of the remaining seasons (per field, per pair)."""
    wide = {c: raw.pivot(index='parcref', columns='year', values=c).reindex(columns=YEARS) for c in ('ndvi_july', 'ndvi_peak')}
    idx = wide['ndvi_july'].index
    rows = []
    for j in range(1, len(YEARS)):
        t, t1 = YEARS[j], YEARS[j - 1]
        others = [k for k in range(len(YEARS)) if k not in (j, j - 1)]
        perm = np.argsort(RNG.random((len(idx), len(others))), axis=1)
        half = len(others) // 2
        A = np.array(others)[perm[:, :half]]; B = np.array(others)[perm[:, half:]]
        def z(col, k, sel):
            v = wide[col].values
            base = np.take_along_axis(v, sel, axis=1)
            mu, sd = np.nanmean(base, 1), np.nanstd(base, 1, ddof=1)
            ok = (~np.isnan(base)).sum(1) >= 2
            return np.where(ok & (sd > 1e-4), (v[:, k] - mu) / np.where(sd > 1e-4, sd, 1), np.nan)
        St = np.clip(np.nanmean(np.vstack([z('ndvi_july', j, A), z('ndvi_peak', j, A)]), 0), -6, 6)
        Sl = np.clip(np.nanmean(np.vstack([z('ndvi_july', j - 1, B), z('ndvi_peak', j - 1, B)]), 0), -6, 6)
        rows.append(pd.DataFrame({'parcref': idx, 'year': t, 'S_split': St, 'S_l1_split': Sl}))
    return pd.concat(rows, ignore_index=True)


def main():
    p = pr.load()
    raw = pd.read_parquet(os.path.join(pr.D, 's2', 's2_parcel_year.parquet'), columns=['parcref', 'year', 'ndvi_july', 'ndvi_peak'])
    p = lags(p)
    p['D'] = pr.add_debt(p, 0.5)
    p['D_l1'] = p.groupby('parcref').D.shift(1)
    out = {}

    # T1/T2 original
    t1t2(p, 'original', out); print('original', {k: round(v['coef'], 3) for k, v in out.items()}, flush=True)

    # split normal
    sp = split_normal(p, raw).merge(p[['parcref', 'year', 'cy', 'cell_id_data', 'shock']], on=['parcref', 'year'])
    a = sp.dropna(subset=['S_split', 'S_l1_split', 'cell_id_data'])
    w = pr.within(a, ['S_split', 'S_l1_split'], 'cy'); out['T1 | split normal'] = ols(w.S_split, w[['S_l1_split']], a.cell_id_data)
    s = a[a.shock]
    w = pr.within(s, ['S_split', 'S_l1_split'], 'cy'); out['T2 | split normal'] = ols(w.S_split, w[['S_l1_split']], s.cell_id_data)
    print('split', out['T1 | split normal']['coef'], out['T2 | split normal']['coef'], flush=True)

    # field fixed effects (two-way)
    a = p.dropna(subset=['S', 'S_l1', 'cell_id_data']).copy()
    w = demean2(a, ['S', 'S_l1']); out['T1 | field FE (lower bound)'] = ols(w.S, w[['S_l1']], a.cell_id_data)
    s = a[a.shock].copy()
    w = demean2(s, ['S', 'S_l1']); out['T2 | field FE (lower bound)'] = ols(w.S, w[['S_l1']], s.cell_id_data)
    print('FE', out['T1 | field FE (lower bound)']['coef'], out['T2 | field FE (lower bound)']['coef'], flush=True)

    # Anderson-Hsiao
    p['dS'], p['dS_l1'] = p.S - p.S_l1, p.S_l1 - p.S_l2
    for zc, lab in (('S_l2', 'z = S(t-2)'), ('S_l3', 'z = S(t-3)')):
        for test, sel in (('T1', None), ('T2', 'shock')):
            a = p.dropna(subset=['dS', 'dS_l1', zc, 'cell_id_data'])
            if sel:
                a = a[a[sel]]
            w = pr.within(a, ['dS', 'dS_l1', zc], 'cy')
            out[f'{test} | Anderson-Hsiao, {lab}'] = iv(w.dS, w.dS_l1, w[zc], a.cell_id_data)
    print('AH', {k: round(v['coef'], 3) for k, v in out.items() if 'Anderson' in k}, flush=True)

    # shuffled placebo: reorder each field's seasons at random, keep everything else
    q = p[['parcref', 'year', 'S', 'cell_id_data', 'shock']].copy()
    q['S'] = q.groupby('parcref').S.transform(lambda v: RNG.permutation(v.values))
    q = lags(q); t1t2(q, 'shuffled seasons (placebo)', out)
    print('shuffled', out['T1 | shuffled seasons (placebo)']['coef'], flush=True)

    # T3
    def t3(df, label, fe=False):
        r = df[df.shock & (df.shock_next == False)].dropna(subset=['S', 'S_next', 'D_l1', 'cell_id_data']).copy()
        r['rebound'] = r.S_next - r.S
        if fe:
            r = r[r.groupby('parcref').S.transform('size') >= 2]
            w = demean2(r, ['rebound', 'D_l1', 'S'])
        else:
            w = pr.within(r, ['rebound', 'D_l1', 'S'], 'cy')
        out[f'T3 | {label}'] = ols(w.rebound, w[['D_l1', 'S']], r.cell_id_data)
    t3(p, 'original'); t3(p, 'field FE (lower bound)', fe=True)
    q['D'] = pr.add_debt(q.sort_values(['parcref', 'year']).reset_index(drop=True), 0.5)
    q['D_l1'] = q.groupby('parcref').D.shift(1)
    t3(q, 'shuffled seasons (placebo)')
    print('T3', {k: round(v['coef'], 3) for k, v in out.items() if k.startswith('T3')}, flush=True)

    json.dump(out, open(os.path.join(RES, 'within_field_check.json'), 'w'), indent=1)
    L = ['# WP2 check A: is the compounding real, or an artefact of the field normal?', '',
         'Each field\'s normal comes from four seasons (2017–2020); an error in it shifts every season the same way and '
         'can look like persistence. The versions below remove that possibility in different ways. Cell × season effects '
         'absorbed; errors clustered by ERA5 cell.', '',
         '| Test | version | coefficient | SE | p | n | note |', '|---|---|---|---|---|---|---|']
    for k, v in out.items():
        t, lab = k.split(' | ')
        note = f"first-stage r {v['first_stage_r']:.2f}" if 'first_stage_r' in v else ''
        L.append(f"| {t} | {lab} | {v['coef']:+.3f} | {v['se']:.3f} | {v['p']:.3g} | {v['n']:,} | {note} |")
    L += ['', 'Reading: *split normal* close to *original* → the shared-normal artefact is small. *Shuffled* shows what '
          'stable differences between fields produce on their own. *Field FE* is biased towards zero with ~9 seasons; '
          '*Anderson–Hsiao* is the consistent estimate of the season-to-season (legacy) effect once stable field '
          'differences are removed; the S(t−3) instrument guards against measurement noise in S.']
    open(os.path.join(RES, 'within_field_check.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

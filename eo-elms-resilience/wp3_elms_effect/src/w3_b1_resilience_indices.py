"""W3-B1 resilience indices (protocol: w3_b1_resilience_indices_protocol.md): Lloret-type resistance, resilience, recovery and relative resilience on
season-integrated NDVI, and a senescence date interpolated from half-months. Also the corrected exploratory senescence row of wp3_results.md.

Input   as wp3_did.py, plus data/matched_sample.parquet, data/matched_sample_e3.parquet
Output  wp3_elms_effect/results/w3_b1_resilience_indices.md, .json (aggregates only)
"""
import json, os, sys
import numpy as np, pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
from w3_z_partf import members

B, SEED = 1999, 20261106
S25, S26, SP = range(2017, 2026), range(2017, 2027), range(2017, 2021)
FAMS = ('All agreement land', 'Management-only')
KS = [f'ndvi_p{k:02d}' for k in range(1, 13)]


def half_months(t):
    s = pd.read_parquet(os.path.join(w.D, 's2', 's2_parcel_year.parquet'), columns=['parcref', 'year', 'senesc_k'] + KS)
    s = s[s.parcref.isin(t.parcref)]
    i = pd.Series(np.arange(len(t)), index=t.parcref).reindex(s.parcref).values
    j = s.year.values - 2017
    A = np.full((len(t), 10, 12), np.nan)
    A[i, j] = s[KS].values.astype('float64')
    old = np.full((len(t), 10), np.nan)
    old[i, j] = s.senesc_k.values.astype('float64')
    return A, old


def integrate(A, min_obs, ends):
    """Trapezoid over half-months 3-10 with linear interpolation across gaps, held flat beyond the first and last observed."""
    W = A[:, :, 2:10]
    n, y, m = W.shape
    V = W.reshape(-1, m); obs = ~np.isnan(V); ix = np.arange(m)
    prev = np.maximum.accumulate(np.where(obs, ix, -1), axis=1)
    nxt = np.minimum.accumulate(np.where(obs, ix, m)[:, ::-1], axis=1)[:, ::-1]
    r = np.arange(len(V))[:, None]
    pv = np.where(prev >= 0, V[r, np.clip(prev, 0, m - 1)], np.nan)
    nv = np.where(nxt < m, V[r, np.clip(nxt, 0, m - 1)], np.nan)
    pv, nv = np.where(np.isnan(pv), nv, pv), np.where(np.isnan(nv), pv, nv)
    gap = np.where((prev >= 0) & (nxt < m) & (nxt > prev), nxt - prev, 1)
    fr = np.where((prev >= 0) & (nxt < m) & (nxt > prev), (ix - prev) / gap, 0.0)
    F = pv + (nv - pv) * fr
    X = ((F[:, :-1] + F[:, 1:]) / 2).sum(1)
    ok = obs.sum(1) >= min_obs
    if ends:
        ok &= obs[:, :3].any(1) & obs[:, -3:].any(1)
    X = np.where(ok & (X >= 0.4), X, np.nan)
    return X.reshape(n, y)


def normal(M):
    b = M[:, :4]; ok = (~np.isnan(b)).sum(1) >= 2
    out = np.full(len(M), np.nan)
    out[ok] = np.nanmean(b[ok], axis=1)
    return out


def indices(X):
    N = normal(X)[:, None]
    lag = np.column_stack([np.full(len(X), np.nan), X[:, :-1]])
    with np.errstate(all='ignore'):
        return dict(Rt=X / N, Rs=X / N, Rc=X / lag, RRs=(X - lag) / N)


def senescence(A):
    n, y, _ = A.shape
    D = np.full((n, y), np.nan); has = np.full((n, y), np.nan)
    pk_win = A[:, :, 3:9]
    any_pk = (~np.isnan(pk_win)).any(2)
    pk = np.where(any_pk, np.nan_to_num(pk_win, nan=-9).argmax(2) + 3, -1)
    for i, j in zip(*np.nonzero(any_pk)):
        a = A[i, j]; p = pk[i, j]; lim = .5 * a[p]
        has[i, j] = 0
        if a[p] <= 0: continue                                        # a non-positive peak has no 50% crossing
        o = np.flatnonzero(~np.isnan(a[p:])) + p
        b = o[a[o] < lim]
        if not len(b): continue
        k1 = b[0]; k0 = o[o < k1][-1]
        if k1 - k0 > 2: continue
        D[i, j] = k0 + 1 + (a[k0] - lim) / (a[k0] - a[k1]) * (k1 - k0); has[i, j] = 1
    return D - normal(D)[:, None], has


def main():
    d = w.Data(); t = d.t
    m0 = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet')).set_index('parcref').in_matched_sample
    M0 = m0.reindex(t.parcref).fillna(False).values.astype(bool)
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    ME = ms.in_matched_sample.values
    Mem = members(t)
    main_sh = w.shock_table(**w.MAIN_SHOCK)
    wet_sh = w.shock_table(**w.MAIN_SHOCK); wet_sh['shock'] = wet_sh['wet']
    HZ = {'Dry or heat': main_sh, 'Wet winter': wet_sh}
    A, old = half_months(t)
    X = integrate(A, 5, True); X6 = integrate(A, 6, False)
    I, I6 = indices(X), indices(X6)
    Sen, Has = senescence(A); w.log('indices built')
    usable = dict(X=[float(np.mean(~np.isnan(X[ME, j]))) for j in range(10)], senescence=[float(np.mean(~np.isnan(Sen[ME, j]))) for j in range(10)])
    cer = np.column_stack([np.zeros(len(t))] + [np.nan_to_num(t[f'cereal_{y}'].astype('float64').values) if f'cereal_{y}' in t else np.zeros(len(t)) for y in w.SEASONS[:-1]])
    crop_pair = d.crop * 2 + cer.astype('int64')
    Gp, tmax = np.where(d.G > 0, d.G - 2, 0), np.where(d.G > 0, d.G, 9999)

    def est(Y, pm, f, sh, sn, crop=None, G=None, tm=None):
        fam = np.where(Mem[f], 'F', 'O') if f != 'All agreement land' else d.fam
        try:
            TR, CO = w.blocks(Y, d.G if G is None else G, d.cell, d.crop if crop is None else crop, crop is not None, list(sn), fam, pm, tm, False)
        except ValueError:
            return None
        return w.Est(w.attach_shocks(TR, d.cells, sh), CO, d.cluster)

    def masks(E, f, kind):
        TR = E.TR
        p = (TR.e.values >= 0) & (TR.fam.values == 'F' if f != 'All agreement land' else True)
        sk, pr = TR.shock.values, TR.prev.values
        return (p & sk, p & ~sk) if kind == 'H1' else (p & ~sk & pr, p & ~sk & ~pr)

    def con(E, f, kind):
        if E is None: return None
        a, b = masks(E, f, kind)
        if not a.any() or not b.any(): return None
        th, V, G, _ = E.run([E.weights(a, b)])
        se = float(np.sqrt(V[0, 0]))
        return dict(est=float(th[0]), se=se, lo=float(th[0] - 1.96 * se), hi=float(th[0] + 1.96 * se), p=float(2 * stats.norm.sf(abs(th[0]) / se)), G=int(G),
                    n_a=int(E.TR.nT.values[a].sum()), n_b=int(E.TR.nT.values[b].sum()))

    rng = np.random.default_rng(SEED)
    def few_shocks(E, f, kind, sh, sn, th0):
        TR = E.TR; a, b = masks(E, f, kind); p = (TR.e.values >= 0) & (TR.fam.values == 'F' if f != 'All agreement land' else True)
        nT, tau, cell = TR.nT.values, TR.tau_sum.values, TR.cell.values
        Na, Nb = nT[a].sum(), nT[b].sum(); ma, mb = tau[a].sum() / Na, tau[b].sum() / Nb
        sc = np.where(a, (tau - nT * ma) / Na, 0.0) - np.where(b, (tau - nT * mb) / Nb, 0.0)
        I_ = pd.Series(sc).groupby(TR.t.values).sum().values; I_ = I_[I_ != 0]; g = len(I_)
        if g < 2:
            season = dict(G=g, se=None, lo=None, hi=None)
        else:
            se = float(np.sqrt(I_ @ I_ * g / (g - 1))); q = float(stats.t.ppf(.975, g - 1))
            season = dict(G=g, se=se, lo=th0 - q * se, hi=th0 + q * se)
        sn = list(sn)
        SH = sh.shock.reindex(pd.MultiIndex.from_product([d.cells, sn])).fillna(False).values.reshape(len(d.cells), len(sn)).astype(bool)
        tix = TR.t.values - sn[0]; draws = []
        for _ in range(B):
            pi = rng.permutation(len(sn)); s1 = SH[cell, pi[tix]]
            if kind == 'H1':
                x, y = p & s1, p & ~s1
            else:
                s0 = np.where(tix > 0, SH[cell, pi[np.clip(tix - 1, 0, None)]], False)
                x, y = p & ~s1 & s0, p & ~s1 & ~s0
            if not x.any() or not y.any(): continue
            draws.append(tau[x].sum() / nT[x].sum() - tau[y].sum() / nT[y].sum())
        draws = np.array(draws)
        pp = float((1 + (np.abs(draws) >= abs(th0)).sum()) / (1 + len(draws)))
        rob = bool(season['lo'] is not None and (season['lo'] > 0 or season['hi'] < 0) and pp < .05)
        return dict(season=season, permutation=dict(p=pp, draws=len(draws)), robust_to_few_shocks=rob)

    rows = []
    def add(index, hazard, f, read):
        sh = HZ[hazard]; xi = index in ('Rt', 'Rs', 'Rc', 'RRs')
        Y = I[index] if xi else Sen
        kind = 'H2' if index in ('Rs', 'Rc', 'RRs') else 'H1'
        sn, crop = (S26, None) if kind == 'H2' else (S25, d.crop)
        E = est(Y, ME, f, sh, sn, crop)
        r = dict(index=index, hazard=hazard, family=f, read=read, seasons=f'{sn[0]}-{sn[-1]}', crop_strata=crop is not None, main=con(E, f, kind))
        a, _ = masks(E, f, kind)
        r['weight_by_season'] = (pd.Series(E.TR.nT.values[a]).groupby(E.TR.t.values[a]).sum() / E.TR.nT.values[a].sum()).round(3).rename(index=str).to_dict()
        r['few_shocks'] = few_shocks(E, f, kind, sh, sn, r['main']['est'])
        r['placebo'] = con(est(Y, ME, f, sh, SP, crop, Gp, tmax), f, kind)
        alt = S25 if kind == 'H2' else S26
        alt_crop = (d.crop if index == 'Rs' else crop_pair) if kind == 'H2' else None
        r['other_version'] = con(est(Y, ME, f, sh, alt, alt_crop), f, kind)
        r['X2_sample'] = con(est(Y, M0, f, sh, sn, crop), f, kind)
        if xi: r['six_of_eight'] = con(est(I6[index], ME, f, sh, sn, crop), f, kind)
        else: r['date_exists'] = con(est(Has, ME, f, sh, S25, d.crop), f, 'H1')
        rows.append(r); m = r['main']
        w.log(index, hazard, f, round(m['est'], 4), round(m['se'], 4), 'placebo', r['placebo'] and round(r['placebo']['est'], 4), 'perm', r['few_shocks']['permutation']['p'])

    for hz in HZ:
        for f in FAMS:
            add('Rt', hz, f, True); add('Senescence date', hz, f, True)
    for f in FAMS:
        for ix in ('Rs', 'Rc', 'RRs'): add(ix, 'Dry or heat', f, True)
    for f in FAMS:
        for ix in ('Rs', 'Rc', 'RRs'): add(ix, 'Wet winter', f, False)
    read = [r for r in rows if r['read']]
    for r, h in zip(read, w.holm([r['main']['p'] for r in read])): r['holm_p'] = float(h)
    for r in rows:
        m, pl = r['main'], r['placebo']
        side = 1 if m['lo'] > 0 else -1 if m['hi'] < 0 else 0
        clean = bool(pl and pl['lo'] <= 0 <= pl['hi'])
        word = {1: 'later', -1: 'earlier'} if r['index'] == 'Senescence date' else {1: 'cushion', -1: 'cost'}
        r['reading'] = 'not read' if not r['read'] else 'not labelled alone' if r['index'] == 'Rc' else f'{word[side]} indicated' if side and clean else f'{word[side]}, placebo fails or is missing' if side else 'none indicated'
        if 'date_exists' in r:
            q = r['date_exists']; r['selected'] = bool(q and (q['lo'] > 0 or q['hi'] < 0) and abs(q['est']) >= .02)

    # Correction: the registered discrete senescence row, its old coding reproduced first
    b = old[:, :4]; Yold = old - np.nanmean(b, axis=1, keepdims=True)
    Eo = d.est(Ymat=Yold, pmask=M0); Ec = d.est('senesc_anom', pmask=M0); Ei = d.est('integral_z', pmask=M0)
    a_ = lambda E: con(E, 'All agreement land', 'H1')
    corr = dict(old_coding=a_(Eo), corrected=a_(Ec), integral_check=a_(Ei), share_minus1=[float(np.mean(old[M0, j] == -1)) for j in range(10)])
    assert abs(corr['old_coding']['est'] + .172) < .0006, corr['old_coding']
    assert abs(corr['integral_check']['est'] - .120) < .0006, corr['integral_check']
    w.log('correction', corr['old_coding']['est'], corr['corrected'])
    json.dump(dict(rows=rows, correction=corr, usable_share_E3=usable), open(os.path.join(w.RES, 'w3_b1_resilience_indices.json'), 'w'), indent=1, default=float)
    w.log('done')


if __name__ == '__main__':
    main()

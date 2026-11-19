"""W3-M (wp3_elms_effect/results/w3_m_sid_protocol.md, registered 19 November 2026 before any SID model): selection-
invariant detection. Detectors STD (X_post), SID-D (X_post - X_pre), SID-R (X_post residualised on X_pre) and SID-A
(adversarial: an encoder shared by a detection head on X_post and, through gradient reversal, an enrolment adversary on
X_pre), on Sentinel-2, AlphaEarth, TESSERA and Presto. D = held-out AUC (leave one region out); D0 = the same pipeline
with the 2020 record in the post role. Intervals: 1,000 resamples of 10 km blocks within held-out regions (seed 29),
parcel bootstrap beside.

Usage   python w3_m_sid.py CACHE_DIR [--workers 8]
Output  wp3_elms_effect/results/w3_m_sid.md, .json (aggregates only)
"""
import argparse, json, os, pickle
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import Ridge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
import option_detection as od
import w3_4_model_comparison as mc
import w3_x_delta_ai as dai

RES = mc.RES
B = 1000
PRODUCTS = ['Sentinel-2', 'AlphaEarth', 'TESSERA', 'Presto']
DETECTORS = ['STD', 'SID-D', 'SID-R', 'SID-A']
ALPHAS = [0.1, 1.0, 10.0, 100.0, 1000.0]
LAMBDAS = [0.3, 1.0, 3.0]
DETECTED = ['Herbal leys', 'No-till', 'Cover crops', 'In-field flower and bird-food plots', 'Grassland options']


def block_key(xy, parcref, size=10_000):
    p = xy.loc[parcref]
    return ((p.x.values // size).astype(int).astype(str) + '_' + (p.y.values // size).astype(int).astype(str))


def hgb(Xtr, ytr, Xte):
    return HistGradientBoostingClassifier(max_iter=200, random_state=0).fit(Xtr, ytr).predict_proba(Xte)[:, 1]


def residualise(Ptr, Qtr, Pte, Qte, groups):
    """Predict Q (post role) from P (pre) with ridge; alpha by 5-fold block CV on training fields; cross-fitted
    training residuals; held-out residuals from the fit on all training fields. No labels used."""
    sp, sq = StandardScaler().fit(Ptr), StandardScaler().fit(Qtr)
    Ptr_s, Qtr_s, Pte_s, Qte_s = sp.transform(Ptr), sq.transform(Qtr), sp.transform(Pte), sq.transform(Qte)
    folds = list(GroupKFold(5).split(Ptr_s, groups=groups))
    err = {a: np.mean([((Ridge(alpha=a).fit(Ptr_s[t], Qtr_s[t]).predict(Ptr_s[v]) - Qtr_s[v]) ** 2).mean() for t, v in folds]) for a in ALPHAS}
    a = min(err, key=err.get)
    Rtr = np.empty_like(Qtr_s)
    for t, v in folds:
        Rtr[v] = Qtr_s[v] - Ridge(alpha=a).fit(Ptr_s[t], Qtr_s[t]).predict(Ptr_s[v])
    Rte = Qte_s - Ridge(alpha=a).fit(Ptr_s, Qtr_s).predict(Pte_s)
    return Rtr, Rte, a


def adv_fit_predict(Ptr, Qtr, ytr, Pte, Qte, lam, seed):
    import torch
    torch.set_num_threads(1); torch.manual_seed(seed); rng = np.random.default_rng(seed)
    s = StandardScaler().fit(np.vstack([Ptr, Qtr]))
    # torch 2.2.2 (last Intel-macOS build) has no NumPy 2 bridge: pass values as Python lists (exact float32 conversion)
    T = lambda X: torch.tensor(s.transform(X).tolist(), dtype=torch.float32)
    P, Q, y = T(Ptr), T(Qtr), torch.tensor(np.asarray(ytr, dtype=float).tolist(), dtype=torch.float32)

    class GRL(torch.autograd.Function):
        @staticmethod
        def forward(ctx, x): return x.view_as(x)
        @staticmethod
        def backward(ctx, g): return -g
    d = P.shape[1]
    enc = torch.nn.Sequential(torch.nn.Linear(d, 64), torch.nn.ReLU(), torch.nn.Linear(64, 64), torch.nn.ReLU())
    head, adv = torch.nn.Linear(64, 1), torch.nn.Linear(64, 1)
    opt = torch.optim.Adam(list(enc.parameters()) + list(head.parameters()) + list(adv.parameters()), lr=1e-3)
    bce = torch.nn.BCEWithLogitsLoss()
    n = len(y)
    for _ in range(60):
        for b in np.array_split(rng.permutation(n), max(1, n // 512)):
            b = torch.tensor(b.tolist())
            loss = bce(head(enc(Q[b])).squeeze(1), y[b]) + lam * bce(adv(GRL.apply(enc(P[b]))).squeeze(1), y[b])
            opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        f = lambda X: np.array(torch.sigmoid(head(enc(T(X)))).squeeze(1).tolist())
        return f(Qte), f(Pte)


def sid_a(df, Xpre, Xq, tr, te):
    """Choose lambda by inner leave-one-region-out on training regions (seed 0), maximising AUC(post) - AUC(pre) of the
    detection head; then fit seeds 0-4 on all training regions and average held-out scores."""
    y = df.y.values; regs = df.region.values
    gain = {}
    for lam in LAMBDAS:
        g = []
        for r in np.unique(regs[tr]):
            itr, ite = tr & (regs != r), tr & (regs == r)
            if len(np.unique(y[ite])) < 2 or len(np.unique(y[itr])) < 2:
                continue
            sq, sp = adv_fit_predict(Xpre[itr], Xq[itr], y[itr], Xpre[ite], Xq[ite], lam, 0)
            g.append(roc_auc_score(y[ite], sq) - roc_auc_score(y[ite], sp))
        gain[lam] = float(np.mean(g))
    lam = max(gain, key=gain.get)
    sc = np.mean([adv_fit_predict(Xpre[tr], Xq[tr], y[tr], Xpre[te], Xq[te], lam, s)[0] for s in range(5)], axis=0)
    return sc, lam


def fold(df, Xpre, Xq, blocks, r, with_adv):
    """One held-out region: scores of each detector with Xq in the post role."""
    y = df.y.values; te = (df.region == r).values; tr = ~te
    out = {'idx': np.where(te)[0]}
    out['STD'] = hgb(Xq[tr], y[tr], Xq[te])
    out['SID-D'] = hgb((Xq - Xpre)[tr], y[tr], (Xq - Xpre)[te])
    Rtr, Rte, a = residualise(Xpre[tr], Xq[tr], Xpre[te], Xq[te], blocks[tr]); out['alpha'] = a
    out['SID-R'] = hgb(Rtr, y[tr], Rte)
    if with_adv:
        out['SID-A'], out['lambda'] = sid_a(df, Xpre, Xq, tr, te)
    return out


def scores(df, F, xy, cache, key, workers, with_adv):
    f = os.path.join(cache, f'sid_{key}.pkl')
    if os.path.exists(f):
        return pickle.load(open(f, 'rb'))
    g = lambda k: F[k].reindex(df.parcref).values.astype('float64')
    Xpre, Xpost, X20 = g('pre'), g('post'), g('y2020')
    blocks = block_key(xy, df.parcref.values)
    regs = [r for r in sorted(df.region.unique()) if df.y[(df.region == r).values].nunique() == 2 and df.y[(df.region != r).values].nunique() == 2]
    S = {}
    for role, Xq in (('post', Xpost), ('placebo', X20)):
        res = Parallel(n_jobs=workers)(delayed(fold)(df, Xpre, Xq, blocks, r, with_adv) for r in regs)
        S[role] = {d: np.full(len(df), np.nan) for d in DETECTORS if d != 'SID-A' or with_adv}
        S[role]['meta'] = {}
        for r, o in zip(regs, res):
            for d in S[role]:
                if d != 'meta':
                    S[role][d][o['idx']] = o[d]
            S[role]['meta'][r] = {k: o[k] for k in ('alpha', 'lambda') if k in o}
    pickle.dump(S, open(f, 'wb'))
    return S


def assess(df, S, xy):
    y = df.y.values; dets = [d for d in S['post'] if d != 'meta']
    ok = np.all([np.isfinite(S[r][d]) for r in ('post', 'placebo') for d in dets], axis=0); idx = np.where(ok)[0]
    auc = lambda s, ix: roc_auc_score(y[ix], s[ix])
    out = {'n': int(len(idx)), 'D': {d: auc(S['post'][d], idx) for d in dets}, 'D0': {d: auc(S['placebo'][d], idx) for d in dets},
           'meta': {'post': S['post']['meta'], 'placebo': S['placebo']['meta']}}
    for lab, G in (('block_10km', dai.groups_block(df, idx, xy)), ('parcel', dai.groups_parcel(df, idx))):
        rng = np.random.default_rng(29); dr = {f'{k}|{d}': [] for k in ('D', 'D0') for d in dets}
        for _ in range(B):
            ix = np.concatenate([np.concatenate([g[i] for i in rng.integers(0, len(g), len(g))]) for g in G])
            if y[ix].min() == y[ix].max():
                continue
            for d in dets:
                dr[f'D|{d}'].append(auc(S['post'][d], ix)); dr[f'D0|{d}'].append(auc(S['placebo'][d], ix))
        out[lab] = {k: [float(np.quantile(v, .025)), float(np.quantile(v, .975))] for k, v in dr.items()}
    return out


def labels(res):
    L = {}
    for p in PRODUCTS:
        L[p] = {}
        for d in DETECTORS:
            if f'Herbal leys | A | {p}' not in res or d not in res[f'Herbal leys | A | {p}']['D']:
                continue
            ctrl = [abs(res[f'{c} | A | {p}']['D'][d] - 0.5) for c in mc.CONTROLS]
            ctrl_std = [abs(res[f'{c} | A | {p}']['D']['STD'] - 0.5) for c in mc.CONTROLS]
            plac = [abs(res[f'{f} | A | {p}']['D0'][d] - 0.5) for f in od.FAMILIES]
            calibrated = all(v <= 0.02 for v in ctrl) and all(v <= 0.02 for v in plac)
            det = [f for f in DETECTED if res[f'{f} | A | {p}']['block_10km'][f'D|{d}'][0] - 0.5 > 0.02]
            if calibrated and len(det) >= 4:
                lab = 'works'
            elif (not calibrated and all(c <= s / 2 for c, s in zip(ctrl, ctrl_std))) or (calibrated and len(det) < 4):
                lab = 'partial'
            else:
                lab = 'fails'
            L[p][d] = dict(label=lab, calibrated=calibrated, controls_dist=ctrl, std_controls_dist=ctrl_std,
                           max_placebo_dist=max(plac), detected=det)
    return L


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cache'); ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--no-adv', action='store_true', help='skip SID-A (only if torch is unavailable; logged as a deviation)')
    a = ap.parse_args(); os.makedirs(a.cache, exist_ok=True)
    S, keep = dai.samples()
    keep_s = set(pd.concat([d.parcref for d in S.values()]))
    F = mc.features(keep_s)
    xy = pd.read_parquet(os.path.join(od.D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y']).drop_duplicates('parcref').set_index('parcref')
    res = {}
    for (fam, comp), df in S.items():
        for p in PRODUCTS:
            key = f'{fam}_{comp}_{p}'.replace(' ', '_')
            sc = scores(df, F[p], xy, a.cache, key, a.workers, not a.no_adv)
            res[f'{fam} | {comp} | {p}'] = assess(df, sc, xy)
            print(fam, comp, p, {d: round(v, 3) for d, v in res[f'{fam} | {comp} | {p}']['D'].items()}, flush=True)
    L = labels(res)
    json.dump({'results': res, 'labels': L}, open(os.path.join(RES, 'w3_m_sid.json'), 'w'), indent=1, default=float)
    report(res, L)


def report(res, L):
    c = lambda v: f'{v[0]:.3f}–{v[1]:.3f}'
    T = ['# W3-M: selection-invariant detection (SID)', '',
         'Run of [w3_m_sid_protocol.md](w3_m_sid_protocol.md) (registered before any model). D = held-out AUC against the comparison '
         'shown; D0 = the same pipeline with the 2020 (pre-entry) record in the post role. 95% intervals: 10 km blocks within held-out '
         'regions. Works = negative controls and every placebo D0 within 0.5 ± 0.02 against never-treated land, and at least 4 of '
         'the 5 I*-detected families detected (D interval above 0.52).', '', '## Labels', '',
         '| Product | ' + ' | '.join(DETECTORS) + ' |', '|---|' + '---|' * len(DETECTORS)]
    for p in PRODUCTS:
        T.append(f'| {p} | ' + ' | '.join(f"**{L[p][d]['label']}** ({len(L[p][d]['detected'])}/5 detected; controls "
                                            f"{L[p][d]['controls_dist'][0]:+.3f}, {L[p][d]['controls_dist'][1]:+.3f} from 0.5; "
                                            f"worst placebo {L[p][d]['max_placebo_dist']:.3f})" if d in L[p] else '–' for d in DETECTORS) + ' |')
    T += ['', '## D and D0 against never-treated land (A) and management-only land (B)', '',
          '| Family | comp. | Product | ' + ' | '.join(f'{d} D (95%)' for d in DETECTORS) + ' | ' + ' | '.join(f'{d} D0' for d in DETECTORS) + ' |',
          '|---|---|---|' + '---|' * (2 * len(DETECTORS))]
    for k, r in res.items():
        f, comp, p = k.split(' | ')
        T.append(f'| {f} | {comp} | {p} | ' + ' | '.join(f"{r['D'][d]:.3f} ({c(r['block_10km'][f'D|{d}'])})" if d in r['D'] else '–' for d in DETECTORS)
                 + ' | ' + ' | '.join(f"{r['D0'][d]:.3f}" if d in r['D0'] else '–' for d in DETECTORS) + ' |')
    open(os.path.join(RES, 'w3_m_sid.md'), 'w').write('\n'.join(T) + '\n')


if __name__ == '__main__':
    main()

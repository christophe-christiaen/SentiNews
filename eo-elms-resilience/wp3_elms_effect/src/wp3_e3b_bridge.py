"""E3b bridge statistic (record row of 30 Oct 2026). Usage: wp3_e3b_bridge.py DIR TAG_A TAG_B"""
import sys, json, numpy as np, pandas as pd
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import CCA
d, ta, tb = sys.argv[1:4]
def load(tag):
    return pd.concat({s: pd.read_parquet(f'{d}/olmoearth_{tag}_{s}.parquet') for s in (2018, 2025)}, names=['season', 'parcref'])
A, B = load(ta), load(tb)
A, B = A.align(B, join='inner', axis=0)
assert np.isfinite(A.values).all() and np.isfinite(B.values).all()
ZA = PCA(10, random_state=30).fit_transform(A.values); ZB = PCA(10, random_state=30).fit_transform(B.values)
def cancorr(Xtr, Ytr, Xte, Yte):
    c = CCA(10, max_iter=5000).fit(Xtr, Ytr); u, v = c.transform(Xte, Yte)
    return np.array([abs(np.corrcoef(u[:, k], v[:, k])[0, 1]) for k in range(10)])
parc = A.index.get_level_values('parcref').unique().values
rng = np.random.default_rng(30); perm = rng.permutation(parc); half = set(perm[:len(perm) // 2])
m = np.array([p in half for p in A.index.get_level_values('parcref')])
cross = (cancorr(ZA[m], ZB[m], ZA[~m], ZB[~m]) + cancorr(ZA[~m], ZB[~m], ZA[m], ZB[m])) / 2
ins = cancorr(ZA, ZB, ZA, ZB)
seas = A.index.get_level_values('season').values
per = {int(s): float(np.median(cancorr(ZA[seas == s], ZB[seas == s], ZA[seas == s], ZB[seas == s]))) for s in (2018, 2025)}
cos = lambda u, v: (u * v).sum(1) / np.linalg.norm(u, axis=1) / np.linalg.norm(v, axis=1)
out = dict(versions=[ta, tb], parcel_seasons=int(len(A)), parcels=int(len(parc)), dim=[A.shape[1], B.shape[1]],
           identical=bool(np.allclose(A.values, B.values)),
           cross_fitted=cross.round(3).tolist(), cross_fitted_median=float(np.median(cross)),
           in_sample_median=float(np.median(ins)), first_cc_in_sample=float(ins[0]), per_season_in_sample_median=per,
           cos_same_parcel_median=float(np.median(cos(A.values, B.values))),
           cos_random_median=float(np.median(cos(A.values, B.values[rng.permutation(len(B))]))),
           rule_met=bool(np.median(cross) >= 0.80))
print(json.dumps(out, indent=1))

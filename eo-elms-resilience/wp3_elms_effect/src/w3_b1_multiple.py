"""W3-B1 section 3 (protocol: w3_b1_inference_protocol.md): Romano-Wolf stepdown over Part F's 60 contrasts and W3-H Step 3's 4 families.
Each estimate and SE must first reproduce the published result files.

Input   as w3_z_partf.py, w3_z_partf_establishment.py, w3_z_partf_harvest.py, w3_h_step3.py; their result .json files
Output  wp3_elms_effect/results/w3_b1_multiple.json (aggregates only)
"""
import json, os, sys
import numpy as np, pandas as pd
from sklearn.decomposition import PCA

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'wp1_regional_signal', 'src'))
import wp3_did as w
import wp3_e3_embeddings as e3
from w3_z_partf import members, gfm, recovery, FAMS
from w3_h_step3 import index_matrix

B, SEED = 9999, 20261105
S26, S25, SE = range(2017, 2027), range(2017, 2026), range(2018, 2027)


def romano_wolf(th, se, I, seed=SEED):
    """Two-sided stepdown on studentized statistics; I holds influence by cell (cells x contrasts)."""
    rng = np.random.default_rng(seed)
    T = np.abs(th / se); order = np.argsort(-T)
    G = I.shape[0]; r = rng.choice([-1.0, 1.0], size=(B, G))
    Ts = np.abs(r @ I * np.sqrt(G / (G - 1)) / se)
    p = np.zeros(len(th)); last = 0.0
    for k, j in enumerate(order):
        mx = Ts[:, order[k:]].max(axis=1)
        last = max(last, float((1 + (mx >= T[j]).sum()) / (1 + B)))
        p[j] = last
    return p


def main():
    d = w.Data(); t = d.t
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    M = ms.in_matched_sample.values
    H, _ = index_matrix(t)
    Mem = members(t); Mem['All agreement land'] = np.ones(len(t), bool)
    obs_set, O, F, _ = gfm(t)
    wet = w.shock_table(); wet['shock'] = wet['wet']; main_sh = w.shock_table(**w.MAIN_SHOCK)
    x = pd.read_parquet(os.path.join(w.W3, 'data', 'w3_z_establishment.parquet')); x = x[x.parcref.isin(t.parcref)]
    i = pd.Series(np.arange(len(t)), index=t.parcref).reindex(x.parcref).values
    C = {k: np.full((len(t), len(w.SEASONS)), np.nan) for k in ('clear', 'high', 'water')}
    for k in C: C[k][i, x.year.values - w.SEASONS[0]] = x[k].values
    with np.errstate(all='ignore'):
        Y1 = np.where(C['clear'] >= 1, C['high'] / C['clear'], np.nan)
        Y3 = np.where(C['clear'] >= 3, C['high'] / C['clear'], np.nan)
        Yw = np.where(C['clear'] + C['water'] >= 1, C['high'] / (C['clear'] + C['water']), np.nan)
    emb, _ = e3.pre_entry_embedding(t.parcref.values)
    emb = np.where(np.isnan(emb), np.nanmean(emb, axis=0), emb)
    Z = PCA(n_components=10, random_state=0).fit_transform(emb)
    for k in range(10): t[f'emb_pc{k + 1}'] = Z[:, k]
    base = w.covariates
    def cov_e3(tt):
        X = base(tt)
        for k in range(10): X[f'emb_pc{k + 1}'] = tt[f'emb_pc{k + 1}'].values
        return X
    w.covariates = cov_e3
    idx = np.flatnonzero(obs_set)
    sub, _, _ = w.match(t.iloc[idx].reset_index(drop=True))
    w.covariates = base
    MO = np.zeros(len(t), bool); MO[idx[sub]] = True
    J = d.Y['ndvi_july_z']; Ib = F.astype('int64'); nc = len(d.cells)
    blocks = [('July NDVI', 'w3_z_partf.json', 'Wet shock: July NDVI, E3 matched sample', J, M, wet, S26, None, FAMS), ('July NDVI', 'w3_z_partf.json', 'Wet shock: July NDVI, observable parcels', J, MO, wet, S26, None, FAMS),
              ('July NDVI', 'w3_z_partf.json', 'Inundated vs not: July NDVI, observable parcels', np.where(O, J, np.nan), MO, wet, S26, Ib, FAMS),
              ('Recovery', 'w3_z_partf.json', 'Inundated vs not: recovery half-month, observable parcels', np.where(O, recovery(t), np.nan), MO, wet, S26, Ib, FAMS),
              ('Establishment', 'w3_z_partf_establishment.json', 'Wet shock: registered version, E3 matched sample (decides)', Y1, M, wet, SE, None, FAMS), ('Establishment', 'w3_z_partf_establishment.json', 'Wet shock: at least 3 clear dates', Y3, M, wet, SE, None, FAMS),
              ('Establishment', 'w3_z_partf_establishment.json', 'Wet shock: clear plus water in the denominator', Yw, M, wet, SE, None, FAMS), ('Establishment', 'w3_z_partf_establishment.json', 'Wet shock: observable parcels', Y1, MO, wet, SE, None, FAMS),
              ('Establishment', 'w3_z_partf_establishment.json', 'Inundated vs not: observable parcels', np.where(O, Y1, np.nan), MO, wet, SE, Ib, FAMS),
              ('Harvest, wet', 'w3_z_partf_harvest.json', 'Wet shock: harvest index, E3 matched sample (decides)', H, M, wet, S25, None, FAMS), ('Harvest, wet', 'w3_z_partf_harvest.json', 'Wet shock: harvest index, observable parcels', H, MO, wet, S25, None, FAMS),
              ('Harvest, wet', 'w3_z_partf_harvest.json', 'Inundated vs not: harvest index, observable parcels', np.where(O, H, np.nan), MO, wet, S25, Ib, FAMS),
              ('Harvest, dry or heat', 'w3_h_harvest.json', None, H, M, main_sh, S25, None, FAMS[:4])]
    pub = {f: json.load(open(os.path.join(w.RES, f))) for f in set(b[1] for b in blocks)}
    rows, IM = [], []
    for out, src, lab, Y, pm, sh, sn, inund, fams in blocks:
        for f in fams:
            sel = f != 'All agreement land'
            fam = np.where(Mem[f], 'F', 'O') if sel else d.fam
            crop = d.crop if inund is None else inund
            TR, CO = w.blocks(Y, d.G, d.cell, crop, inund is not None, list(sn), fam, pm, None, False)
            TR = w.attach_shocks(TR, d.cells, sh)
            if inund is not None: TR['shock'] = TR.key.values % 1000 == 2
            E = w.Est(TR, CO, d.cluster); T = E.TR
            p = (T.e.values >= 0) & (T.fam.values == 'F' if sel else True)
            W = E.weights(p & T.shock.values, p & ~T.shock.values)
            th, V, G, Iv = E.run([W])
            # influence by cell, on all cells, in cell order
            wt = W * T.nT.values; sw = pd.Series(wt).groupby(E.gkey).transform('sum').values
            v = W * T.R.values - np.where(E.first, sw * T.Cres.values, 0.0)
            I = np.zeros(nc); s = pd.Series(v).groupby(E.clu).sum(); I[s.index.values] = s.values
            est, se = float(th[0]), float(np.sqrt(V[0, 0]))
            pubrow = next(r['frozen'] for r in (pub[src]['step3']['rows'] if lab is None else pub[src]['rows']) if r['family'] == f and (lab is None or r['contrast'] == lab))
            assert abs(est - pubrow['est']) < 1e-9 and abs(se - pubrow['se']) < 1e-9, (lab, f, est, pubrow['est'], se, pubrow['se'])
            rows.append(dict(outcome=out, contrast=lab or 'Dry or heat: harvest index, E3 matched sample (decides)', family=f, est=est, se=se, lo=est - 1.96 * se, hi=est + 1.96 * se))
            IM.append(I); w.log(out, lab, f, round(est, 4), round(se, 4))
    assert len(rows) == 64, len(rows)
    th = np.array([r['est'] for r in rows]); se = np.array([r['se'] for r in rows]); I = np.column_stack(IM)
    pall = romano_wolf(th, se, I)
    out = np.array([r['outcome'] for r in rows]); pw = np.zeros(len(rows))
    for o in set(out):
        m = out == o; pw[m] = romano_wolf(th[m], se[m], I[:, m])
    from scipy import stats
    for r, a, b, t_ in zip(rows, pall, pw, th / se):
        r.update(p_raw=float(2 * stats.norm.sf(abs(t_))), p_rw_all=float(a), p_rw_outcome=float(b), survives=bool(a < .05))
    json.dump(dict(rows=rows, draws=B, seed=SEED), open(os.path.join(w.RES, 'w3_b1_multiple.json'), 'w'), indent=1, default=float)
    w.log('reproduced 64 of 64; survivors', sum(r['survives'] for r in rows))
    w.log('done')


if __name__ == '__main__':
    main()

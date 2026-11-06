"""WP3 E3b harvest rule, blind precision check (protocol: wp3_e3b_olmoearth_matching_protocol.md, record of 6 November 2026). How precisely the E3b subsample can compare harvest
contrasts between matched samples, using M0 and MA as a stand-in for MO and MA. Writes and prints standard errors only: no estimate leaves this script.

Input   as wp3_e3_embeddings.py, plus data/e3b_subsample.parquet, data/w3_h_field_index.parquet
Output  wp3_elms_effect/results/wp3_e3b_harvest_precision.json (standard errors and counts only)
"""
import json, os, sys
import numpy as np, pandas as pd
from sklearn.decomposition import PCA

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
from w3_z_partf import members
from w3_h_step3 import index_matrix
from wp3_e3_embeddings import pre_entry_embedding

S25 = range(2017, 2026)
PCS = [f'emb_pc{k + 1}' for k in range(10)]


def main():
    d = w.Data(); t = d.t
    sub = pd.read_parquet(os.path.join(w.W3, 'data', 'e3b_subsample.parquet'))
    ix = np.flatnonzero(t.parcref.isin(sub.parcref).values)
    ts = t.iloc[ix].reset_index(drop=True).copy()
    emb, _ = pre_entry_embedding(ts.parcref.values)
    emb = np.where(np.isnan(emb), np.nanmean(emb, axis=0), emb)
    Z = PCA(n_components=10, random_state=0).fit(emb).transform(emb)
    for k, c in enumerate(PCS): ts[c] = Z[:, k]
    base = w.covariates
    M0 = w.match(ts)[0]
    def cov(tt):
        X = base(tt)
        for c in PCS: X[c] = tt[c].values
        return X
    w.covariates = cov
    MA = w.match(ts)[0]
    w.covariates = base
    H, _ = index_matrix(t); Hs = H[ix]; Mem = members(t)
    G, cell, crop, fam0 = d.G[ix], d.cell[ix], d.crop[ix], d.fam[ix]
    main_sh = w.shock_table(**w.MAIN_SHOCK)
    wet_sh = w.shock_table(**w.MAIN_SHOCK); wet_sh['shock'] = wet_sh['wet']
    block = d.block50[cell]
    def theta(f, sh, pm, se=False):
        sel = f != 'All agreement land'
        fam = np.where(Mem[f][ix], 'F', 'O') if sel else fam0
        TR0, CO = w.blocks(Hs, G, cell, crop, False, list(S25), fam, pm, None, False)
        E = w.Est(w.attach_shocks(TR0, d.cells, sh), CO, d.cluster)
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        W = E.weights(p & TR.shock.values, p & ~TR.shock.values); th = float((W * TR.tau_sum.values).sum())
        if not se: return th
        _, V, g, _ = E.run([W]); return th, float(np.sqrt(V[0, 0])), int(g), int(TR.nT.values[p].sum())
    rows = []; blocks_ = sorted(set(block))
    for lab, f, sh in (('Dry or heat, all land', 'All agreement land', main_sh), ('Dry or heat, management-only', 'Management-only', main_sh), ('Wet, all land', 'All agreement land', wet_sh)):
        a0, se0, g0, n0 = theta(f, sh, M0, True); aA, seA, gA, nA = theta(f, sh, MA, True)
        J = np.array([[theta(f, sh, MA & (block != b)), theta(f, sh, M0 & (block != b))] for b in blocks_])
        B = len(blocks_); jk = lambda v: float(np.sqrt((B - 1) / B * ((v - v.mean()) ** 2).sum()))
        r = dict(contrast=lab, se_cell_MA=seA, se_cell_M0=se0, clusters_MA=gA, parcel_seasons_MA=nA, se_block_jackknife_MA=jk(J[:, 0]), se_difference_M0_MA_block_jackknife=jk(J[:, 0] - J[:, 1]), blocks=B)
        rows.append(r); print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    json.dump(dict(fields_M0=int(M0.sum()), fields_MA=int(MA.sum()), rows=rows), open(os.path.join(w.RES, 'wp3_e3b_harvest_precision.json'), 'w'), indent=1)
    print('fields', int(M0.sum()), int(MA.sum()))


if __name__ == '__main__':
    main()

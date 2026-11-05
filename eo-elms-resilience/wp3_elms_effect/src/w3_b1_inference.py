"""W3-B1 sections 1, 2 (inputs) and 4 (protocol: w3_b1_inference_protocol.md): inference when shocks are few, event studies for
Rambachan-Roth, and crop conditioning. Point estimates are the registered ones; only the uncertainty changes in section 1.

Input   as w3_h_step3.py and w3_z_partf.py, plus matched_sample.parquet, shared/data/schemes/national/{cs_options,sfi_actions,rpa_parcel_points}.csv
Output  wp3_elms_effect/results/w3_b1_inference.json, w3_b1_events.json (aggregates only)
"""
import json, os, sys
import numpy as np, pandas as pd
from scipy import stats
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'wp1_regional_signal', 'src'))
import wp3_did as w
from w3_z_partf import members
from w3_h_step3 import index_matrix, family_codes
from wp1_nowcast import DEFRA

B, SEED = 1999, 20261105
S25, S26 = range(2017, 2026), range(2017, 2027)
NAT = os.path.join(w.D, 'schemes', 'national')


def merged_cells(d):
    """Connected components of ERA5 cells linked by a CS contract or an SFI application. Reads ID, parcel and coordinate columns only."""
    p = d.t.parcref.str.strip().str.upper().values
    cell_of = pd.Series(d.cell, index=p)
    cs = pd.read_csv(os.path.join(NAT, 'cs_options.csv'), dtype=str, usecols=['CONTRACT_ID', 'PARCREF']).dropna()
    cs['parcref'] = cs.PARCREF.str.strip().str.upper(); cs['id'] = 'CS' + cs.CONTRACT_ID
    r = pd.read_csv(os.path.join(NAT, 'rpa_parcel_points.csv'), dtype=str, usecols=['parcel_reference', 'x_bng', 'y_bng'])
    r['x'], r['y'] = pd.to_numeric(r.x_bng, errors='coerce'), pd.to_numeric(r.y_bng, errors='coerce')
    r = r.dropna(subset=['x', 'y']).drop_duplicates('parcel_reference').reset_index(drop=True)
    s = pd.read_csv(os.path.join(NAT, 'sfi_actions.csv'), dtype=str, usecols=['app_id', 'x_bng', 'y_bng']).dropna()
    s['x'], s['y'] = pd.to_numeric(s.x_bng, errors='coerce'), pd.to_numeric(s.y_bng, errors='coerce')
    s = s.dropna(subset=['x', 'y']).drop_duplicates(['app_id', 'x', 'y'])
    _, ix = cKDTree(r[['x', 'y']].values).query(s[['x', 'y']].values, k=1)
    s['parcref'] = r.parcel_reference.str.strip().str.upper().values[ix]; s['id'] = 'SFI' + s.app_id
    a = pd.concat([cs[['id', 'parcref']], s[['id', 'parcref']]], ignore_index=True)
    a = a[a.parcref.isin(cell_of.index)].drop_duplicates()
    a['cell'] = cell_of.reindex(a.parcref).values
    linked = a.parcref.nunique(), int(((d.G > 0) & pd.Series(p).isin(a.parcref).values).sum())
    g = a.drop_duplicates(['id', 'cell'])
    ids = pd.factorize(g.id)[0]; n = len(d.cells)
    A = coo_matrix((np.ones(len(g)), (g.cell.values, ids + n)), shape=(n + ids.max() + 1, n + ids.max() + 1))
    _, lab = connected_components(A, directed=False)
    lab = lab[:n]
    vc = pd.Series(lab).value_counts()
    return pd.factorize(lab)[0], dict(clusters=int(vc.size), largest_share_of_cells=float(vc.iloc[0] / n), treated_linked=linked[1], agreements=int(a.id.nunique()),
                                      agreements_in_more_than_one_cell=int((g.groupby('id').cell.nunique() > 1).sum()))


def main():
    d = w.Data(); t = d.t
    m0 = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet')).set_index('parcref').in_matched_sample
    M0 = m0.reindex(t.parcref).fillna(False).values.astype(bool)
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    ME = ms.in_matched_sample.values
    H, _ = index_matrix(t)
    Mem = members(t)
    main_sh = w.shock_table(**w.MAIN_SHOCK)
    wet_sh = w.shock_table(**w.MAIN_SHOCK); wet_sh['shock'] = wet_sh['wet']
    comp, comp_info = merged_cells(d); w.log('merged', comp_info)
    reg = pd.Series(t.region.map(DEFRA).values).groupby(d.cell).agg(lambda x: x.value_counts().index[0])
    reg_of = pd.factorize(reg.reindex(range(len(d.cells))).values)[0]

    def est(Y, pm, fam, sh, sn, use_crop, uni=False):
        TR, CO = w.blocks(Y, d.G, d.cell, d.crop, use_crop, list(sn), fam, pm, None, uni)
        return w.Est(w.attach_shocks(TR, d.cells, sh), CO, d.cluster)

    J = d.Y['ndvi_july_z']
    fam_of = lambda f: (np.where(Mem[f], 'F', 'O'), True) if f != 'All agreement land' else (d.fam, False)
    def T(name, Y, pm, f, sh, sn, use_crop): return dict(name=name, Y=Y, pm=pm, f=f, sh=sh, sn=sn, use_crop=use_crop)
    targets = [T('A: H1 July NDVI, frozen', J, M0, 'All agreement land', main_sh, S25, True), T('B: H1 July NDVI, E3 sample', J, ME, 'All agreement land', main_sh, S25, True)]
    targets += [T(f'C: dry or heat harvest, {f}', H, ME, f, main_sh, S25, False) for f in ('All agreement land', 'Management-only')]
    targets += [T(f'D: wet-winter harvest, {f}', H, ME, f, wet_sh, S25, False) for f in ('All agreement land', 'Management-only', 'Buffer strips')]
    targets += [T(f'E: wet-winter July NDVI, {f}', J, ME, f, wet_sh, S26, False) for f in ('All agreement land', 'Buffer strips')]

    rng = np.random.default_rng(SEED)
    res = []
    for x in targets:
        fam, sel = fam_of(x['f'])
        E = est(x['Y'], x['pm'], fam, x['sh'], x['sn'], x['use_crop'])
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        sk, nT, tau = TR.shock.values, TR.nT.values, TR.tau_sum.values
        W = E.weights(p & sk, p & ~sk)
        th0 = float((W * tau).sum())
        def v(cl):
            _, V, G, I = E.run([W], clusters=cl); return float(V[0, 0]), int(G), I[:, 0]
        cell = TR.cell.values
        vc, gc, _ = v(E.clu)
        vm, gm, _ = v(comp[cell])
        vb, gb, _ = v(d.block50[cell])
        vr, gr, _ = v(reg_of[cell])
        # The estimator's influence functions subtract group-time means, so they sum to about zero within a season and can't carry
        # season-level uncertainty. These scores use each row's deviation from its side's mean effect, without that conditioning.
        Na, Nb = nT[p & sk].sum(), nT[p & ~sk].sum(); ma, mb = tau[p & sk].sum() / Na, tau[p & ~sk].sum() / Nb
        sc = np.where(p & sk, (tau - nT * ma) / Na, 0.0) - np.where(p & ~sk, (tau - nT * mb) / Nb, 0.0)
        def lz(cl):
            I_ = pd.Series(sc).groupby(cl).sum().values; I_ = I_[I_ != 0]; g = len(I_); return float(I_ @ I_ * g / (g - 1)), g
        vs, G_s = lz(TR.t.values)
        vcl, _ = lz(cell); vcs, _ = lz(cell * 10000 + TR.t.values); vrs, g_rs = lz(reg_of[cell])
        two = vcl + vs - vcs
        ci = lambda var, q: dict(se=float(np.sqrt(var)), lo=th0 - q * np.sqrt(var), hi=th0 + q * np.sqrt(var))
        tq = lambda g: float(stats.t.ppf(.975, g - 1))
        inf = dict(cell=ci(vc, 1.96) | dict(G=gc), agreement_merged=ci(vm, 1.96) | dict(G=gm), block50=ci(vb, 1.96) | dict(G=gb), region=ci(vr, tq(gr)) | dict(G=gr),
                   two_way=ci(two, 1.96) if two > 0 else dict(se=None), season=ci(vs, tq(G_s)) | dict(G=G_s), cell_no_conditioning=ci(vcl, 1.96), region_no_conditioning=ci(vrs, tq(g_rs)) | dict(G=g_rs))
        # permutation of shock seasons
        sn = list(x['sn']); col = {'shock': x['sh'].shock}
        SH = x['sh'].shock.reindex(pd.MultiIndex.from_product([d.cells, sn])).fillna(False).values.reshape(len(d.cells), len(sn)).astype(bool)
        tix = TR.t.values - sn[0]; draws = []; drop = 0
        for _ in range(B):
            pi = rng.permutation(len(sn)); s2 = SH[cell, pi[tix]]
            a, b = p & s2, p & ~s2
            if not a.any() or not b.any(): drop += 1; continue
            draws.append(tau[a].sum() / nT[a].sum() - tau[b].sum() / nT[b].sum())
        draws = np.array(draws); pperm = float((1 + (np.abs(draws) >= abs(th0)).sum()) / (1 + len(draws)))
        loo = {}
        for s in sorted(set(TR.t.values[p])):
            keep = p & (TR.t.values != s)
            a, b = keep & sk, keep & ~sk
            if a.any() and b.any():
                wl = E.weights(a, b); th, V, G, _ = E.run([wl]); loo[int(s)] = w.row('', th, V, 0, G)
        shares = {int(s): float(nT[p & sk & (TR.t.values == s)].sum() / nT[p & sk].sum()) for s in sorted(set(TR.t.values[p & sk]))}
        robust = bool((inf['season']['lo'] > 0 or inf['season']['hi'] < 0) and pperm < .05)
        res.append(dict(name=x['name'], est=th0, inference=inf, permutation=dict(p=pperm, draws=len(draws), dropped=drop), leave_one_out=loo, hazard_season_shares=shares, robust_to_few_shocks=robust))
        w.log(x['name'], round(th0, 4), 'cell', round(np.sqrt(vc), 4), 'season', round(np.sqrt(vs), 4), G_s, 'perm', round(pperm, 3), robust)
    # event studies for HonestDiD
    ev = {}
    for x in targets:
        if x['name'].startswith(('A', 'B')) or x['name'].endswith('harvest, All agreement land'):
            fam, _ = fam_of(x['f'])
            E = est(x['Y'], x['pm'], fam, x['sh'], x['sn'], x['use_crop'], uni=True)
            TR = E.TR; es = [-4, -3, -2, 0, 1, 2, 3]
            We = [E.weights((TR.e.values == e) & TR.shock.values, (TR.e.values == e) & ~TR.shock.values) for e in es]
            th, V, G, _ = E.run(We)
            ev[x['name']] = dict(es=es, beta=th.tolist(), V=V.tolist(), n_hazard={int(e): int(TR.nT.values[(TR.e.values == e) & TR.shock.values].sum()) for e in es})
    json.dump(ev, open(os.path.join(w.RES, 'w3_b1_events.json'), 'w'), indent=1, default=float)
    # section 4: crop conditioning
    crop = {}
    Gp, tmax = np.where(d.G > 0, d.G - 2, 0), np.where(d.G > 0, d.G, 9999)
    for lab, pm in (('A: frozen sample', M0), ('B: E3 sample', ME)):
        for uc in (True, False):
            E1 = d.est(pmask=pm, use_crop=uc); th, V, G, _ = E1.run(w.h1(E1)[:1])
            Ep = d.est(pmask=pm, use_crop=uc, G=Gp, tmax=tmax); a, Va, Ga, _ = Ep.run(w.h1(Ep)[:1])
            crop[f'{lab}, crop strata {"yes" if uc else "no"}'] = dict(H1=w.row('', th, V, 0, G), placebo=w.row('', a, Va, 0, Ga))
    cer = np.column_stack([t[f'cereal_{y}'].astype('float64').values if f'cereal_{y}' in t else np.full(len(t), np.nan) for y in w.SEASONS])
    fc = family_codes()
    pc = pd.read_parquet(os.path.join(w.W3, 'data', 'w3_s_parcel_codes.parquet')); pc = pc[pc.scheme.isin(['CS', 'SFI'])]
    extra = {'Herbal leys': 'herbal_leys', 'Grassland options': 'grassland_options'}
    fams = dict(Mem) | {k: t.parcref.isin(pc[pc.code.isin(fc[fc == v].index)].parcref).values for k, v in extra.items()}
    rot = []
    for f in ['All agreement land', 'Management-only', 'Cover crops', 'No-till', 'Herbal leys', 'Grassland options', 'Buffer strips']:
        sel = f != 'All agreement land'
        fam = np.where(fams[f], 'F', 'O') if sel else d.fam
        def eff(E):
            TR = E.TR; q = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
            th, V, G, _ = E.run([E.weights(q)]); return w.row('', th, V, 0, G, int(TR.nT.values[q].sum()))
        E = est(cer, ME, fam, main_sh, S25, False)
        TRp, COp = w.blocks(cer, Gp, d.cell, d.crop, False, list(range(2017, 2021)), fam, ME, tmax, False)
        Ep = w.Est(w.attach_shocks(TRp, d.cells, main_sh), COp, d.cluster)
        a, pl = eff(E), eff(Ep)
        rot.append(dict(family=f, effect=a, placebo=pl, shifts=bool((a['lo'] > 0 or a['hi'] < 0) and abs(a['est']) >= .02 and pl['lo'] <= 0 <= pl['hi'])))
        w.log('rotation', f, round(a['est'], 3), round(pl['est'], 3))
    json.dump(dict(targets=res, merged_clusters=comp_info, crop_conditioning=crop, rotations=rot), open(os.path.join(w.RES, 'w3_b1_inference.json'), 'w'), indent=1, default=float)
    w.log('done')


if __name__ == '__main__':
    main()

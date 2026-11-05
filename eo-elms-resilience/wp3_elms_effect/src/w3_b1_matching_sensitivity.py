"""W3-B1 matching sensitivity (protocol: w3_b1_matching_sensitivity_protocol.md): how strong an unobserved factor would have to be, by removing covariate
groups from the frozen matching and by bounding imbalance times shock response against the observed covariates.

Input   as w3_b1_inference.py, plus shared/data/embeddings/parcels, results/w3_b1_inference.json
Output  wp3_elms_effect/results/w3_b1_matching_sensitivity.md, .json (aggregates only)
"""
import json, os, re, sys
import numpy as np, pandas as pd
from sklearn.decomposition import PCA

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
from w3_z_partf import members
from w3_h_step3 import index_matrix
from wp3_e3_embeddings import pre_entry_embedding

S25 = range(2017, 2026)
AFTER = range(2021, 2026)
PCS = [f'emb_pc{k + 1}' for k in range(10)]
GROUPS = {'NDVI trajectory': r'^ndvi_p\d\d', 'Crop history': r'^(cereal|crop)_', 'Flood zone': r'^fz[23]$', 'Peat class': r'^peat_', 'Scheme intensity, 1 km': r'^scheme_1km$', 'Embedding components': r'^emb_pc'}
LIMIT = .10
PLACEBO = {'A: H1 July NDVI, frozen': '+0.079, fails', 'B: H1 July NDVI, E3 sample': '+0.080, fails', 'C: dry or heat harvest, All agreement land': '-0.081, passes narrowly',
           'C: dry or heat harvest, Management-only': '-0.095, passes narrowly', 'D: wet-winter harvest, All agreement land': '-0.128, fails',
           'D: wet-winter harvest, Management-only': '-0.139, fails', 'D: wet-winter harvest, Buffer strips': '-0.162, fails'}


def gamma(Y, X, ctrl, cell, crop, use_crop, shock_of, seasons):
    """Slope in shock seasons minus slope in other seasons, within strata, in never-treated fields of the matched sample. X standardised."""
    ix = np.flatnonzero(ctrl); num = {True: 0.0, False: 0.0}; den = {True: 0.0, False: 0.0}
    V = X[ix]
    for s in seasons:
        j = s - w.SEASONS[0]; y = Y[ix, j].astype('float64'); ok = np.isfinite(y)
        key = cell[ix] * 1000 + (crop[ix, j] + 1 if use_crop else 0)
        sh = shock_of(cell[ix], s)
        k = pd.factorize(key[ok])[0]
        n = np.bincount(k); ybar = np.bincount(k, y[ok]) / n
        Xok = V[ok]
        Xbar = np.column_stack([np.bincount(k, Xok[:, c]) / n for c in range(Xok.shape[1])])
        yd, Xd, sk = y[ok] - ybar[k], Xok - Xbar[k], sh[ok]
        for side in (True, False):
            m = sk == side
            num[side] = num[side] + Xd[m].T @ yd[m]; den[side] = den[side] + (Xd[m] ** 2).sum(0)
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where((den[True] > 1) & (den[False] > 1), num[True] / den[True] - num[False] / den[False], np.nan)


def report():
    o = json.load(open(os.path.join(w.RES, 'w3_b1_matching_sensitivity.json'))); rows = o['rows']; e = o['embedding_test']
    L = ['# W3-B1 matching sensitivity', '', 'Protocol: [w3_b1_matching_sensitivity_protocol.md](w3_b1_matching_sensitivity_protocol.md). Labels beside registered results; no registered reading changes. Exploratory. Baseline matching reproduced both saved samples exactly, and the estimates reproduced the published ones.', '',
         '## Summary', '', 'k1 and k2: how many times stronger than the strongest observed factor an unobserved one must be to take the estimate to zero. The label uses the smaller.', '',
         '| Result | Estimate | S, largest group shift | k1 | Largest δ × γ | k2 | Label | Placebo |', '|---|---:|---:|---:|---:|---:|---|---|']
    for r in rows:
        L.append(f"| {r['name']} | {r['est']:+.3f} | {r['S']:.3f} | {r['k1']:.2f} | {r['max_b']:.3f} | {r['k2']:.2f} | {r['label']} | {r['placebo']} |")
    gs = list(GROUPS)
    L += ['', '## Check 1: shift when a group is left out of the matching', '', '| Result | ' + ' | '.join(gs) + ' | No matching |', '|---|' + '---:|' * (len(gs) + 1)]
    for r in rows:
        L.append(f"| {r['name']} | " + ' | '.join(f"{r['shifts'][g]:+.3f}" if g in r['shifts'] else '' for g in gs) + f" | {r['no_matching_shift']:+.3f} |")
    L += ['', '## Check 2: strongest observed covariates', '', 'δ before matching, for the result\'s family; γ per SD in never-treated matched fields, 2021–2025. Marginal slopes, so not additive.', '',
          '| Result | Largest δ × γ: covariate (δ, γ) | Largest δ: covariate (δ, γ) | Largest γ: covariate (δ, γ) | γ needed at largest δ | δ needed at largest γ | Bias to pass the 0.10 limit |', '|---|---|---|---|---:|---:|---:|']
    c = lambda q: f"{q['covariate']} ({q['delta']:+.2f}, {q['gamma']:+.3f})"
    for r in rows:
        L.append(f"| {r['name']} | {c(r['strongest_b'])} | {c(r['largest_delta'])} | {c(r['largest_gamma'])} | {r['gamma_needed_at_largest_delta']:.3f} | {r['delta_needed_at_largest_gamma']:.2f} | {r['bias_to_limit']:.3f} |")
    L += ['', f"**Check on the method:** embeddings in the frozen sample predicted a shift of {e['predicted_shift']:+.4f}; the realised change from A to B was {e['realised_shift']:+.4f}. Both small, opposite signs, one data point.", '',
          '## Reading', '',
          '- **The harvest results depend on the embeddings.** Without them in the matching, dry-or-heat harvest goes from +0.039 to -0.001 on all land and +0.041 to 0.000 on management-only; wet harvest from -0.040 to -0.013. No other group moves any row by more than 0.017.',
          '- **That is what makes dry-or-heat harvest fragile,** both rows just under k = 1 (0.97 and 0.998). The label is close to its boundary, and the substance is not: the embeddings are the difference between a small gain and none.',
          '- **Direction.** Embedding matching removes an imbalance that pushes the harvest contrast down, so this is not evidence against the gain by itself: matching on the embeddings may be correcting a real bias. It does mean that the gain rests on one matching choice.',
          '- **H1 is strong here, and that does not clear it.** H1 barely depends on matching, but its placebo fails at about the size of the estimate (+0.079, +0.080), so differences of the needed size already exist, in a form matching does not remove.',
          '- **Wet buffer strips are strong, wet all land and management-only moderate, all with failed placebos.**',
          '- **Equivalence:** the bias needed to push dry-or-heat harvest past 0.10 t/ha (0.061, 0.059) is about 1.5 times S, so a factor as strong as the strongest observed would not on its own do it, in either direction, from this estimate.',
          '- **Not covered:** the few-shocks spread and HonestDiD are separate. Both checks consider one factor at a time.']
    open(os.path.join(w.RES, 'w3_b1_matching_sensitivity.md'), 'w').write('\n'.join(L) + '\n')


def main():
    d = w.Data(); t = d.t
    pub = {x['name']: x for x in json.load(open(os.path.join(w.RES, 'w3_b1_inference.json')))['targets']}
    M0 = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet')).set_index('parcref').in_matched_sample.reindex(t.parcref).fillna(False).values.astype(bool)
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    ME = ms.in_matched_sample.values
    emb, cnt = pre_entry_embedding(t.parcref.values)
    emb = np.where(np.isnan(emb), np.nanmean(emb, axis=0), emb)
    Z = PCA(n_components=10, random_state=0).fit(emb).transform(emb)
    for k, c in enumerate(PCS): t[c] = Z[:, k]
    base_cov = w.covariates
    def cov_e3(tt):
        X = base_cov(tt)
        for c in PCS: X[c] = tt[c].values
        return X
    def rematch(cov, drop):
        pat = GROUPS[drop] if drop else None
        def f(tt):
            X = cov(tt)
            return X.loc[:, [c for c in X.columns if not re.search(pat, c)]] if pat else X
        w.covariates = f
        try:
            return w.match(t)[0]
        finally:
            w.covariates = base_cov
    assert (rematch(base_cov, None) == M0).all(), 'frozen sample not reproduced'
    assert (rematch(cov_e3, None) == ME).all(), 'E3 sample not reproduced'
    w.log('baseline samples reproduced')
    H, _ = index_matrix(t); Mem = members(t); J = d.Y['ndvi_july_z']
    main_sh = w.shock_table(**w.MAIN_SHOCK)
    wet_sh = w.shock_table(**w.MAIN_SHOCK); wet_sh['shock'] = wet_sh['wet']
    def T(name, Y, frozen, f, sh, uc, unit): return dict(name=name, Y=Y, frozen=frozen, f=f, sh=sh, uc=uc, unit=unit)
    targets = [T('A: H1 July NDVI, frozen', J, True, 'All agreement land', main_sh, True, 'SD'), T('B: H1 July NDVI, E3 sample', J, False, 'All agreement land', main_sh, True, 'SD')]
    targets += [T(f'C: dry or heat harvest, {f}', H, False, f, main_sh, False, 't/ha') for f in ('All agreement land', 'Management-only')]
    targets += [T(f'D: wet-winter harvest, {f}', H, False, f, wet_sh, False, 't/ha') for f in ('All agreement land', 'Management-only', 'Buffer strips')]

    def theta(x, pm):
        sel = x['f'] != 'All agreement land'
        fam = np.where(Mem[x['f']], 'F', 'O') if sel else d.fam
        TR0, CO = w.blocks(x['Y'], d.G, d.cell, d.crop, x['uc'], list(S25), fam, pm, None, False)
        E = w.Est(w.attach_shocks(TR0, d.cells, x['sh']), CO, d.cluster)
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        Wt = E.weights(p & TR.shock.values, p & ~TR.shock.values)
        return float((Wt * TR.tau_sum.values).sum())
    def shock_fn(sh):
        def f(cell, s):
            return sh.shock.reindex(pd.MultiIndex.from_arrays([d.cells[cell], np.full(len(cell), s)])).fillna(False).values.astype(bool)
        return f

    # check 1: leave one group out
    samples = {}
    for frozen, cov in ((True, base_cov), (False, cov_e3)):
        for g in GROUPS:
            if frozen and g == 'Embedding components': continue
            samples[frozen, g] = rematch(cov, g)
            w.log('rematched', 'frozen' if frozen else 'E3', g, int(samples[frozen, g].sum()))
    res = []
    Xbase, Xe3 = base_cov(t), cov_e3(t)
    for x in targets:
        pm = M0 if x['frozen'] else ME
        th0 = theta(x, pm)
        assert abs(th0 - pub[x['name']]['est']) < 1e-9, (x['name'], th0)
        shifts = {g: theta(x, samples[x['frozen'], g]) - th0 for g in GROUPS if (x['frozen'], g) in samples}
        nomatch = theta(x, None) - th0
        S = max(map(abs, shifts.values())); k1 = abs(th0) / S
        # check 2: imbalance times shock response
        X = Xbase if x['frozen'] else Xe3
        sd = X.std().replace(0, np.nan); Xs = ((X - X.mean()) / sd).values
        tr = Mem[x['f']] if x['f'] != 'All agreement land' else d.G > 0
        delta = np.nanmean(Xs[tr], axis=0) - np.nanmean(Xs[d.G == 0], axis=0)
        gam = gamma(x['Y'], np.nan_to_num(Xs), pm & (d.G == 0), d.cell, d.crop, x['uc'], shock_fn(x['sh']), AFTER)
        b = np.abs(delta * gam); names = np.array(X.columns)
        i_b, i_d, i_g = np.nanargmax(b), np.nanargmax(np.abs(delta)), np.nanargmax(np.abs(gam))
        k2 = abs(th0) / b[i_b]; k = min(k1, k2)
        r = dict(name=x['name'], unit=x['unit'], est=th0, placebo=PLACEBO[x['name']], shifts=shifts, no_matching_shift=nomatch, S=S, k1=k1,
                 strongest_b=dict(covariate=names[i_b], b=float(b[i_b]), delta=float(delta[i_b]), gamma=float(gam[i_b])), max_b=float(b[i_b]), k2=k2,
                 largest_delta=dict(covariate=names[i_d], delta=float(delta[i_d]), gamma=float(gam[i_d])), largest_gamma=dict(covariate=names[i_g], delta=float(delta[i_g]), gamma=float(gam[i_g])),
                 gamma_needed_at_largest_delta=abs(th0) / abs(delta[i_d]), delta_needed_at_largest_gamma=abs(th0) / abs(gam[i_g]), bias_to_limit=LIMIT - abs(th0), k=k,
                 label='fragile' if k < 1 else 'moderate' if k < 3 else 'strong')
        res.append(r)
        w.log(x['name'], round(th0, 3), {g: round(v, 3) for g, v in shifts.items()}, 'none', round(nomatch, 3), 'k1', round(k1, 2), 'k2', round(k2, 2), r['label'], r['strongest_b'])
    # check on the method: the embeddings were unobserved in the frozen match
    a = targets[0]
    sdE = Xe3[PCS].std(); Xp = ((Xe3[PCS] - Xe3[PCS].mean()) / sdE).values
    dA = Xp[M0 & (d.G > 0)].mean(0) - Xp[M0 & (d.G == 0)].mean(0)
    gA = gamma(a['Y'], Xp, M0 & (d.G == 0), d.cell, d.crop, True, shock_fn(main_sh), AFTER)
    pred = float(-(dA * gA).sum()); real = res[1]['est'] - res[0]['est']
    out = dict(rows=res, embedding_test=dict(predicted_shift=pred, realised_shift=real, delta=dA.tolist(), gamma=gA.tolist()))
    json.dump(out, open(os.path.join(w.RES, 'w3_b1_matching_sensitivity.json'), 'w'), indent=1, default=float)
    report()
    w.log('embedding test', round(pred, 4), round(real, 4), 'done')


if __name__ == '__main__':
    main()

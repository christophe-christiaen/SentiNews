"""WP3 E3b: does the agreement-land drought cushion survive matching on OlmoEarth embeddings?
Protocol: wp3_elms_effect/results/wp3_e3b_olmoearth_matching_protocol.md (registered 30 October 2026; R4 added
6 November 2026). Exploratory, no multiple-testing correction.

On the E3b subsample (seed 30), three matched samples with the section 7 matching unchanged:
  M0 original covariates; MA + 10 AlphaEarth components (as E3); MO + 10 OlmoEarth components.
OlmoEarth pre-entry embedding = mean over farm seasons 2017/18, 2018/19, 2019/20 (files s2018, s2019, s2020) of the
16 x 16, patch-4 field embedding; fields with no pre-entry OlmoEarth embedding are reported and dropped from the
subsample for all three samples (like for like). Components fitted on all remaining subsample fields.
Balance for all covariates and both component sets in all three samples; H1-H3 (frozen plan and within cohort);
harvest contrasts for R4 as in wp3_e3b_harvest_precision.py.

Usage   wp3_e3b_matching.py EMB_DIR [--check]
        EMB_DIR = folder of s{season}_b{k}.parquet files (the project Drive's e3b_emb, passed in, not hard-coded).
        --check reads the embeddings and prints counts only (no balance, no estimate).
Output  wp3_elms_effect/results/wp3_e3b_olmoearth_matching.md, .json (aggregates only)
"""
import argparse, glob, json, os, sys
import numpy as np, pandas as pd
from sklearn.decomposition import PCA

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
import wp3_within_cohort as wc
from wp3_e3_embeddings import pre_entry_embedding

SEASONS = (2018, 2019, 2020)            # farm seasons 2017/18-2019/20
AE = [f'ae_pc{k + 1}' for k in range(10)]
OE = [f'oe_pc{k + 1}' for k in range(10)]
S25 = range(2017, 2026)
H1_FULL_E3 = 0.087


def olmoearth_pre_entry(emb_dir, parcrefs):
    acc = cnt = None; per_season = {}
    for s in SEASONS:
        fs = sorted(glob.glob(os.path.join(emb_dir, f's{s}_b*.parquet')))
        d = pd.concat([pd.read_parquet(f) for f in fs])
        d = d[~d.index.duplicated()].reindex(parcrefs)
        v = d.values.astype('float64'); ok = ~np.isnan(v).any(axis=1)
        per_season[s] = dict(files=len(fs), fields=int(ok.sum()))
        acc = np.where(ok[:, None], v, 0) if acc is None else acc + np.where(ok[:, None], v, 0)
        cnt = ok.astype(int) if cnt is None else cnt + ok
    mean = acc / np.maximum(cnt, 1)[:, None]
    return mean, cnt, per_season


def match_weighted(ts, cols):
    """w.match with `cols` added to the covariates; also returns the matching weights, captured from w.match's own
    balance call so the matching is exactly the section 7 one."""
    base, cap = w.covariates, {}
    def cov(tt):
        X = base(tt)
        for c in cols: X[c] = tt[c].values
        return X
    smd0 = w.smd
    def smd_capture(X, treat, wt=None):
        if wt is not None: cap['wt'] = pd.Series(wt, index=X.index)
        return smd0(X, treat, wt)
    w.covariates, w.smd = cov, smd_capture
    try:
        M, bal, _ = w.match(ts)
    finally:
        w.covariates, w.smd = base, smd0
    return M, bal, cap['wt']


def balance(ts, M, wt, cols):
    X = w.covariates(ts)
    for c in AE + OE: X[c] = ts[c].values
    treat = (ts.G > 0).values
    s = w.smd(X[M], treat[M], wt.reindex(X.index[M]).values)
    return dict(max_covariates=float(s.drop(AE + OE).max()), max_AE=float(s[AE].max()), max_OE=float(s[OE].max()),
                n_over_01=int((s > 0.1).sum()), max_matched_set=float(s.drop([c for c in AE + OE if c not in cols]).max()))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('emb_dir'); ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    d = w.Data(); t = d.t
    sub = pd.read_parquet(os.path.join(w.W3, 'data', 'e3b_subsample.parquet'))
    ix0 = np.flatnonzero(t.parcref.isin(sub.parcref).values)
    oe, cnt, per_season = olmoearth_pre_entry(a.emb_dir, t.parcref.values[ix0])
    keep = cnt > 0
    counts = dict(subsample_in_panel=int(len(ix0)), per_season=per_season, with_pre_entry=int(keep.sum()),
                  dropped_no_pre_entry=int((~keep).sum()),
                  dropped_by_role={'agreement': int(((t.G.values[ix0] > 0) & ~keep).sum()), 'never_treated': int(((t.G.values[ix0] == 0) & ~keep).sum())},
                  seasons_per_field={int(k): int(v) for k, v in zip(*np.unique(cnt, return_counts=True))})
    print(json.dumps(counts, indent=1), flush=True)
    if a.check:
        return
    ix = ix0[keep]; oe = oe[keep]
    ts = t.iloc[ix].reset_index(drop=True).copy()
    ae, _ = pre_entry_embedding(ts.parcref.values)
    ae = np.where(np.isnan(ae), np.nanmean(ae, axis=0), ae)
    pa, po = PCA(n_components=10, random_state=0).fit(ae), PCA(n_components=10, random_state=0).fit(oe)
    for k in range(10):
        ts[AE[k]] = pa.transform(ae)[:, k]; ts[OE[k]] = po.transform(oe)[:, k]
    counts['variance_10pcs'] = dict(AE=float(pa.explained_variance_ratio_.sum()), OE=float(po.explained_variance_ratio_.sum()))

    S = {}
    for lab, cols in (('M0', []), ('MA', AE), ('MO', OE)):
        M, bal, wt = match_weighted(ts, cols)
        S[lab] = dict(M=M, bal=balance(ts, M, wt, cols), treated=int(((ts.G > 0).values & M).sum()), control=int(((ts.G == 0).values & M).sum()))
        print(lab, S[lab]['bal'], S[lab]['treated'], S[lab]['control'], flush=True)

    # H1-H3 on the subsample: build the estimator on the full panel with pmask = matched subsample fields
    full = lambda M: np.isin(np.arange(len(t)), ix[M])
    est = {}
    for lab in S:
        mask = full(S[lab]['M'])
        E1 = d.est('ndvi_july_z', pmask=mask); W = w.h1(E1)[:1] + w.h3(E1); th, V, G, _ = E1.run(W)
        E2 = d.est('ndvi_peak_z', pmask=mask); th2, V2, G2, _ = E2.run(w.h2(E2)[:1])
        r = {'H1': w.row('H1', th, V, 0, G), 'H2': w.row('H2', th2, V2, 0, G2), 'H3': w.row('H3', th, V, 1, G)}
        wcr = wc.run(d, mask, ['g'], 'within cohort E3b ' + lab)
        for h in ('H1', 'H2', 'H3'):
            r[h + ' within cohort'] = wcr[h]['after entry']; r[h + ' within cohort, before entry'] = wcr[h]['before entry']
        est[lab] = r
        print(lab, {k: round(v['est'], 3) for k, v in r.items()}, flush=True)

    # R4 harvest contrasts, as in wp3_e3b_harvest_precision.py
    from w3_z_partf import members
    from w3_h_step3 import index_matrix
    H, _ = index_matrix(t); Hs = H[ix]; Mem = members(t)
    G_, cell, crop, fam0 = d.G[ix], d.cell[ix], d.crop[ix], d.fam[ix]
    main_sh = w.shock_table(**w.MAIN_SHOCK)
    wet_sh = w.shock_table(**w.MAIN_SHOCK); wet_sh['shock'] = wet_sh['wet']
    def theta(f, sh, pm):
        sel = f != 'All agreement land'
        fam = np.where(Mem[f][ix], 'F', 'O') if sel else fam0
        TR0, CO = w.blocks(Hs, G_, cell, crop, False, list(S25), fam, pm, None, False)
        E = w.Est(w.attach_shocks(TR0, d.cells, sh), CO, d.cluster)
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        Wt = E.weights(p & TR.shock.values, p & ~TR.shock.values)
        th, V, g, _ = E.run([Wt]); return dict(est=float(th[0]), se=float(np.sqrt(V[0, 0])), clusters=int(g))
    harvest = {}
    for lab, f, sh in (('Dry or heat, all land', 'All agreement land', main_sh), ('Wet winter, all land', 'All agreement land', wet_sh),
                       ('Dry or heat, management-only', 'Management-only', main_sh)):
        harvest[lab] = {m: theta(f, sh, S[m]['M']) for m in S}
        print(lab, {m: round(v['est'], 3) for m, v in harvest[lab].items()}, flush=True)

    # readings fixed in advance
    R = {}
    R['R1'] = dict(max_smd_MO=S['MO']['bal']['max_matched_set'], passes=S['MO']['bal']['max_matched_set'] <= 0.1)
    h1a, h1o = est['MA']['H1']['est'], est['MO']['H1']['est']
    R['R2'] = dict(H1_MA=h1a, H1_MO=h1o, diff=h1o - h1a, passes=bool(abs(h1o - h1a) <= 0.03 and np.sign(h1o) == np.sign(h1a)), read=R['R1']['passes'])
    R['R3'] = dict(max_OE_in_MA=S['MA']['bal']['max_OE'], max_AE_in_MO=S['MO']['bal']['max_AE'])
    def r4(lab):
        A_, O_ = harvest[lab]['MA']['est'], harvest[lab]['MO']['est']
        ok = abs(O_ - A_) <= 0.03 and np.sign(O_) == np.sign(A_)
        near0 = (not ok) and abs(O_ - A_) <= 0.03 and abs(O_) <= 0.03 and abs(A_) <= 0.03
        return dict(MA=A_, MO=O_, diff=O_ - A_, passes=bool(ok), sign_only_near_zero=bool(near0))
    R['R4'] = {lab: r4(lab) for lab in harvest}
    R['R4']['deciding_both_pass'] = bool(R['R4']['Dry or heat, all land']['passes'] and R['R4']['Wet winter, all land']['passes'])
    R['R4']['read'] = R['R1']['passes']
    R['subsample_check'] = dict(H1_MA=h1a, full_sample_E3=H1_FULL_E3, differs_by_more_than_003=bool(abs(h1a - H1_FULL_E3) > 0.03))
    out = dict(counts=counts, samples={k: {kk: vv for kk, vv in v.items() if kk != 'M'} for k, v in S.items()},
               estimates=est, harvest=harvest, readings=R)
    json.dump(out, open(os.path.join(w.RES, 'wp3_e3b_olmoearth_matching.json'), 'w'), indent=1, default=float)
    report(out)


def report(o):
    c, S, E, Hv, R = o['counts'], o['samples'], o['estimates'], o['harvest'], o['readings']
    yn = lambda b: 'yes' if b else 'no'
    L = ['# WP3 E3b: matching on OlmoEarth pre-entry embeddings (exploratory)', '',
         'Protocol: [wp3_e3b_olmoearth_matching_protocol.md](wp3_e3b_olmoearth_matching_protocol.md). OlmoEarth-v1-Base, '
         '16 × 16 windows, patch 4 (the weaker check set by the bridge result), pre-entry = mean of farm seasons 2017/18–2019/20; '
         '10 components each of OlmoEarth and AlphaEarth, fitted on the subsample.', '',
         f"Subsample fields in the panel {c['subsample_in_panel']:,}; with a pre-entry OlmoEarth embedding {c['with_pre_entry']:,}; "
         f"dropped {c['dropped_no_pre_entry']:,} ({c['dropped_by_role']['agreement']:,} agreement, {c['dropped_by_role']['never_treated']:,} never-treated). "
         f"Variance in 10 components: OlmoEarth {c['variance_10pcs']['OE']:.2f}, AlphaEarth {c['variance_10pcs']['AE']:.2f}.", '',
         '## Balance (largest standardised difference after matching)', '',
         '| Sample | agreement / never-treated fields | covariates | AlphaEarth comps | OlmoEarth comps | above 0.1 |', '|---|---|---|---|---|---|']
    for k, v in S.items():
        b = v['bal']; L.append(f"| {k} | {v['treated']:,} / {v['control']:,} | {b['max_covariates']:.3f} | {b['max_AE']:.3f} | {b['max_OE']:.3f} | {b['n_over_01']} |")
    L += ['', '## Estimates (SE clustered by ERA5 cell)', '', '| Estimate | M0 | MA | MO |', '|---|---|---|---|']
    for k in E['M0']:
        L.append(f"| {k} | " + ' | '.join(f"{E[m][k]['est']:+.3f} ({E[m][k]['se']:.3f})" for m in ('M0', 'MA', 'MO')) + ' |')
    L += ['', '## Harvest contrasts (t/ha, W3-H index)', '', '| Contrast | M0 | MA | MO |', '|---|---|---|---|']
    for k, v in Hv.items():
        L.append(f"| {k} | " + ' | '.join(f"{v[m]['est']:+.3f} ({v[m]['se']:.3f})" for m in ('M0', 'MA', 'MO')) + ' |')
    r = R
    L += ['', '## Readings fixed in advance', '',
          f"- **R1 · balance:** largest difference in MO {r['R1']['max_smd_MO']:.3f} → {'passes' if r['R1']['passes'] else 'fails: E3b inconclusive, R2 and R4 not read'}.",
          f"- **R2 · cushion vs embedding:** H1 MO {r['R2']['H1_MO']:+.3f} vs MA {r['R2']['H1_MA']:+.3f} (difference {r['R2']['diff']:+.3f}) → {'passes' if r['R2']['passes'] else 'fails'}{'' if r['R2']['read'] else ' (not read: R1 failed)'}.",
          f"- **R3 · cross-balance (reported):** OlmoEarth components in MA {r['R3']['max_OE_in_MA']:.3f}; AlphaEarth components in MO {r['R3']['max_AE_in_MO']:.3f} (against 0.1)."]
    for k in ('Dry or heat, all land', 'Wet winter, all land', 'Dry or heat, management-only'):
        v = r['R4'][k]
        L.append(f"- **R4 · {k}{'' if 'management' not in k else ' (reported, does not decide)'}:** MO {v['MO']:+.3f} vs MA {v['MA']:+.3f} (difference {v['diff']:+.3f}) → "
                 f"{'passes' if v['passes'] else 'fails'}{' (sign only; both within ±0.03 of zero)' if v['sign_only_near_zero'] else ''}.")
    L += [f"- **R4 overall:** both deciding contrasts pass: {yn(r['R4']['deciding_both_pass'])}{'' if r['R4']['read'] else ' (not read: R1 failed)'}.",
          f"- **Subsample check:** H1 in MA {r['subsample_check']['H1_MA']:+.3f} vs full-sample E3 +0.087: differs by more than 0.03: {yn(r['subsample_check']['differs_by_more_than_003'])}.", '',
          'H1 = shock minus non-shock effect on July NDVI; H2 = recovery; H3 = land-use change minus management options. '
          'Limits as in the protocol: a pass is not evidence of a gain; the subsample is noisy; 16 × 16 is the weaker check.']
    open(os.path.join(w.RES, 'wp3_e3b_olmoearth_matching.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

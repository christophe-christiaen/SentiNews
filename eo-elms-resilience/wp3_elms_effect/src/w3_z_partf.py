"""Addendum 6 Part F: do agreements cushion cereal land in wet winters? (protocol: w3_z_addendum6_hazards_protocol.md,
Part F and the record rows of 4 November 2026). Layer 1 is the wet shock; layer 2 is GFM inundation on observable parcels.
Runs July NDVI and recovery on the cereal frame; establishment, harvest and the grassland frame are not ready.

Input   as wp3_did.py, plus matched_sample_e3.parquet, w3_z_gfm_parcel_season.parquet, w3_s_parcel_codes.parquet,
        results/w3_s_crosswalk.csv
Output  wp3_elms_effect/results/w3_z_partf.md, .json (aggregates only)
Contains modified Copernicus Emergency Management Service information 2015-2026.
"""
import json, os, sys
import numpy as np, pandas as pd
from sklearn.decomposition import PCA

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
import wp3_within_cohort as wc
import wp3_e3_embeddings as e3

S, SP = range(2017, 2027), range(2017, 2021)
BUFFER = ['SW1', 'SW3', 'SW4', 'WT2']
FAMS = ['All agreement land', 'Management-only', 'Cover crops', 'No-till', 'Buffer strips']


def members(t):
    x = pd.read_csv(os.path.join(w.RES, 'w3_s_crosswalk.csv'), keep_default_na=False)
    x = x[x.scheme.isin(['CS', 'SFI'])]
    p = pd.read_parquet(os.path.join(w.W3, 'data', 'w3_s_parcel_codes.parquet'))
    p = p[p.scheme.isin(['CS', 'SFI'])]
    sets = {'Management-only': set(x[x.family == 'management_only'].code), 'Cover crops': set(x[x.family == 'cover_crops'].code),
            'No-till': set(x[x.family == 'no_till'].code), 'Buffer strips': set(BUFFER)}
    return {k: t.parcref.isin(p[p.code.isin(v)].parcref).values for k, v in sets.items()}


def gfm(t):
    c = pd.read_parquet(os.path.join(w.W3, 'data', 'w3_z_gfm_parcel_season.parquet'),
                        columns=['parcref', 'season', 'pt_obs_days', 'pt_flood_days', 'ol_obs_days', 'ol_flood_days'])
    c = c[c.parcref.isin(t.parcref)]
    c['obs'] = c.ol_obs_days.fillna(c.pt_obs_days) > 0
    c['fl'] = c.ol_flood_days.fillna(c.pt_flood_days) > 0
    i = pd.Series(np.arange(len(t)), index=t.parcref).reindex(c.parcref).values
    years = np.arange(2016, 2027)
    O, F = np.zeros((len(t), 11), bool), np.zeros((len(t), 11), bool)
    j = c.season.values - 2016
    O[i, j], F[i, j] = c.obs.values, c.fl.values
    return O[:, :5].all(1), O[:, 1:], F[:, 1:], years     # observable; obs and flood for 2017-2026


def recovery(t):
    cols = [f'ndvi_p{k:02d}' for k in range(1, 13)]
    s = pd.read_parquet(os.path.join(w.D, 's2', 's2_parcel_year.parquet'), columns=['parcref', 'year'] + cols)
    s = s[s.parcref.isin(t.parcref)]
    i = pd.Series(np.arange(len(t)), index=t.parcref).reindex(s.parcref).values
    A = np.full((len(t), len(S), 12), np.nan)
    A[i, s.year.values - 2017] = s[cols].values.astype('float64')
    b = A[:, :4]; n = (~np.isnan(b)).sum(1)
    with np.errstate(all='ignore'):
        import warnings; warnings.simplefilter('ignore')
        mu, sd = np.nanmean(b, 1), np.nanstd(b, 1, ddof=1)
    mu[n < 2], sd[n < 2] = np.nan, np.nan
    ok = np.abs(A - mu[:, None, :]) <= sd[:, None, :]
    usable = ~np.isnan(A - mu[:, None, :]) & ~np.isnan(sd[:, None, :])
    Y = np.where(ok.any(2), ok.argmax(2) + 1.0, 13.0)
    Y[~usable.any(2)] = np.nan
    return Y


def main():
    d = w.Data(); t = d.t
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    M = ms.in_matched_sample.values
    Mem = members(t); Mem['All agreement land'] = np.ones(len(t), bool)
    obs_set, O, F, _ = gfm(t)
    sh = w.shock_table(); sh['shock'] = sh['wet']
    cl = w.smd
    fp = (t.fz3 | t.deep_peat).values
    Gp, tmax = np.where(d.G > 0, d.G - 2, 0), np.where(d.G > 0, d.G, 9999)
    res = []

    def est(Y, pm, fam, G=None, tm=None, sn=S, uni=False, crop=None):
        try:
            TR, CO = w.blocks(Y, d.G if G is None else G, d.cell, d.crop if crop is None else crop, crop is not None,
                              list(sn), fam, pm, tm, uni)
        except ValueError:
            return None
        TR = w.attach_shocks(TR, d.cells, sh)
        if crop is not None:
            TR['shock'] = TR.key.values % 1000 == 2
        return w.Est(TR, CO, d.cluster)

    def con(E, sel=None, sign=1):
        if E is None: return None
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        a, b = p & TR.shock.values, p & ~TR.shock.values
        if not a.any() or not b.any(): return None
        th, V, G, _ = E.run([E.weights(a, b)])
        return w.row('', th, V, 0, G, int(TR.nT.values[p].sum())) | dict(n_hazard=int(TR.nT.values[a].sum()))

    def wcon(E, sel, before):
        if E is None: return None
        TR = E.TR; m = (TR.fam.values == 'F') if sel else np.ones(len(TR), bool)
        win = (np.isin(TR.e.values, wc.PRE) & (TR.t.values <= 2020)) if before else TR.e.values >= 0
        v, k = wc.within(E, win & m & TR.shock.values, win & m & ~TR.shock.values, ['g'])
        if k == 0: return None
        th, V, G, _ = E.run([v])
        return w.row('', th, V, 0, G, int(TR.nT.values[v != 0].sum())) | dict(cohorts=k)

    def block(label, Y, pm, sign, crop=None, fams=FAMS):
        for f in fams:
            sel = f != 'All agreement land'
            fam = np.where(Mem[f], 'F', 'O') if sel else d.fam
            E = est(Y, pm, fam, crop=crop)
            r = dict(contrast=label, family=f, sign=sign, frozen=con(E, sel))
            r['placebo'] = con(est(Y, pm, fam, G=Gp, tm=tmax, sn=SP, crop=crop), sel)
            Eu = est(Y, pm, fam, uni=True, crop=crop)
            r['within'], r['within_before'] = wcon(Eu, sel, False), wcon(Eu, sel, True)
            r['fz3_peat'] = con(est(Y, pm & fp, fam, crop=crop), sel)
            r['neither'] = con(est(Y, pm & ~fp, fam, crop=crop), sel)
            a, p = r['frozen'], r['placebo']
            r['cushion_indicated'] = bool(a and p and sign * a['lo'] > 0 if sign > 0 else a and p and a['hi'] < 0) and bool(p and p['lo'] <= 0 <= p['hi'])
            res.append(r); w.log(label, f, a and round(a['est'], 4), a and round(a['se'], 4), 'placebo', p and round(p['est'], 4), r['cushion_indicated'])

    Yj = d.Y['ndvi_july_z']
    block('Wet shock: July NDVI, E3 matched sample', Yj, M, 1)

    # layer 2: observable parcels, re-matched on the E3 covariates
    emb, cnt = e3.pre_entry_embedding(t.parcref.values)
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
    sub, bal, _ = w.match(t.iloc[idx].reset_index(drop=True))
    w.covariates = base
    MO = np.zeros(len(t), bool); MO[idx[sub]] = True
    tr = d.G > 0
    desc = dict(cereal_parcels=len(t), matched=int(M.sum()), observable=int(obs_set.sum()), observable_matched=int(MO.sum()),
                observable_share_treated=float(obs_set[tr].mean()), observable_share_never=float(obs_set[d.G == 0].mean()),
                observable_share_fz3=float(obs_set[t.fz3.values].mean()), observable_share_not_fz3=float(obs_set[~t.fz3.values].mean()),
                observable_share_deep_peat=float(obs_set[t.deep_peat.values].mean()), observable_share_not_deep_peat=float(obs_set[~t.deep_peat.values].mean()),
                rematch_max_smd=float(bal.smd_after.max()), rematch_cov_over_0_1=int((bal.smd_after > .1).sum()),
                treated_observable_matched=int((MO & tr).sum()), never_observable_matched=int((MO & (d.G == 0)).sum()),
                inundated_parcel_seasons=int((F & MO[:, None] & O).sum()))
    w.log(desc)
    block('Wet shock: July NDVI, observable parcels', Yj, MO, 1)
    Yo = np.where(O, Yj, np.nan)
    block('Inundated vs not: July NDVI, observable parcels', Yo, MO, 1, crop=F.astype('int64'))
    Yr = np.where(O, recovery(t), np.nan)
    desc['recovery_not_reached_share_inundated'] = float((Yr[F & O & MO[:, None]] == 13).mean())
    block('Inundated vs not: recovery half-month, observable parcels', Yr, MO, -1, crop=F.astype('int64'))
    json.dump(dict(rows=res, sample=desc), open(os.path.join(w.RES, 'w3_z_partf.json'), 'w'), indent=1, default=float)

    c = lambda x: '' if not x else f"{x['est']:+.3f} ({x['lo']:+.3f}, {x['hi']:+.3f})"
    L = ['# Addendum 6 Part F: agreements in wet winters, cereal frame', '',
         'Protocol: [w3_z_addendum6_hazards_protocol.md](w3_z_addendum6_hazards_protocol.md), Part F and the record rows of 4 November 2026. '
         'Exploratory; no multiple-testing correction. Estimate (95% interval); SE clustered by ERA5 cell; strata ERA5 cell × season. '
         'Not run yet: establishment, the economic outcome and the grassland frame. Inundation contrasts are association only.', '',
         'Contains modified Copernicus Emergency Management Service information 2015–2026.', '', '## Sample', ''] + \
        [f'- {k.replace("_", " ")}: {v:,}' if isinstance(v, int) else f'- {k.replace("_", " ")}: {v:.3f}' for k, v in desc.items()] + ['']
    for lab in dict.fromkeys(r['contrast'] for r in res):
        L += [f'## {lab}', '', ('Lower recovery half-month is earlier, so a cushion is negative.' if 'recovery' in lab else 'A cushion is positive.'), '',
              '| Family | Parcel-seasons | Contrast | Placebo | Cushion indicated | Within cohort | Within cohort, before entry | Flood Zone 3 or deep peat | Neither |',
              '|---|---|---|---|---|---|---|---|---|']
        for r in res:
            if r['contrast'] == lab:
                f = r['frozen']
                L.append(f"| {r['family']} | {f['n'] if f else 0:,} | {c(f)} | {c(r['placebo'])} | {'yes' if r['cushion_indicated'] else 'no'} | {c(r['within'])} | {c(r['within_before'])} | {c(r['fz3_peat'])} | {c(r['neither'])} |")
        L.append('')
    open(os.path.join(w.RES, 'w3_z_partf.md'), 'w').write('\n'.join(L))
    w.log('done')


if __name__ == '__main__':
    main()

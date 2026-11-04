"""Addendum 6 Part F establishment: do agreements cushion February-March green cover in wet winters? (protocol:
w3_z_addendum6_hazards_protocol.md, record rows of 4 November 2026). The registered version on the E3 matched sample decides.

Input   as w3_z_partf.py, plus shared/data/s2/gee_local_estab/s2e_*.csv
Output  wp3_elms_effect/results/w3_z_partf_establishment.md, .json (aggregates only);
        wp3_elms_effect/data/w3_z_establishment.parquet (private)
Contains modified Copernicus Emergency Management Service information 2015-2026.
"""
import glob, json, os, re, sys
import numpy as np, pandas as pd
from sklearn.decomposition import PCA

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
import wp3_within_cohort as wc
import wp3_e3_embeddings as e3
from w3_z_partf import members, gfm, FAMS

S, SP = range(2018, 2027), range(2018, 2021)
N_SQUARE_YEARS = 711


def load(t):
    files = glob.glob(os.path.join(w.D, 's2', 'gee_local_estab', 's2e_*.csv'))
    assert len(files) == N_SQUARE_YEARS, f'{len(files)} of {N_SQUARE_YEARS} square-years'
    parts = []
    for f in files:
        y = int(re.search(r'_(\d{4})\.csv$', f).group(1))
        parts.append(pd.read_csv(f).assign(year=y))
    x = pd.concat(parts, ignore_index=True)
    assert not x.duplicated(['parcref', 'year']).any()
    x.to_parquet(os.path.join(w.W3, 'data', 'w3_z_establishment.parquet'), index=False)
    x = x[x.parcref.isin(t.parcref)]
    i = pd.Series(np.arange(len(t)), index=t.parcref).reindex(x.parcref).values
    out = {k: np.full((len(t), len(w.SEASONS)), np.nan) for k in ('clear', 'high', 'water')}
    for k in out:
        out[k][i, x.year.values - w.SEASONS[0]] = x[k].values
    return out


def main():
    d = w.Data(); t = d.t
    C = load(t)
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    M = ms.in_matched_sample.values
    Mem = members(t); Mem['All agreement land'] = np.ones(len(t), bool)
    obs_set, O, F, _ = gfm(t)
    sh = w.shock_table(); sh['shock'] = sh['wet']
    fp = (t.fz3 | t.deep_peat).values
    Gp, tmax = np.where(d.G > 0, d.G - 2, 0), np.where(d.G > 0, d.G, 9999)
    with np.errstate(all='ignore'):
        Y1 = np.where(C['clear'] >= 1, C['high'] / C['clear'], np.nan)
        Y3 = np.where(C['clear'] >= 3, C['high'] / C['clear'], np.nan)
        Yw = np.where(C['clear'] + C['water'] >= 1, C['high'] / (C['clear'] + C['water']), np.nan)
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

    def con(E, sel=None):
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

    def block(label, Y, pm, crop=None, decides=False):
        for f in FAMS:
            sel = f != 'All agreement land'
            fam = np.where(Mem[f], 'F', 'O') if sel else d.fam
            E = est(Y, pm, fam, crop=crop)
            r = dict(contrast=label, family=f, decides=decides, frozen=con(E, sel))
            r['placebo'] = con(est(Y, pm, fam, G=Gp, tm=tmax, sn=SP, crop=crop), sel)
            Eu = est(Y, pm, fam, uni=True, crop=crop)
            r['within'], r['within_before'] = wcon(Eu, sel, False), wcon(Eu, sel, True)
            r['fz3_peat'] = con(est(Y, pm & fp, fam, crop=crop), sel)
            r['neither'] = con(est(Y, pm & ~fp, fam, crop=crop), sel)
            a, p = r['frozen'], r['placebo']
            r['cushion_indicated'] = bool(a and p and a['lo'] > 0 and p['lo'] <= 0 <= p['hi'])
            res.append(r); w.log(label, f, a and round(a['est'], 4), a and round(a['se'], 4), 'placebo', p and round(p['est'], 4), r['cushion_indicated'])

    block('Wet shock: registered version, E3 matched sample (decides)', Y1, M, decides=True)
    block('Wet shock: at least 3 clear dates', Y3, M)
    block('Wet shock: clear plus water in the denominator', Yw, M)

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
    block('Wet shock: observable parcels', Y1, MO)
    block('Inundated vs not: observable parcels', np.where(O, Y1, np.nan), MO, crop=F.astype('int64'))

    # clear and water dates by wet winter and group, 2018-2026, E3 matched sample
    wet = sh.wet.reindex(pd.MultiIndex.from_product([d.cells, w.SEASONS])).fillna(False).values.reshape(len(d.cells), len(w.SEASONS))[d.cell]
    jj = np.arange(len(w.SEASONS))[1:]
    desc = []
    for lab, m in (('treated', M & (d.G > 0)), ('never treated', M & (d.G == 0))):
        for wv, wn in ((True, 'wet winter'), (False, 'other winter')):
            mask = np.zeros_like(wet, bool); mask[np.ix_(m, jj)] = True; mask &= wet == wv
            desc.append(dict(group=lab, winter=wn, parcel_seasons=int(mask.sum()), clear=float(np.nanmean(C['clear'][mask])), water=float(np.nanmean(C['water'][mask])),
                             no_clear_share=float(np.nanmean(C['clear'][mask] < 1)), under_3_clear_share=float(np.nanmean(C['clear'][mask] < 3))))
    json.dump(dict(rows=res, dates=desc, rematch_max_smd=float(bal.smd_after.max())), open(os.path.join(w.RES, 'w3_z_partf_establishment.json'), 'w'), indent=1, default=float)
    c = lambda x: '' if not x else f"{x['est']:+.3f} ({x['lo']:+.3f}, {x['hi']:+.3f})"
    L = ['# Addendum 6 Part F: agreements and February–March establishment in wet winters, cereal frame', '',
         'Protocol: [w3_z_addendum6_hazards_protocol.md](w3_z_addendum6_hazards_protocol.md), record rows of 4 November 2026. Exploratory; no multiple-testing correction. '
         'Share of clear dates with NDVI above 0.3 (0.01 = 1 percentage point). Estimate (95% interval); SE clustered by ERA5 cell; strata ERA5 cell × season; seasons 2018–2026; '
         'placebos on 2018–2020. The first table decides; the others are reported only. Inundation contrasts are association only.', '',
         'Contains modified Copernicus Emergency Management Service information 2015–2026.', '', '## Clear and water dates per parcel-season, E3 matched sample', '',
         '| Group | Winter | Parcel-seasons | Clear dates | Water dates | No clear date | Under 3 clear dates |', '|---|---|---|---|---|---|---|']
    for x in desc:
        L.append(f"| {x['group']} | {x['winter']} | {x['parcel_seasons']:,} | {x['clear']:.2f} | {x['water']:.3f} | {100 * x['no_clear_share']:.1f}% | {100 * x['under_3_clear_share']:.1f}% |")
    L.append('')
    for lab in dict.fromkeys(r['contrast'] for r in res):
        L += [f'## {lab}', '', '| Family | Parcel-seasons | Contrast | Placebo | Cushion indicated | Within cohort | Within cohort, before entry | Flood Zone 3 or deep peat | Neither |',
              '|---|---|---|---|---|---|---|---|---|']
        for r in res:
            if r['contrast'] == lab:
                f = r['frozen']
                L.append(f"| {r['family']} | {f['n'] if f else 0:,} | {c(f)} | {c(r['placebo'])} | {'yes' if r['cushion_indicated'] else 'no'} | {c(r['within'])} | {c(r['within_before'])} | {c(r['fz3_peat'])} | {c(r['neither'])} |")
        L.append('')
    open(os.path.join(w.RES, 'w3_z_partf_establishment.md'), 'w').write('\n'.join(L))
    w.log('done')


if __name__ == '__main__':
    main()

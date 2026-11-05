"""Addendum 6 Part F economic outcome: do agreement fields hold their harvest index better in wet winters? (protocol:
w3_z_addendum6_hazards_protocol.md, record row of 5 November 2026). The wet-shock contrast on the E3 matched sample decides.

Input   as w3_z_partf.py, plus w3_h_field_index.parquet, data/raw/cops.ods, data/raw/auk_2026/AUK-chapter7-20260709.ods
Output  wp3_elms_effect/results/w3_z_partf_harvest.md, .json (aggregates only)
Contains modified Copernicus Emergency Management Service information 2015-2026.
"""
import json, os, sys
import numpy as np, pandas as pd
from sklearn.decomposition import PCA

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'wp1_regional_signal', 'src'))
import wp3_did as w
import wp3_within_cohort as wc
import wp3_e3_embeddings as e3
from w3_z_partf import members, gfm, FAMS
from w3_h_step3 import index_matrix
from w3_h_prices import prices
from wp1_nowcast import CROPS, DEFRA, YEARS, yields

S, SP = range(2017, 2026), range(2017, 2021)
RATIO_MAX = 1.5


def r2(o, p):
    return float(1 - ((o - p) ** 2).sum() / ((o - o.mean()) ** 2).sum())


def index_checks(d, wet):
    """Error against Defra in wet and other region-seasons, after reproducing the gate's R²."""
    t = d.t; reg = t.region.map(DEFRA).values
    rows = [dict(region=r, year=y, wet=bool(wet[reg == r, j].mean() >= .5)) for j, y in enumerate(YEARS) for r in sorted(set(reg))]
    R = pd.DataFrame(rows)
    x = pd.read_parquet(os.path.join(w.W3, 'data', 'w3_h_field_index.parquet'), columns=['year', 'crop', 'region', 'index_t_ha'])
    med = x.groupby(['crop', 'region', 'year']).index_t_ha.median().rename('pred').reset_index()
    Y = yields(); Y = Y[Y.year.isin(YEARS)]
    gate = json.load(open(os.path.join(w.RES, 'w3_h_harvest.json')))['gate']
    out = {}
    for c in CROPS:
        q = Y[Y.crop == c].copy()
        g = q.groupby('region').yield_t_ha
        q['obs'] = q.yield_t_ha - (g.transform('sum') - q.yield_t_ha) / (g.transform('count') - 1)
        q = q.merge(med[med.crop == c], on=['region', 'year']).merge(R, on=['region', 'year'])
        got = r2(q.obs, q.pred)
        assert abs(got - gate[c]['r2']) < 1e-6, (c, got, gate[c]['r2'])
        e, b = (q.pred - q.obs).abs(), q.pred - q.obs
        out[c] = dict(r2=got, wet_region_seasons=int(q.wet.sum()), other_region_seasons=int((~q.wet).sum()), mae_wet=float(e[q.wet].mean()), mae_other=float(e[~q.wet].mean()),
                      ratio=float(e[q.wet].mean() / e[~q.wet].mean()), bias_wet=float(b[q.wet].mean()), bias_other=float(b[~q.wet].mean()))
    return out, R.groupby('year').wet.sum().astype(int).to_dict()


def main():
    d = w.Data(); t = d.t
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    M = ms.in_matched_sample.values
    H, C = index_matrix(t)
    Mem = members(t); Mem['All agreement land'] = np.ones(len(t), bool)
    obs_set, O, F, _ = gfm(t)
    sh = w.shock_table(); sh['dry'] = sh['shock']; sh['shock'] = sh['wet']
    fp = (t.fz3 | t.deep_peat).values
    Gp, tmax = np.where(d.G > 0, d.G - 2, 0), np.where(d.G > 0, d.G, 9999)
    res = []
    wet = sh.wet.reindex(pd.MultiIndex.from_product([d.cells, w.SEASONS])).fillna(False).values.reshape(len(d.cells), len(w.SEASONS))[d.cell].astype(bool)

    checks, wet_regions = index_checks(d, wet[:, :len(YEARS)])
    w.log('index checks', checks)

    # share of cereal-frame parcel-seasons with an index, E3 matched sample, 2017-2025
    cover = []
    for lab, m in (('treated', M & (d.G > 0)), ('never treated', M & (d.G == 0))):
        for wv, wn in ((True, 'wet winter'), (False, 'other winter')):
            mask = np.zeros_like(wet); mask[np.ix_(m, range(len(S)))] = True; mask &= wet == wv
            cover.append(dict(group=lab, winter=wn, parcel_seasons=int(mask.sum()), share_with_index=float((~np.isnan(H[mask])).mean())))
    season_wet = {y: float(wet[M, j].mean()) for j, y in enumerate(S)}

    def est(Y, pm, fam, G=None, tm=None, sn=S, uni=False, inund=None, use_crop=False, never=False):
        G0 = d.G if G is None else G
        crop = d.crop if inund is None else inund
        uc = use_crop or inund is not None
        try:
            if never:
                P = [w.blocks(Y, G0, d.cell, crop, uc, list(sn), fam, pm & ((G0 == g) | (G0 == 0)), tm, uni) for g in sorted(set(G0[(G0 > 0) & pm]) & set(sn))]
                TR, CO = pd.concat([x[0] for x in P], ignore_index=True), pd.concat([x[1] for x in P], ignore_index=True)
            else:
                TR, CO = w.blocks(Y, G0, d.cell, crop, uc, list(sn), fam, pm, tm, uni)
        except ValueError:
            return None
        TR = w.attach_shocks(TR, d.cells, sh)
        TR['dry'] = sh.dry.reindex(pd.MultiIndex.from_arrays([d.cells[TR.cell.values], TR.t.values])).fillna(False).values.astype(bool)
        if inund is not None:
            TR['shock'] = TR.key.values % 1000 == 2
        return w.Est(TR, CO, d.cluster)

    def con(E, sel=None, no_dry=False):
        if E is None: return None
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        if no_dry: p = p & ~TR.dry.values
        a, b = p & TR.shock.values, p & ~TR.shock.values
        if not a.any() or not b.any(): return None
        th, V, G, _ = E.run([E.weights(a, b), E.weights(a), E.weights(b)])
        return w.row('', th, V, 0, G, int(TR.nT.values[p].sum())) | dict(n_hazard=int(TR.nT.values[a].sum()), in_hazard=float(th[1]), in_other=float(th[2]))

    def wcon(E, sel, before):
        if E is None: return None
        TR = E.TR; m = (TR.fam.values == 'F') if sel else np.ones(len(TR), bool)
        win = (np.isin(TR.e.values, wc.PRE) & (TR.t.values <= 2020)) if before else TR.e.values >= 0
        v, k = wc.within(E, win & m & TR.shock.values, win & m & ~TR.shock.values, ['g'])
        if k == 0: return None
        th, V, G, _ = E.run([v])
        return w.row('', th, V, 0, G, int(TR.nT.values[v != 0].sum())) | dict(cohorts=k)

    def block(label, Y, pm, inund=None, decides=False):
        for f in FAMS:
            sel = f != 'All agreement land'
            fam = np.where(Mem[f], 'F', 'O') if sel else d.fam
            E = est(Y, pm, fam, inund=inund)
            r = dict(contrast=label, family=f, decides=decides, frozen=con(E, sel))
            r['placebo'] = con(est(Y, pm, fam, G=Gp, tm=tmax, sn=SP, inund=inund), sel)
            Eu = est(Y, pm, fam, uni=True, inund=inund)
            r['within'], r['within_before'] = wcon(Eu, sel, False), wcon(Eu, sel, True)
            r['fz3_peat'] = con(est(Y, pm & fp, fam, inund=inund), sel)
            r['neither'] = con(est(Y, pm & ~fp, fam, inund=inund), sel)
            if decides:
                r['never_only'] = con(est(Y, pm, fam, never=True), sel)
                r['crop_strata'] = con(est(Y, pm, fam, use_crop=True), sel)
                r['july_ndvi_same_rows'] = con(est(np.where(np.isnan(H), np.nan, d.Y['ndvi_july_z']), pm, fam), sel)
                r['wet_vs_other_no_dry_or_heat'] = con(E, sel, no_dry=True)
                for c in CROPS:
                    r[c] = con(est(C[c], pm, fam), sel)
                    r[c + ' placebo'] = con(est(C[c], pm, fam, G=Gp, tm=tmax, sn=SP), sel)
            a, p = r['frozen'], r['placebo']
            r['cushion_indicated'] = bool(a and p and a['lo'] > 0 and p['lo'] <= 0 <= p['hi'])
            res.append(r); w.log(label, f, a and (round(a['est'], 4), round(a['lo'], 4), round(a['hi'], 4), a['n']), 'placebo', p and (round(p['est'], 4), round(p['lo'], 4), round(p['hi'], 4)), r['cushion_indicated'])

    block('Wet shock: harvest index, E3 matched sample (decides)', H, M, decides=True)

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
    block('Wet shock: harvest index, observable parcels', H, MO)
    block('Inundated vs not: harvest index, observable parcels', np.where(O, H, np.nan), MO, inund=F.astype('int64'))

    p = prices()
    feed = float(np.mean(list(p['Feed wheat'].values())))
    allp = [v for s in p.values() for v in s.values()]
    money = [dict(family=r['family'], gbp_ha=r['frozen']['est'] * feed, lo=r['frozen']['lo'] * feed, hi=r['frozen']['hi'] * feed,
                  cheapest=r['frozen']['est'] * min(allp), dearest=r['frozen']['est'] * max(allp)) for r in res if r['decides'] and r['frozen']]
    json.dump(dict(rows=res, index_checks=checks, wet_region_seasons_by_year=wet_regions, share_with_index=cover, share_of_matched_fields_in_wet_cells=season_wet,
                   prices=dict(feed_wheat_mean=feed, low=min(allp), high=max(allp), rows=money), rematch_max_smd=float(bal.smd_after.max())),
              open(os.path.join(w.RES, 'w3_z_partf_harvest.json'), 'w'), indent=1, default=float)

    c = lambda x: '' if not x else f"{x['est']:+.3f} ({x['lo']:+.3f}, {x['hi']:+.3f})"
    L = ['# Addendum 6 Part F: agreements and the harvest index in wet winters, cereal frame', '',
         'Protocol: [w3_z_addendum6_hazards_protocol.md](w3_z_addendum6_hazards_protocol.md), record row of 5 November 2026. Exploratory; no multiple-testing correction. '
         'W3-H field harvest index, t/ha: an index built from Sentinel-2 and weather, not measured yield. Estimate (95% interval); SE clustered by ERA5 cell; strata ERA5 cell × season; seasons 2017–2025; '
         'placebos on 2017–2020. The first table decides; the others are reported only. An interval below zero is reported, not read as a finding. Inundation contrasts are association only.', '',
         'Contains modified Copernicus Emergency Management Service information 2015–2026.', '',
         '## Index checks, do not change the reading', '', f'Error against Defra in wet and other region-seasons (at least half the region\'s cereal-frame fields in wet-shock cells). Yardstick: W3-H\'s limit of {RATIO_MAX}. Gate R² reproduced first.', '',
         '| Crop | Wet region-seasons | MAE wet (t/ha) | MAE other (t/ha) | Ratio | Bias wet (t/ha) | Bias other (t/ha) | Within yardstick |', '|---|---:|---:|---:|---:|---:|---:|---|']
    for k, v in checks.items():
        L.append(f"| {k} | {v['wet_region_seasons']} | {v['mae_wet']:.2f} | {v['mae_other']:.2f} | {v['ratio']:.2f} | {v['bias_wet']:+.2f} | {v['bias_other']:+.2f} | {'yes' if v['ratio'] <= RATIO_MAX else 'NO'} |")
    L += ['', 'Wet region-seasons by harvest year: ' + ', '.join(f'{y}: {n}' for y, n in wet_regions.items()) + '.', '',
          'Share of E3-matched fields in wet-shock cells by harvest year: ' + ', '.join(f'{y}: {v:.0%}' for y, v in season_wet.items()) + '.', '',
          '## Share of parcel-seasons with an index, E3 matched sample', '', 'A field never sown, or out of the three crops, has no index, so that loss is not counted.', '',
          '| Group | Winter | Parcel-seasons | With an index |', '|---|---|---:|---:|']
    for x in cover:
        L.append(f"| {x['group']} | {x['winter']} | {x['parcel_seasons']:,} | {x['share_with_index']:.1%} |")
    L.append('')
    for lab in dict.fromkeys(r['contrast'] for r in res):
        L += [f'## {lab}', '', '| Family | Parcel-seasons | Contrast | Placebo | Cushion indicated | Within cohort | Within cohort, before entry | Flood Zone 3 or deep peat | Neither |',
              '|---|---:|---|---|---|---|---|---|---|']
        for r in res:
            if r['contrast'] == lab:
                f = r['frozen']
                L.append(f"| {r['family']} | {f['n'] if f else 0:,} | {c(f)} | {c(r['placebo'])} | {'yes' if r['cushion_indicated'] else 'no'} | {c(r['within'])} | {c(r['within_before'])} | {c(r['fz3_peat'])} | {c(r['neither'])} |")
        L.append('')
    dec = [r for r in res if r['decides']]
    L += ['## Reported beside the deciding table', '', '| Family | In wet winters | In other winters | Never-treated controls only | Strata with CROME crop | No dry-or-heat seasons on either side | July NDVI, same rows (SD) |', '|---|---:|---:|---|---|---|---|']
    for r in dec:
        f = r['frozen']
        L.append(f"| {r['family']} | {f['in_hazard']:+.3f} | {f['in_other']:+.3f} | {c(r['never_only'])} | {c(r['crop_strata'])} | {c(r['wet_vs_other_no_dry_or_heat'])} | {c(r['july_ndvi_same_rows'])} |")
    L += ['', '### By crop: same crop in both seasons compared', '', '| Family | ' + ' | '.join(f'{k}: contrast; placebo' for k in CROPS) + ' |', '|---|' + '---|' * len(CROPS)]
    for r in dec:
        L.append(f"| {r['family']} | " + ' | '.join(f"{c(r[k])}; {c(r[k + ' placebo'])}" for k in CROPS) + ' |')
    L += ['', '### £/ha', '', f'The t/ha contrast times Defra\'s mean UK feed wheat price for 2021–2025, £{feed:.0f}/t; across all crop prices in those seasons, £{min(allp):.0f}–£{max(allp):.0f}/t. Revenue only; costs are not counted.', '',
          '| Family | £/ha (95% interval) | At lowest and highest price |', '|---|---|---|']
    for x in money:
        L.append(f"| {x['family']} | {x['gbp_ha']:+.1f} ({x['lo']:+.1f}, {x['hi']:+.1f}) | {x['cheapest']:+.1f} to {x['dearest']:+.1f} |")
    L += ['', f"Observable parcels: maximum re-matching balance {bal.smd_after.max():.3f} SD. 2026 follows after Defra's final figures on 10 December 2026.", '']
    open(os.path.join(w.RES, 'w3_z_partf_harvest.md'), 'w').write('\n'.join(L))
    w.log('done')


if __name__ == '__main__':
    main()

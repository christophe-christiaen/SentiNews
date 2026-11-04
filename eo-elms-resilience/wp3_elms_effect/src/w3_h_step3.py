"""W3-H Step 3: do agreement fields hold their harvest index better in shock seasons? (protocol: w3_h_harvest_protocol.md,
record rows of 4 November 2026). The pooled contrast on the E3 matched sample, with its before-entry placebo, decides.

Input   as wp3_did.py, plus matched_sample_e3.parquet, w3_h_field_index.parquet, w3_s_parcel_codes.parquet,
        results/w3_s_crosswalk.csv, data/raw/cops.ods
Output  wp3_elms_effect/results/w3_h_harvest.md, .json: Step 3 section added (aggregates only)
"""
import json, os, sys
import numpy as np, pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'wp1_regional_signal', 'src'))
import wp3_did as w
import wp3_within_cohort as wc
from w3_z_partf import members
from wp1_nowcast import CROPS, DEFRA, YEARS, yields

S, SP = range(2017, 2026), range(2017, 2021)
FAMS = ['All agreement land', 'Management-only', 'Cover crops', 'No-till']


def index_matrix(t):
    x = pd.read_parquet(os.path.join(w.W3, 'data', 'w3_h_field_index.parquet'), columns=['parcref', 'year', 'crop', 'index_t_ha'])
    x = x[x.parcref.isin(t.parcref)]
    i = pd.Series(np.arange(len(t)), index=t.parcref).reindex(x.parcref).values
    H = np.full((len(t), len(w.SEASONS)), np.nan)
    H[i, x.year.values - w.SEASONS[0]] = x.index_t_ha.values
    C = {}
    for c in CROPS:
        m = (x.crop == c).values
        C[c] = np.full(H.shape, np.nan)
        C[c][i[m], x.year.values[m] - w.SEASONS[0]] = x.index_t_ha.values[m]
    return H, C


def family_codes():
    x = pd.read_csv(os.path.join(w.RES, 'w3_s_crosswalk.csv'), keep_default_na=False)
    return x[x.scheme.isin(['CS', 'SFI'])].set_index('code').family


def strict_management(t):
    """Fields whose CS and SFI codes are all management-only."""
    fam = family_codes()
    p = pd.read_parquet(os.path.join(w.W3, 'data', 'w3_s_parcel_codes.parquet'))
    p = p[p.scheme.isin(['CS', 'SFI'])]
    only = p.code.map(lambda c: fam.get(c) == 'management_only' if not isinstance(fam.get(c), pd.Series) else (fam.get(c) == 'management_only').all())
    return t.parcref.isin(only.groupby(p.parcref).all().pipe(lambda s: s[s].index)).values


def leaving_cereals(d, M):
    """Fields in cereals the season before entry: share with a non-cereal CROME season from entry to 2025, next to
    never-treated fields over the same seasons, weighted to the family's cohorts."""
    t = d.t; fam = family_codes()
    p = pd.read_parquet(os.path.join(w.W3, 'data', 'w3_s_parcel_codes.parquet'))
    p = p[p.scheme.isin(['CS', 'SFI'])]
    out = {}
    for lab, f in (('Herbal leys', 'herbal_leys'), ('Grassland options', 'grassland_options')):
        mem = t.parcref.isin(p[p.code.isin(fam[fam == f].index)].parcref).values
        rows = []
        for g in range(2021, 2026):
            cols = [f'cereal_{y}' for y in range(g, 2026)]
            base = t[f'cereal_{g - 1}'].fillna(False).astype(bool).values
            left = (t[cols].astype('float64') == 0).any(axis=1).values
            a, b = M & mem & (d.G == g) & base, M & (d.G == 0) & base
            if a.sum():
                rows.append((int(a.sum()), left[a].mean(), left[b].mean()))
        n = sum(r[0] for r in rows)
        out[lab] = dict(fields=n, family=sum(r[0] * r[1] for r in rows) / n, never_treated=sum(r[0] * r[2] for r in rows) / n)
    return out


def regional(d):
    """Defra's regional anomaly against the region's share of the cereal frame in agreements, 8 regions x 9 seasons."""
    t = d.t; reg = t.region.map(DEFRA).values
    sh = w.shock_table().shock.reindex(pd.MultiIndex.from_product([d.cells, YEARS])).fillna(False).values.reshape(len(d.cells), len(YEARS))[d.cell]
    rows = []
    for j, y in enumerate(YEARS):
        for r in sorted(set(reg)):
            m = reg == r
            rows.append(dict(region=r, year=y, share=float(((d.G[m] > 0) & (d.G[m] <= y)).mean()), shock=bool(sh[m, j].mean() >= 0.5)))
    R = pd.DataFrame(rows); Y = yields(); Y = Y[Y.year.isin(YEARS)]
    Y['anom'] = Y.yield_t_ha - Y.groupby(['crop', 'region']).yield_t_ha.transform('mean')
    res = {}
    for c in CROPS:
        z = R.merge(Y[Y.crop == c], on=['region', 'year'])
        z = z[z.year >= 2021]
        res[c] = {}
        for lab, q in (('shock', z[z.shock]), ('other', z[~z.shock])):
            res[c][lab] = dict(n=int(len(q)), spearman=float(stats.spearmanr(q.share, q.anom)[0]) if len(q) > 2 else None)
    return res, int(R[R.year >= 2021].shock.sum())


def main():
    d = w.Data(); t = d.t
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    M = ms.in_matched_sample.values
    H, C = index_matrix(t)
    Mem = members(t); Mem['All agreement land'] = np.ones(len(t), bool)
    strict = strict_management(t)
    sh = w.shock_table()
    Gp, tmax = np.where(d.G > 0, d.G - 2, 0), np.where(d.G > 0, d.G, 9999)

    def est(Y, fam, G=None, tm=None, sn=S, uni=False, use_crop=False, never=False):
        G0 = d.G if G is None else G
        try:
            if never:
                P = [w.blocks(Y, G0, d.cell, d.crop, use_crop, list(sn), fam, M & ((G0 == g) | (G0 == 0)), tm, uni)
                     for g in sorted(set(G0[(G0 > 0) & M]) & set(sn))]
                TR, CO = pd.concat([x[0] for x in P], ignore_index=True), pd.concat([x[1] for x in P], ignore_index=True)
            else:
                TR, CO = w.blocks(Y, G0, d.cell, d.crop, use_crop, list(sn), fam, M, tm, uni)
        except ValueError:
            return None
        return w.Est(w.attach_shocks(TR, d.cells, sh), CO, d.cluster)

    def con(E, sel):
        if E is None: return None
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        a, b = p & TR.shock.values, p & ~TR.shock.values
        if not a.any() or not b.any(): return None
        th, V, G, _ = E.run([E.weights(a, b), E.weights(a), E.weights(b)])
        return w.row('', th, V, 0, G, int(TR.nT.values[p].sum())) | dict(n_shock=int(TR.nT.values[a].sum()), in_shock=float(th[1]), in_other=float(th[2]))

    def wcon(E, sel, before):
        if E is None: return None
        TR = E.TR; m = (TR.fam.values == 'F') if sel else np.ones(len(TR), bool)
        win = (np.isin(TR.e.values, wc.PRE) & (TR.t.values <= 2020)) if before else TR.e.values >= 0
        v, k = wc.within(E, win & m & TR.shock.values, win & m & ~TR.shock.values, ['g'])
        if k == 0: return None
        th, V, G, _ = E.run([v])
        return w.row('', th, V, 0, G, int(TR.nT.values[v != 0].sum())) | dict(cohorts=k)

    def verdict(a, p):
        if a and p and a['lo'] > 0 and p['lo'] <= 0 <= p['hi']: return 'holds better'
        if a and a['hi'] < 0: return 'holds worse'
        return 'not shown'

    famv = lambda mask, sel: np.where(mask, 'F', 'O') if sel else d.fam
    july = np.where(np.isnan(H), np.nan, d.Y['ndvi_july_z'])
    res = []
    for f in FAMS + ['Management-only, no other option']:
        strict_row = f not in FAMS
        sel = f != 'All agreement land'
        fam = famv(strict if strict_row else Mem[f], sel)
        r = dict(family=f, decides=not strict_row)
        r['frozen'] = con(est(H, fam), sel)
        r['placebo'] = con(est(H, fam, G=Gp, tm=tmax, sn=SP), sel)
        r['verdict'] = verdict(r['frozen'], r['placebo'])
        Eu = est(H, fam, uni=True)
        r['within'], r['within_before'] = wcon(Eu, sel, False), wcon(Eu, sel, True)
        r['never_only'] = con(est(H, fam, never=True), sel)
        r['crop_strata'] = con(est(H, fam, use_crop=True), sel)
        r['july_ndvi_same_rows'] = con(est(july, fam), sel)
        for c in CROPS:
            r[c] = con(est(C[c], fam), sel)
            r[c + ' placebo'] = con(est(C[c], fam, G=Gp, tm=tmax, sn=SP), sel)
        res.append(r)
        a, p = r['frozen'], r['placebo']
        w.log(f, a and (round(a['est'], 4), round(a['lo'], 4), round(a['hi'], 4), a['n']), 'placebo', p and (round(p['est'], 4), round(p['lo'], 4), round(p['hi'], 4)), r['verdict'])
    leave = leaving_cereals(d, M)
    reg, n_shock_rs = regional(d)
    path = os.path.join(w.RES, 'w3_h_harvest.json')
    out = json.load(open(path))
    out['step3'] = dict(rows=res, leaving_cereals=leave, regional=reg, regional_shock_region_seasons=n_shock_rs,
                        farm_level='not run: the farm grouping cannot group fields into holdings')
    json.dump(out, open(path, 'w'), indent=1, default=float)

    c = lambda x: '' if not x else f"{x['est']:+.3f} ({x['lo']:+.3f}, {x['hi']:+.3f})"
    L = ['## Step 3: agreement fields against matched fields', '',
         'Harvest index anomaly in shock seasons minus other seasons, t/ha. Estimate (95% interval); SE clustered by ERA5 cell; strata ERA5 cell × season; '
         'seasons 2017–2025; E3 matched sample; frozen-plan estimator; placebo on 2017–2020. Rule fixed in advance. No multiple-testing correction. '
         'This is an index built from Sentinel-2 and weather, not measured yield.', '',
         '### Decides', '', '| Family | Parcel-seasons | In shock seasons | In other seasons | Contrast | Placebo | Reading |', '|---|---:|---:|---:|---|---|---|']
    for r in res:
        if r['decides']:
            a = r['frozen']
            L.append(f"| {r['family']} | {a['n']:,} | {a['in_shock']:+.3f} | {a['in_other']:+.3f} | {c(a)} | {c(r['placebo'])} | {r['verdict']} |")
    L += ['', '### Reported only', '', '| Family | Within cohort | Within cohort, before entry | Never-treated controls only | Strata with CROME crop | July NDVI, same rows (SD) |', '|---|---|---|---|---|---|']
    for r in res:
        L.append(f"| {r['family']} | {c(r['within'])} | {c(r['within_before'])} | {c(r['never_only'])} | {c(r['crop_strata'])} | {c(r['july_ndvi_same_rows'])} |")
    L += ['', f"Management-only, no other option: contrast {c(res[-1]['frozen'])}, placebo {c(res[-1]['placebo']) or 'not possible (no field in a cohort early enough)'}; the rule cannot be applied.", '',
          '### By crop: field in the same crop in both seasons compared', '', '| Family | ' + ' | '.join(f'{k}: contrast; placebo' for k in CROPS) + ' |', '|---|' + '---|' * len(CROPS)]
    for r in res:
        L.append(f"| {r['family']} | " + ' | '.join(f"{c(r[k])}; {c(r[k + ' placebo'])}" for k in CROPS) + ' |')
    L += ['', '### Options that take land out of cereals', '', 'Fields in cereals the season before entry, E3 matched sample: share with a non-cereal CROME season from entry to 2025. '
          'Never-treated fields cover the same seasons, weighted to the family\'s cohorts.', '', '| Family | Fields | Family | Never treated |', '|---|---:|---:|---:|']
    for k, v in leave.items():
        L.append(f"| {k} | {v['fields']:,} | {v['family']:.0%} | {v['never_treated']:.0%} |")
    L += ['', '### Regional context, no causal reading', '', 'Spearman correlation across region-seasons, 2021–2025, between Defra\'s yield anomaly and the region\'s share of the cereal frame in agreements. '
          'A region-season counts as shock if at least half its fields are in shock cells.', '', '| Crop | Shock: n, correlation | Other: n, correlation |', '|---|---|---|']
    for k, v in reg.items():
        f2 = lambda x: f"{x['n']}, {x['spearman']:+.2f}" if x['spearman'] is not None else f"{x['n']}, n/a"
        L.append(f"| {k} | {f2(v['shock'])} | {f2(v['other'])} |")
    L += ['', '### Not run or not stated', '', '- **Farm-level reading: not run.** The farm grouping links agreements to companies by nearest location, covers only fields under an option, and holds no fields for non-agreement farms, so it cannot group fields into holdings.',
          '- **£/ha: not stated yet.** Defra\'s farm-gate price series is not held locally.', '- **2026:** added after Defra\'s final figures on 10 December 2026.']
    p = os.path.join(w.RES, 'w3_h_harvest.md')
    head = open(p).read().split('\n## Step 3')[0].rstrip('\n')
    open(p, 'w').write(head + '\n\n' + '\n'.join(L) + '\n')
    w.log('done')


if __name__ == '__main__':
    main()

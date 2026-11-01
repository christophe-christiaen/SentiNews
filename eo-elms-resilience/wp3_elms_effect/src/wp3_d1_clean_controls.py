"""WP3 deviation D1 (decisions record, 1 November 2026, fixed before this was run): H1-H3 with a cleaned
never-treated comparison.

Never-treated parcels found in older scheme snapshots are dropped (primary: option snapshots by parcel reference;
strict: also parcel points inside older agreement outlines). Agreement parcels unchanged. Section 7 matching and E3
embedding matching are redone on each cleaned sample; H1-H3 with the frozen-plan estimator and the within-cohort design.
The registered results files are not touched; outputs go to wp3_d1_clean_controls.{md,json}.
"""
import json, os, sys, tempfile
from pathlib import Path
import geopandas as gpd, numpy as np, pandas as pd, pyogrio
from sklearn.decomposition import PCA

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wp3_did as w
import wp3_within_cohort as wc
import wp3_e3_embeddings as e3

DL = Path.home() / 'Downloads'
Z = lambda z, inner='': f'/vsizip/{DL / z}' + (('/' + inner) if inner else '')
OPT = [(Z('Environmental_Stewardship_Scheme_Options_-5671551631491542539.zip', 'Environmental_Stewardship_Scheme_Options_(England)___Natural_England.shp'), 'PARCREF', 'STARTDAT'),
       (Z('Environmental_Stewardship_Scheme_Options_1394686066374668060.zip', 'de361e5f-c146-4c28-a60a-a863b9563de2.gdb'), 'PARCREF', 'STARTDAT'),
       (Z('Countryside_Stewardship_Scheme_Options_629916221128040189.zip', 'Countryside_Stewardship_Scheme_Options___Natural_England.shp'), 'PARC_REF', 'STARTDAT'),
       (str(DL / 'Countryside_Stewardship_Scheme_2016_Options_England_4881680122048640024.gpkg'), 'PARCREF', 'STARTDATE')]
AGR = [Z('Environmental_Stewardship_Agreements_England_-3405005387259729334.zip', 'Environmental_Stewardship_Scheme_Agreements_(England)___Natural_England.shp'),
       Z('Environmental_Stewardship_Agreements_England_-3405005387259729334(1).zip', 'Environmental_Stewardship_Scheme_Agreements_(England)___Natural_England.shp'),
       Z('Countryside_Stewardship_Scheme_Agreements_2591408201934897153.zip', 'Countryside_Stewardship_Scheme_Agreements___Natural_England.shp')]


def snapshots(t):
    """Parcel references in any option snapshot (with earliest start), and never-treated points inside old outlines."""
    starts = []
    for src, pc, sc in OPT:
        lay = pyogrio.list_layers(src)[0][0]
        cols = [c for c in pyogrio.read_info(src, layer=lay)['fields'] if c.upper() in (pc, sc)]
        df = pyogrio.read_dataframe(src, layer=lay, columns=cols, read_geometry=False)
        df.columns = [c.upper() for c in df.columns]
        starts.append(pd.DataFrame({'parcref': df[pc].astype(str).str.replace(' ', ''), 'start': pd.to_datetime(df[sc], errors='coerce')}))
    s = pd.concat(starts).dropna(subset=['parcref']).groupby('parcref').start.min()
    nev = t[t.G == 0]
    pan = pd.read_parquet(os.path.join(w.D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y'])
    pts = nev[['parcref']].merge(pan, on='parcref')
    P = gpd.GeoDataFrame(pts, geometry=gpd.points_from_xy(pts.x, pts.y), crs=27700)
    inside = set()
    for src in AGR:
        a = pyogrio.read_dataframe(src, columns=['AGREF']).to_crs(27700)        # agreement ID only
        inside |= set(gpd.sjoin(P, a, predicate='within').parcref)
    return s, inside


def run_sample(label, t_clean, tmp):
    os.makedirs(os.path.join(tmp, 'data'), exist_ok=True)
    t_clean.to_parquet(os.path.join(tmp, 'data', 'treatment.parquet'), index=False)
    w.W3 = tmp                                              # load() reads the cleaned table; registered files untouched
    d = w.Data(); t = d.t
    emb, cnt = e3.pre_entry_embedding(t.parcref.values)
    emb = np.where(np.isnan(emb), np.nanmean(emb, axis=0), emb)
    Zp = PCA(n_components=10, random_state=0).fit_transform(emb)
    for k in range(10):
        t[f'emb_pc{k + 1}'] = Zp[:, k]
    base_cov = w.covariates
    M0, bal0, _ = w.match(t)
    def cov_e3(tt):
        X = base_cov(tt)
        for k in range(10):
            X[f'emb_pc{k + 1}'] = tt[f'emb_pc{k + 1}'].values
        return X
    w.covariates = cov_e3
    M3, bal3, _ = w.match(t)
    w.covariates = base_cov
    out = {'never_treated': int((d.G == 0).sum()), 'agreement': int((d.G > 0).sum())}
    for lab, M, bal in (('section 7 matching', M0, bal0), ('matching + embeddings (E3)', M3, bal3)):
        E1 = d.est('ndvi_july_z', pmask=M); W = w.h1(E1)[:1] + w.h3(E1); th, V, G, _ = E1.run(W)
        E2 = d.est('ndvi_peak_z', pmask=M); th2, V2, G2, _ = E2.run(w.h2(E2)[:1])
        r = {'H1': w.row('H1', th, V, 0, G), 'H2': w.row('H2', th2, V2, 0, G2), 'H3': w.row('H3', th, V, 1, G)}
        wcr = wc.run(d, M, ['g'], f'{label} {lab} within cohort')
        for h in ('H1', 'H2', 'H3'):
            r[h + ' within cohort'] = wcr[h]['after entry']; r[h + ' within cohort, before entry'] = wcr[h]['before entry']
        r['matched'] = {'treated': int(((d.G > 0) & M).sum()), 'control': int(((d.G == 0) & M).sum()), 'max_smd_after': float(bal.smd_after.max())}
        out[lab] = r
        w.log(label, lab, {k: round(v['est'], 3) for k, v in r.items() if 'est' in v})
    return out


def main():
    t = pd.read_parquet(os.path.join(w.ROOT, 'wp3_elms_effect', 'data', 'treatment.parquet'))
    s, inside = snapshots(t)
    nev = t.G == 0
    c_opt = nev & t.parcref.isin(s.index)
    c_str = c_opt | (nev & t.parcref.isin(inside))
    tr = t[t.G > 0]
    earlier = int((s.reindex(tr.parcref).values < pd.to_datetime(tr.entry_date).values).sum())
    res = {'counts': {'never_treated_registered': int(nev.sum()), 'dropped_primary': int(c_opt.sum()), 'dropped_strict': int(c_str.sum()),
                      'agreement_parcels': int(len(tr)), 'agreement_with_earlier_snapshot_start': earlier}}
    w.log(res['counts'])
    with tempfile.TemporaryDirectory() as tmp:
        res['primary'] = run_sample('primary', t[~c_opt], tmp)
        res['strict'] = run_sample('strict', t[~c_str], tmp)
    frozen = json.load(open(os.path.join(w.RES, 'wp3_e3_embeddings.json')))['estimates']
    res['registered'] = {'section 7 matching': frozen['original matching'], 'matching + embeddings (E3)': frozen['matching + embeddings (E3)']}
    json.dump(res, open(os.path.join(w.RES, 'wp3_d1_clean_controls.json'), 'w'), indent=1, default=float)
    c = res['counts']; f = lambda r: f"{r['est']:+.3f} ({r['se']:.3f})"
    L = ['# WP3 deviation D1: cleaned never-treated comparison', '',
         'Fixed in the decisions record (1 November 2026) before this was run. The registered estimates stay the registered '
         'results; these are reported beside them, corrected for never-treated parcels found under agreement in older '
         'Natural England snapshots.', '',
         f"- Never-treated parcels: {c['never_treated_registered']:,} registered; dropped {c['dropped_primary']:,} (primary, option "
         f"snapshots) or {c['dropped_strict']:,} (strict, also inside older agreement outlines).",
         f"- Agreement parcels unchanged ({c['agreement_parcels']:,}); {c['agreement_with_earlier_snapshot_start']:,} have an earlier start in "
         'an older snapshot than their recorded entry (not changed; reported).', '']
    keys = ['H1', 'H1 within cohort', 'H1 within cohort, before entry', 'H2', 'H3', 'H2 within cohort', 'H3 within cohort']
    for lab in ('section 7 matching', 'matching + embeddings (E3)'):
        L += [f'## {lab}', '', '| Estimate | registered | D1 primary | D1 strict |', '|---|---|---|---|']
        for k in keys:
            L.append(f"| {k} | {f(res['registered'][lab][k])} | {f(res['primary'][lab][k])} | {f(res['strict'][lab][k])} |")
        L += ['', f"Matched: primary {res['primary'][lab]['matched']['treated']:,} agreement and {res['primary'][lab]['matched']['control']:,} never-treated "
              f"(largest standardised difference {res['primary'][lab]['matched']['max_smd_after']:.2f}); strict {res['strict'][lab]['matched']['control']:,} never-treated.", '']
    L += ['Estimate (SE), SE clustered by ERA5 cell. H1 = shock minus non-shock effect on July NDVI; H2 = recovery; H3 = family B minus family A.']
    open(os.path.join(w.RES, 'wp3_d1_clean_controls.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

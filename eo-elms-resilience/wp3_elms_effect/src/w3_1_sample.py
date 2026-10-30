"""W3-1 samples (protocol w3_1_linear_features_protocol.md and its record of 30 October 2026).

1. Matched versus excluded fields (UKFields rule), within each group, on pre-entry July NDVI (mean 2017-2020), ITL1
   region and UKFields polygon area (only where a polygon exists). Reported before any outcome is read.
2. Samples, seed 30, on the W3-4 cereal frame, matched fields only: up to 3,000 positives per family, stratified by
   region in proportion; comparisons A (never-treated) and B (management-only, no linear option), each the same size
   per region. Negative control: management-only against A.
Reads geometry, scheme codes and pre-entry July NDVI only. Writes the per-parcel sample (private) and aggregates.
"""
import json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import option_detection as od

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
SEED, CAP = 30, 3000
FAMS = ['new_hedges', 'area_strips', 'hedge_management', 'walls_banks']

agr, never, mgmt = od.load()
m = pd.read_parquet(os.path.join(D, 'parcels', 'ukfields_england_match.parquet'))
lin = m.set_index('parcref')[FAMS].any(axis=1)
ndvi = pd.read_parquet(os.path.join(D, 's2', 's2_parcel_year.parquet'), columns=['parcref', 'year', 'ndvi_july'])
ndvi = ndvi[ndvi.year.between(2017, 2020)].groupby('parcref').ndvi_july.mean()
M = m.set_index('parcref')

groups = {f: agr[agr.parcref.isin(M.index[M[f]])] for f in FAMS}
groups['never_treated'] = never
groups['management_only'] = mgmt[~mgmt.parcref.map(lin).fillna(False)]


def sd(a, b):
    a, b = a.dropna(), b.dropna()
    s = np.sqrt((a.var() + b.var()) / 2)
    return round(float((a.mean() - b.mean()) / s), 3) if s > 0 and len(a) and len(b) else None


comparison = {}
for g, df in groups.items():
    x = df[['parcref', 'region']].assign(matched=df.parcref.map(M.matched).fillna(False).astype(bool),
                                          ndvi=df.parcref.map(ndvi), area=df.parcref.map(M.ukfields_area_ha))
    a, b = x[x.matched], x[~x.matched]
    reg = pd.concat([a.region.value_counts(normalize=True), b.region.value_counts(normalize=True)], axis=1).fillna(0)
    comparison[g] = dict(parcels=len(x), matched=len(a), excluded=len(b),
                         ndvi_july_pre_mean=[round(float(a.ndvi.mean()), 3), round(float(b.ndvi.mean()), 3)],
                         ndvi_july_pre_std_diff=sd(a.ndvi, b.ndvi),
                         area_ha_median_where_polygon=[round(float(a.area.median()), 2), round(float(b.area.median()), 2)],
                         area_std_diff_where_polygon=sd(np.log(a.area), np.log(b.area)),
                         region_share_max_abs_diff=round(float((reg.iloc[:, 0] - reg.iloc[:, 1]).abs().max()), 3))

rng = np.random.default_rng(SEED)


def draw(df, n):
    return df.sample(n=min(n, len(df)), random_state=int(rng.integers(1 << 31)))


def stratified(pos, cap):
    if len(pos) <= cap:
        return pos
    k = (pos.region.value_counts(normalize=True) * cap).round().astype(int)
    return pd.concat([draw(pos[pos.region == r], n) for r, n in k.items()])


def matched_only(df):
    return df[df.parcref.map(M.matched).fillna(False).astype(bool)]


parts, counts = [], {}
A_pool, B_pool = matched_only(groups['never_treated']), matched_only(groups['management_only'])
for fam in FAMS + ['management_only']:
    pos = stratified(matched_only(groups[fam]), CAP)
    parts.append(pos.assign(family=fam, role='positive'))
    counts[fam] = {'positive': len(pos)}
    for role, pool in (('A', A_pool), ('B', B_pool)):
        if fam == 'management_only' and role == 'B':
            continue
        pool = pool[~pool.parcref.isin(pos.parcref)]
        got, short = [], 0
        for r, n in pos.region.value_counts().items():
            c = pool[pool.region == r]
            got.append(draw(c, n)); short += max(0, n - len(c))
        comp = pd.concat(got)
        parts.append(comp.assign(family=fam, role=role))
        counts[fam][role] = len(comp); counts[fam][f'{role}_shortfall'] = short

S = pd.concat(parts)[['parcref', 'region', 'family', 'role']]
S['ukfields_id'] = S.parcref.map(M.ukfields_id)
S.to_parquet(os.path.join(D, 'parcels', 'w3_1_sample.parquet'), index=False)
res = dict(seed=SEED, cap=CAP, frame='W3-4 cereal frame (od.load), UKFields-matched only',
           matched_vs_excluded=comparison, sample_counts=counts, unique_parcels=int(S.parcref.nunique()),
           unique_polygons=int(S.ukfields_id.nunique()))
json.dump(res, open(os.path.join(ROOT, 'wp3_elms_effect', 'results', 'w3_1_sample.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))

"""WP3 E3b subsample (protocol: wp3_e3b_olmoearth_matching_protocol.md, Sample), drawn once with seed 30 before any
embedding is computed. No outcome is read.

- 20,000 agreement fields from the E3 matched sample, stratified by ITL1 region x cohort (G), proportional allocation
  (largest remainder);
- all never-treated fields in the ERA5 cells of those agreement fields, capped at 40,000: if more, allocated to cells in
  proportion to their never-treated count (largest remainder) and drawn at random within each cell.

Output: wp3_elms_effect/data/e3b_subsample.parquet (private), results/wp3_e3b_subsample.json (counts only) and
docs/colab/e3b_parcels.csv (parcref, lat, lon, role) for the Colab extraction.
"""
import json, os
import numpy as np, pandas as pd, geopandas as gpd
import wp3_did as w

SEED, N_AGR, CAP = 30, 20000, 40000


def alloc(sizes, total):
    q = sizes / sizes.sum() * total; n = np.floor(q).astype(int)
    n.iloc[np.argsort(-(q - n).values)[:total - n.sum()]] += 1
    return n


def main():
    rng = np.random.default_rng(SEED)
    t = pd.read_parquet(os.path.join(w.W3, 'data', 'treatment.parquet'))
    t = t.merge(pd.read_parquet(os.path.join(w.D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y']), on='parcref', how='left')
    t = t.merge(pd.read_parquet(os.path.join(w.D, 'weather', 'parcel_era5_cell.parquet'))[['parcref', 'cell_id_data']], on='parcref', how='left')
    t = t[t.cell_id_data.notna()].reset_index(drop=True)
    w.region(t)
    m = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet')).set_index('parcref').in_matched_sample
    t['m_e3'] = m.reindex(t.parcref).fillna(False).values
    agr = t[(t.G > 0) & t.m_e3]
    size = agr.groupby(['region', 'G']).size(); n = alloc(size, N_AGR)
    pick = [g.sample(int(n[k]), random_state=int(rng.integers(1 << 31))) for k, g in agr.groupby(['region', 'G']) if n[k] > 0]
    A = pd.concat(pick)
    nt = t[(t.G == 0) & t.cell_id_data.isin(A.cell_id_data.unique())]
    if len(nt) > CAP:
        cs = nt.groupby('cell_id_data').size(); nc = alloc(cs, CAP)
        nt = pd.concat([g.sample(int(nc[c]), random_state=int(rng.integers(1 << 31))) for c, g in nt.groupby('cell_id_data') if nc[c] > 0])
    S = pd.concat([A.assign(role='agreement'), nt.assign(role='never_treated')])[['parcref', 'role', 'G', 'region', 'cell_id_data', 'x', 'y']]
    S.to_parquet(os.path.join(w.W3, 'data', 'e3b_subsample.parquet'), index=False)
    ll = gpd.GeoSeries(gpd.points_from_xy(S.x, S.y), crs=27700).to_crs(4326)
    pd.DataFrame({'parcref': S.parcref.values, 'lat': ll.y.values, 'lon': ll.x.values}).to_csv(
        os.path.join(w.ROOT, 'docs', 'colab', 'e3b_parcels.csv'), index=False)
    out = dict(seed=SEED, agreement=int(len(A)), never_treated=int(len(nt)), never_treated_available=int(((t.G == 0) & t.cell_id_data.isin(A.cell_id_data.unique())).sum()),
               era5_cells=int(A.cell_id_data.nunique()), agreement_by_region=A.region.value_counts().to_dict(),
               agreement_by_cohort={int(k): int(v) for k, v in A.G.value_counts().sort_index().items()})
    json.dump(out, open(os.path.join(w.RES, 'wp3_e3b_subsample.json'), 'w'), indent=1); print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()

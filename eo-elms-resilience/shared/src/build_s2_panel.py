"""Sentinel-2 parcel x year panel with the outcomes defined in wp3_elms_effect/results/preregistration.md, plus
weather-shock exposure per parcel-season. Quality summary only: this script never splits outcomes by scheme group.

Input   shared/data/s2/gee_local/s2_<square>_<year>.csv            direct Earth Engine extraction
        ~/Downloads/eo_elms_s2_parcels*/s2_<square>_<year>.csv     Drive exports, if downloaded (optional)
        shared/data/weather/era5land_monthly.parquet, era5land_heatdays.parquet, parcel_era5_cell.parquet
Output  shared/data/s2/s2_parcel_year.parquet     parcref, year, half-monthly values, outcome metrics, anomalies
        shared/data/weather/cell_year_shocks.parquet
        shared/results/s2_panel_quality.md        coverage and data-quality counts only

Outcomes (half-month k: 1 = 1-15 March ... 12 = 16-31 August)
  Shocks: see preregistration section 5 (dry = spring rain <= -20% or Jun-Jul soil moisture <= -1 SD)
  ndvi_july   mean of NDVI p09, p10           ndmi_july, ndre_july likewise
  ndvi_peak   max NDVI over p04-p09           peak_k = half-month of the peak
  integral    sum of NDVI p03-p10 (needs >= 6 of the 8 half-months, scaled to 8)
  senesc_k    first half-month after the peak with NDVI < 50% of the peak
Anomalies: z-scores against the parcel's own 2017-2020 values (needs >= 2 baseline seasons).
"""
import glob, os, re
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 's2_panel_quality.md')
K = range(1, 13)
BASE = (2017, 2020)


def files():
    local = glob.glob(os.path.join(D, 's2', 'gee_local', 's2_*.csv'))
    drive = glob.glob(os.path.expanduser('~/Downloads/eo_elms_s2_parcels*/**/s2_*.csv'), recursive=True)
    got = {}
    for f in drive + local:                       # local wins if both exist
        m = re.search(r's2_(\d+_\d+)_(\d{4})\.csv$', f)
        if m:
            got[(m.group(1), int(m.group(2)))] = f
    return got


def load(got):
    parts = []
    for (sq, y), f in sorted(got.items()):
        d = pd.read_csv(f)
        d['year'] = y; d['square'] = sq
        parts.append(d)
    p = pd.concat(parts, ignore_index=True)
    for c in p.columns:
        if c[:4] in ('ndvi', 'ndre', 'ndmi') or c.startswith('n_p'):
            p[c] = pd.to_numeric(p[c], errors='coerce').astype('float32')
    return p.drop_duplicates(['parcref', 'year'])


def metrics(p):
    nd = lambda k: p[f'ndvi_p{k:02d}']
    p['ndvi_july'] = p[['ndvi_p09', 'ndvi_p10']].mean(axis=1)
    p['ndmi_july'] = p[['ndmi_p09', 'ndmi_p10']].mean(axis=1)
    p['ndre_july'] = p[['ndre_p09', 'ndre_p10']].mean(axis=1)
    win = p[[f'ndvi_p{k:02d}' for k in range(4, 10)]]
    p['ndvi_peak'] = win.max(axis=1)
    p['peak_k'] = (win.fillna(-9).values.argmax(axis=1) + 4).astype('int8')
    p.loc[p.ndvi_peak.isna(), 'peak_k'] = -1
    integ = p[[f'ndvi_p{k:02d}' for k in range(3, 11)]]
    cnt = integ.notna().sum(axis=1)
    p['integral'] = (integ.sum(axis=1) * 8 / cnt).where(cnt >= 6)
    arr = p[[f'ndvi_p{k:02d}' for k in K]].values
    sen = np.full(len(p), -1, dtype='int8')
    for i, (pk, mx) in enumerate(zip(p.peak_k.values, p.ndvi_peak.values)):
        if pk > 0:
            after = np.where(arr[i, pk:] < 0.5 * mx)[0]
            if len(after):
                sen[i] = pk + 1 + after[0]
    p['senesc_k'] = sen
    p['clear_looks'] = p[[f'n_p{k:02d}' for k in K]].sum(axis=1)
    return p


def anomalies(p):
    b = p[p.year.between(*BASE)]
    for v in ('ndvi_july', 'ndvi_peak', 'ndmi_july', 'ndre_july', 'integral'):
        g = b.groupby('parcref')[v].agg(['mean', 'std', 'count'])
        g = g[g['count'] >= 2]
        m = p.parcref.map(g['mean']); s = p.parcref.map(g['std'].clip(lower=0.02))   # floor avoids division blow-ups
        p[f'{v}_z'] = ((p[v] - m) / s).astype('float32')
    return p


def shocks():
    W = os.path.join(D, 'weather')
    m = pd.read_parquet(os.path.join(W, 'era5land_monthly.parquet'))
    h = pd.read_parquet(os.path.join(W, 'era5land_heatdays.parquet'))
    spring = m[m.month.between(3, 7)].groupby(['cell_id', 'year']).precip_mm.sum().rename('spring_mm')
    w = m.copy(); w['season'] = np.where(w.month >= 10, w.year + 1, w.year)       # Oct-Mar belongs to the next season
    winter = w[(w.month >= 10) | (w.month <= 3)].groupby(['cell_id', 'season']).precip_mm.sum().rename('winter_mm')
    winter.index = winter.index.set_names(['cell_id', 'year'])
    s = pd.concat([spring, winter], axis=1).reset_index()
    for col in ('spring_mm', 'winter_mm'):
        normal = s[s.year.between(1991, 2020)].groupby('cell_id')[col].mean()
        s[col.replace('_mm', '_anom_pct')] = (s[col] / s.cell_id.map(normal) - 1) * 100
    s = s.merge(h[['cell_id', 'year', 'hot_days_28']], on=['cell_id', 'year'], how='left')
    sm = m[m.month.isin([6, 7])].groupby(['cell_id', 'year']).swvl2.mean().rename('jj_swvl2').reset_index()
    clim = sm[sm.year.between(1991, 2020)].groupby('cell_id').jj_swvl2.agg(['mean', 'std'])
    sm['soil_moist_z'] = (sm.jj_swvl2 - sm.cell_id.map(clim['mean'])) / sm.cell_id.map(clim['std'])
    s = s.merge(sm[['cell_id', 'year', 'soil_moist_z']], on=['cell_id', 'year'], how='left')
    s['dry_shock'] = (s.spring_anom_pct <= -20) | (s.soil_moist_z <= -1)          # pre-registration, section 5
    s['severe_dry_shock'] = (s.spring_anom_pct <= -30) | (s.soil_moist_z <= -1.5)
    s['heat_shock'] = s.hot_days_28 >= 5
    s['wet_shock'] = s.winter_anom_pct >= 30
    s.to_parquet(os.path.join(W, 'cell_year_shocks.parquet'), index=False)
    return s


def main():
    got = files()
    p = anomalies(metrics(load(got)))
    s = shocks()
    cell = pd.read_parquet(os.path.join(D, 'weather', 'parcel_era5_cell.parquet'))[['parcref', 'cell_id_data']]
    p = p.merge(cell, on='parcref', how='left').merge(
        s[['cell_id', 'year', 'spring_anom_pct', 'soil_moist_z', 'hot_days_28', 'winter_anom_pct', 'dry_shock', 'severe_dry_shock', 'heat_shock', 'wet_shock']]
        .rename(columns={'cell_id': 'cell_id_data'}), on=['cell_id_data', 'year'], how='left')
    p.to_parquet(os.path.join(D, 's2', 's2_parcel_year.parquet'), index=False)

    q = p.groupby('year').agg(parcels=('parcref', 'size'), squares=('square', 'nunique'), clear_looks=('clear_looks', 'median'),
                              july_ok=('ndvi_july', lambda x: x.notna().mean()), peak_ok=('ndvi_peak', lambda x: x.notna().mean()),
                              july_ndvi=('ndvi_july', 'median'), dry=('dry_shock', 'mean'), heat=('heat_shock', 'mean'))
    q[['july_ok', 'peak_ok', 'dry', 'heat']] = (q[['july_ok', 'peak_ok', 'dry', 'heat']] * 100).round(0)
    lines = ['# Sentinel-2 parcel panel: data quality (no scheme-group comparisons)', '',
             f'- Square-year files: {len(got)} (of 790); parcel-seasons: {len(p):,}; parcels: {p.parcref.nunique():,}',
             f'- Parcels with a usable 2017–2020 baseline (>= 2 seasons) for July NDVI: {p.dropna(subset=["ndvi_july_z"]).parcref.nunique():,}', '',
             '| Year | parcels | squares | median clear looks | % with July value | % with peak value | median July NDVI | % parcels in dry shock | % in heat shock |',
             '|---|---|---|---|---|---|---|---|---|'] + \
            [f'| {y} | {int(r.parcels):,} | {int(r.squares)} | {r.clear_looks:.0f} | {r.july_ok:.0f} | {r.peak_ok:.0f} | {r.july_ndvi:.2f} | {r.dry:.0f} | {r.heat:.0f} |'
             for y, r in q.iterrows()] + \
            ['', 'Shocks are ERA5-Land, defined as in the pre-registration: dry = March–July rainfall >= 20% below the 1991–2020 normal or June–July soil moisture <= -1 SD; '
             'heat = >= 5 days >= 28 °C in June–August.']
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()

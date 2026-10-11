"""Sentinel-1 parcel x season panel from gee_s1_interactive.py output. Quality summary only (no scheme-group comparisons).

Season Y = October Y-1 to August Y; half-month k: 1-2 October, 3-4 November, 5-6 December, 7-8 January, 9-10 February,
11-12 March, 13-14 April, 15-16 May, 17-18 June, 19-20 July, 21-22 August. Backscatter in dB.

Measures per parcel-season
  winter_vv, winter_vh   mean of December-February (k 5-10): soil wetness (wetter soil = brighter)
  winter_cover           winter VH - VV (dB): higher = more vegetation cover (cover crop, autumn-sown crop), lower = bare
  spring_growth          May-June VH - VV (k 15-18): crop biomass, usable when Sentinel-2 is cloud-blocked
  winter_vv_anom         winter_vv minus the parcel's mean over all seasons; winter_vv_z the same in parcel SD units
  winter_passes          radar passes in December-February (orbit mix changes over time; keep for checks)
Joined: ERA5-Land winter rainfall anomaly and wet shock (October-March >= 30% above normal) for the parcel's cell.

Input   shared/data/s1/gee_local/s1_<square>_<season>.csv; shared/data/weather/{cell_year_shocks,parcel_era5_cell}.parquet
Output  shared/data/s1/s1_parcel_season.parquet; shared/results/s1_panel_quality.md
"""
import glob, os, re
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
SRC = os.environ.get('S1_LOCAL_DIR', os.path.join(D, 's1', 'gee_local'))
SUMMARY = os.environ.get('S1_SUMMARY', os.path.join(ROOT, 'shared', 'results', 's1_panel_quality.md'))
OUT = os.environ.get('S1_PANEL', os.path.join(D, 's1', 's1_parcel_season.parquet'))
WINTER, SPRING = range(5, 11), range(15, 19)


def load():
    parts = []
    for f in sorted(glob.glob(os.path.join(SRC, 's1_*.csv'))):
        m = re.search(r's1_(\d+_\d+)_(\d{4})\.csv$', f)
        if not m:
            continue
        d = pd.read_csv(f); d['square'], d['season'] = m.group(1), int(m.group(2))
        parts.append(d)
    p = pd.concat(parts, ignore_index=True).drop_duplicates(['parcref', 'season'])
    num = [c for c in p.columns if re.match(r'(vv|vh|n)_p\d\d$', c)]
    p[num] = p[num].apply(pd.to_numeric, errors='coerce').astype('float32')
    return p, len(parts)


def measures(p):
    col = lambda v, ks: [f'{v}_p{k:02d}' for k in ks]
    p['winter_vv'] = p[col('vv', WINTER)].mean(axis=1)
    p['winter_vh'] = p[col('vh', WINTER)].mean(axis=1)
    p['winter_cover'] = p.winter_vh - p.winter_vv
    p['spring_growth'] = p[col('vh', SPRING)].mean(axis=1) - p[col('vv', SPRING)].mean(axis=1)
    p['winter_passes'] = p[col('n', WINTER)].sum(axis=1)
    g = p.groupby('parcref').winter_vv
    p['winter_vv_anom'] = (p.winter_vv - g.transform('mean')).astype('float32')
    p['winter_vv_z'] = (p.winter_vv_anom / g.transform('std').clip(lower=0.2)).astype('float32')
    return p


def main():
    p, nfiles = load()
    p = measures(p)
    W = os.path.join(D, 'weather')
    cell = pd.read_parquet(os.path.join(W, 'parcel_era5_cell.parquet'))[['parcref', 'cell_id_data']]
    s = pd.read_parquet(os.path.join(W, 'cell_year_shocks.parquet'))[['cell_id', 'year', 'winter_anom_pct', 'wet_shock']]
    p = p.merge(cell, on='parcref', how='left').merge(s.rename(columns={'cell_id': 'cell_id_data', 'year': 'season'}),
                                                      on=['cell_id_data', 'season'], how='left')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    p.to_parquet(OUT, index=False)
    q = p.groupby('season').agg(parcels=('parcref', 'size'), squares=('square', 'nunique'), passes=('winter_passes', 'median'),
                                winter_vv=('winter_vv', 'median'), anom=('winter_vv_anom', 'median'), cover=('winter_cover', 'median'),
                                wet=('wet_shock', 'mean'), rain=('winter_anom_pct', 'median'))
    # validation: does radar winter brightening follow measured winter rainfall? (cell-season means)
    cs = p.groupby(['cell_id_data', 'season']).agg(anom=('winter_vv_anom', 'mean'), rain=('winter_anom_pct', 'first')).dropna()
    cs['anom_w'] = cs.anom - cs.groupby(level='cell_id_data').anom.transform('mean')   # within-cell, across seasons
    cs['rain_w'] = cs.rain - cs.groupby(level='cell_id_data').rain.transform('mean')
    r = cs.anom_w.corr(cs.rain_w) if len(cs) > 10 else np.nan
    lines = ['# Sentinel-1 parcel panel: data quality (no scheme-group comparisons)', '',
             f'- Square-season files: {nfiles} (of 790); parcel-seasons: {len(p):,}; parcels: {p.parcref.nunique():,}',
             f'- Check: within each weather cell, seasons with wetter winters have brighter radar? correlation of winter VV '
             f'anomaly with October–March rainfall anomaly: {r:.2f} (cell-seasons: {len(cs):,})', '',
             '| Season | parcels | squares | median winter passes | median winter VV (dB) | median VV anomaly (dB) | median winter VH−VV (dB) | % parcels in wet shock | median winter rain vs normal (%) |',
             '|---|---|---|---|---|---|---|---|---|'] + \
            [f'| {y} | {int(x.parcels):,} | {int(x.squares)} | {x.passes:.0f} | {x.winter_vv:.2f} | {x.anom:+.2f} | {x.cover:.2f} | '
             f'{100 * x.wet:.0f} | {x.rain:+.0f} |' for y, x in q.iterrows()] + \
            ['', 'Winter = December–February. Wet shock (pre-registration): October–March rainfall >= 30% above the 1991–2020 normal. '
             'The orbit mix changes over time (Sentinel-1B lost in December 2021): compare passes per season before reading trends.']
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()

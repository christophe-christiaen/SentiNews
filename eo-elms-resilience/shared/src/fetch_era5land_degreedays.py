"""Degree-days above 30 C for WP1 addendum E (wp1_regional_signal/results/protocol.md, addendum E and its record of
30 October 2026, written before this ran): ERA5-Land DAILY_AGGR temperature_2m_max at each weather cell centre used by
the cereal parcels (cell_id_data), summed over max(0, Tmax - 30 C) for 1 June-15 July (dd30_jul15) and 1 June-31 August
(dd30_aug31), seasons 2017-2026. Same sampling as fetch_era5land.py.

Output  shared/data/weather/era5land_degreedays.parquet   cell_id, year, dd30_jul15, dd30_aug31
Usage   python fetch_era5land_degreedays.py --project ee-natusjatkachenko03
"""
import argparse, os
import pandas as pd, ee
from fetch_era5land import OUT, sample, with_retry
from gee_s1_interactive import init_ee

YEARS = range(2017, 2027)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--project', required=True); a = ap.parse_args()
    init_ee(a.project)
    ids = sorted(pd.read_parquet(os.path.join(OUT, 'parcel_era5_cell.parquet')).cell_id_data.unique())
    fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([int(c.split('_')[0]) * 0.1, int(c.split('_')[1]) * 0.1]), {'cell_id': c}) for c in ids])
    dd = lambda col: col.map(lambda i: i.subtract(303.15).max(0)).sum()
    out = []
    for y in YEARS:
        daily = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR').select('temperature_2m_max')
        img = ee.Image.cat(dd(daily.filterDate(f'{y}-06-01', f'{y}-07-16')).rename('dd30_jul15'),
                           dd(daily.filterDate(f'{y}-06-01', f'{y}-09-01')).rename('dd30_aug31'))
        n = daily.filterDate(f'{y}-06-01', f'{y}-09-01').size().getInfo()
        d = with_retry(lambda: sample(img, fc)).assign(year=y)
        print(y, len(d), 'cells;', n, 'days; mean dd30 (Jun-Aug)', round(d.dd30_aug31.mean(), 2), flush=True)
        out.append(d)
    pd.concat(out, ignore_index=True)[['cell_id', 'year', 'dd30_jul15', 'dd30_aug31']].to_parquet(os.path.join(OUT, 'era5land_degreedays.parquet'), index=False)


if __name__ == '__main__':
    main()

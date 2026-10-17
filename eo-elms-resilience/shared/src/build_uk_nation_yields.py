"""U3: yields outside England for WP1 (Scotland, Northern Ireland), as one tidy table.

Scotland: regional yields by crop from the Scottish Government's "Regional estimates for Cereal and oilseed rape
harvest: final estimates 1991-2025" (Tables 2, 5, 8). Three geographies: four regions 1991-2017, ITL2 2018-2024, new ITL2 from 2025 (breaks in
the series, not backdated). West Central Scotland is dropped: about 1% of Scottish cereals, and its 2018-2019 values
equal the national ones. 2020 and 2022 yields use a different method (publisher's Note 3); flagged.
Northern Ireland: national yields from the Defra cereal and oilseed dataset (DAERA post-harvest survey).
Wales is not included: its yields in the Defra dataset are England's (dataset metadata).

Input   data/raw/scotland_harvest/regional_1991_2025.xlsx; data/raw/cops.ods
Output  shared/data/yields/uk_nation_yields.csv (crop, nation, region, year, yield_t_ha, geography, method_flag)
"""
import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CROPS = {'wheat': 'wheat', 'winter barley': 'winter barley', 'spring barley': 'spring barley', 'oats': 'oats'}


def scotland():
    f = os.path.join(ROOT, 'data', 'raw', 'scotland_harvest', 'regional_1991_2025.xlsx')
    out = []
    for sheet, geo in (('Table 2', 'four regions NE, NW, SE, SW (1991-2017)'), ('Table 5', 'ITL2 (2018-2024)'), ('Table 8', 'new ITL2 (2025 on)')):
        raw = pd.read_excel(f, sheet_name=sheet, header=None)
        h = raw.index[raw[0].astype(str).str.strip() == 'Crop'][0]
        t = raw.iloc[h + 1:].copy(); t.columns = [str(c).strip().split('.')[0] for c in raw.iloc[h]]
        years = [c for c in t.columns if c.isdigit()]
        t = t.melt(id_vars=['Crop', 'Region'], value_vars=years, var_name='year', value_name='yield_t_ha')
        t['crop'] = t.Crop.astype(str).str.strip().str.lower().map(CROPS)
        t['yield_t_ha'] = pd.to_numeric(t.yield_t_ha, errors='coerce')
        t = t.dropna(subset=['crop', 'yield_t_ha'])
        t['region'] = t.Region.astype(str).str.strip()
        t['geography'] = geo
        out.append(t[['crop', 'region', 'year', 'yield_t_ha', 'geography']])
    s = pd.concat(out, ignore_index=True)
    s['year'] = s.year.astype(int)
    s = s[~s.region.str.contains('West Central', case=False)].drop_duplicates(['crop', 'region', 'year'])
    s['nation'] = 'Scotland'
    s['method_flag'] = s.year.isin([2020, 2022]).map({True: 'different yield method (publisher Note 3)', False: ''})
    return s


def northern_ireland():
    f = os.path.join(ROOT, 'data', 'raw', 'cops.ods')
    out = []
    for sheet, crop in (('Regional_wheat', 'wheat'), ('Regional_winter_barley', 'winter barley'),
                        ('Regional_spring_barley', 'spring barley'), ('Regional_oats', 'oats')):
        v = pd.read_excel(f, engine='odf', sheet_name=sheet, header=None)
        yrow = v.index[v[0].astype(str).str.contains('Yield', case=False)][0]
        years = {j: int(x) for j, x in v.iloc[2].items() if isinstance(x, (int, float)) and pd.notna(x) and 1990 < x < 2100}
        r = v.index[(v[0].astype(str).str.strip() == 'Northern Ireland') & (v.index > yrow)][0]
        for j, y in years.items():
            val = pd.to_numeric(v.iloc[r, j], errors='coerce')
            if pd.notna(val):
                out.append(dict(crop=crop, region='Northern Ireland', year=y, yield_t_ha=float(val), geography='national'))
    n = pd.DataFrame(out); n['nation'] = 'Northern Ireland'; n['method_flag'] = ''
    return n


def main():
    d = pd.concat([scotland(), northern_ireland()], ignore_index=True).sort_values(['nation', 'crop', 'region', 'year'])
    os.makedirs(os.path.join(ROOT, 'shared', 'data', 'yields'), exist_ok=True)
    d.to_csv(os.path.join(ROOT, 'shared', 'data', 'yields', 'uk_nation_yields.csv'), index=False)
    print(d.groupby(['nation', 'crop']).agg(regions=('region', 'nunique'), first=('year', 'min'), last=('year', 'max'), n=('yield_t_ha', 'size')))


if __name__ == '__main__':
    main()

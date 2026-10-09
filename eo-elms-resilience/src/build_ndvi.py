"""Turn raw MODIS subsets into site-year NDVI metrics.
Inputs : data/raw/modis/*.json  (MOD13Q1 250 m 16-day NDVI, MCD12Q1 500 m land cover 2019)
Output : data/processed/ndvi_site_year.csv

Land-cover mask (MCD12Q1 LC_Type1, IGBP): 12 croplands, 14 cropland/natural mosaic -> 'crop';
10 grasslands -> 'grass'. Each 250 m NDVI pixel takes the class of the 500 m cell it falls in.

Metrics per site-year and cover type (median across masked pixels of a per-pixel statistic):
  peak      mean of the 3 highest composites, DOY 113-193 (late Apr - mid Jul)   [PRIMARY]
  early     same statistic but DOY 113-177 only (information available by ~1 July)
  july      max composite DOY 177-209 (early senescence => drought / low yield)
Cloud contamination only lowers NDVI in max-value composites, so top-k statistics are robust."""
import glob, json, os, re, numpy as np, pandas as pd
ROOT = os.path.join(os.path.dirname(__file__), '..')
RAW = os.path.join(ROOT, 'data/raw/modis')
def load(fn):
    j = json.load(open(fn)); n, m = int(j['nrows']), int(j['ncols'])
    return n, m, [(int(s['modis_date'][5:]), np.array(s['data'], float).reshape(n, m)) for s in j['subset']]
rows = []
for lc_fn in glob.glob(f'{RAW}/MCD12Q1_LC_Type1_*.json'):
    key = re.match(r'.*MCD12Q1_LC_Type1_(.+)_(\d+)_2019_1\.json', lc_fn)
    reg_tag, site = key.group(1), int(key.group(2))
    ln, lm, lcs = load(lc_fn); lc = lcs[0][1]
    for fn in sorted(glob.glob(f'{RAW}/MOD13Q1_250m_16_days_NDVI_{reg_tag}_{site}_*_81.json')):
        year = int(fn.split('_')[-2])
        n, m, comps = load(fn)
        if not comps: continue
        ri = (np.arange(n) * ln // n); ci = (np.arange(m) * lm // m)
        lcg = lc[np.ix_(ri, ci)]
        doy = np.array([d for d, _ in comps]); cube = np.stack([a for _, a in comps]) * 1e-4
        cube[cube < -0.2] = np.nan
        def stat(lo, hi, k):
            sel = cube[(doy >= lo) & (doy <= hi)]
            if len(sel) < k: return np.full((n, m), np.nan)
            s = np.sort(np.nan_to_num(sel, nan=-1), axis=0)[-k:]
            s[s < -0.5] = np.nan
            return np.nanmean(s, axis=0)
        mets = dict(peak=stat(113, 193, 3), early=stat(113, 177, 3), july=stat(177, 209, 1))
        for cover, cls in dict(crop=(12, 14), grass=(10,)).items():
            mask = np.isin(lcg, cls)
            if mask.sum() < 20: continue
            r = dict(region_tag=reg_tag, site=site, year=year, cover=cover, npix=int(mask.sum()))
            for k, v in mets.items():
                vv = v[mask]; r[k] = float(np.nanmedian(vv)) if np.isfinite(vv).any() else np.nan
                # spatial heterogeneity (spectral-variation proxy) of peak NDVI
            pk = mets['peak'][mask]; r['peak_cv'] = float(np.nanstd(pk) / np.nanmean(pk))
            rows.append(r)
df = pd.DataFrame(rows)
df['region'] = df.region_tag.str.replace('_', ' ').str.replace(' and The', ' & The')
df.to_csv(os.path.join(ROOT, 'data/processed/ndvi_site_year.csv'), index=False)
print(df.groupby(['region', 'cover']).agg(sites=('site', 'nunique'), years=('year', 'nunique'), npix=('npix', 'mean')).round(0))

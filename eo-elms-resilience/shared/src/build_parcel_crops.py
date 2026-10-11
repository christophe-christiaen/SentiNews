"""Combine CROME years into a crop history per parcel and join it to the parcel scheme table.

Input   shared/data/parcels/crome/parcel_crop_<year>.parquet   (from fetch_crome.py, 2016-2024)
        shared/data/parcels/parcel_schemes.parquet             (from build_parcel_schemes.py)
Output  shared/data/parcels/parcel_panel.parquet               one row per parcel: scheme group, entry year, crop
                                                              code per year, cereal years, cereal before entry
        shared/results/parcel_crops_summary.md                 counts only (safe to commit)

Definitions
  cereal_years       number of years the parcel was in cereals (wheat, barley, oats, rye, triticale)
  cereal_share       cereal_years / years observed
  cereal_land        cereal in at least half of the observed years (rotations include break crops)
  cereal_pre_entry   for agreement parcels: share of observed years before the entry year in cereals
  cereal_2018/2022   cereal in the two drought years
"""
import glob, os, re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
P = os.path.join(ROOT, 'shared', 'data', 'parcels')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 'parcel_crops_summary.md')


def main():
    files = sorted(glob.glob(os.path.join(P, 'crome', 'parcel_crop_*.parquet')))
    years = [int(re.search(r'(\d{4})', os.path.basename(f)).group(1)) for f in files]
    crop = cer = None
    for y, f in zip(years, files):
        d = pd.read_parquet(f, columns=['parcref', 'lucode', 'cereal']).set_index('parcref')
        c, k = d.lucode.rename(f'crop_{y}'), d.cereal.rename(f'cereal_{y}')
        crop = c.to_frame() if crop is None else crop.join(c, how='outer')
        cer = k.to_frame() if cer is None else cer.join(k, how='outer')
    t = pd.read_parquet(os.path.join(P, 'parcel_schemes.parquet')).set_index('parcref')
    t = t.join(crop).join(cer)
    ccols = [f'cereal_{y}' for y in years]
    obs = t[[f'crop_{y}' for y in years]].notna()
    t['years_observed'] = obs.sum(axis=1)
    t['cereal_years'] = t[ccols].fillna(False).astype(bool).sum(axis=1)
    t['cereal_share'] = (t.cereal_years / t.years_observed.where(t.years_observed > 0)).round(3)
    t['cereal_land'] = t.cereal_share >= 0.5
    entry = t.entry_year.astype('float')            # NaN where the parcel never entered
    before = {y: (entry > y) & t[f'crop_{y}'].notna() for y in years}   # NaN > y is False
    n_pre = sum(before[y].astype(int) for y in years)
    pre = sum((before[y] & t[f'cereal_{y}'].fillna(False).astype(bool)).astype(int) for y in years)
    t['cereal_pre_entry'] = (pre / n_pre.where(n_pre > 0)).round(3)
    t = t.reset_index()
    t.to_parquet(os.path.join(P, 'parcel_panel.parquet'), index=False)

    g = t.groupby('parcel_group')
    by_year = pd.DataFrame({y: t[f'cereal_{y}'].mean() for y in years}, index=['cereal share of parcels']).T
    lines = ['# Stage 0 · Parcel crop history (counts only)', '',
             f'- CROME years: {", ".join(map(str, years))}; parcels: {len(t):,}',
             f'- Parcels in cereals in at least half of the observed years (cereal land): {t.cereal_land.sum():,} '
             f'({t.cereal_land.mean():.1%})', '',
             '## Cereal land by scheme group', '',
             pd.DataFrame({'parcels': g.size(), 'cereal land': g.cereal_land.sum(),
                           'share': g.cereal_land.mean().round(3)}).to_markdown(), '',
             '## Agreement parcels on cereal land, by entry year', '',
             t[(t.parcel_group == 'agreement') & t.cereal_land].groupby('entry_year').size().rename('parcels').to_frame().to_markdown(), '',
             '## Share of parcels in cereals each year', '', by_year.round(3).to_markdown(), '',
             '- Agreement parcels that were mostly cereal before entry (cereal_pre_entry >= 0.5): '
             f'{(t.cereal_pre_entry >= 0.5).sum():,}',
             f'- Cereal land in the drought years: 2018 {t.get("cereal_2018", pd.Series(dtype=bool)).fillna(False).sum():,} parcels, '
             f'2022 {t.get("cereal_2022", pd.Series(dtype=bool)).fillna(False).sum():,} parcels']
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()

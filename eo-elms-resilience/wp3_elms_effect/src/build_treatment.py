"""WP3 treatment table for the pre-registered analysis (wp3_elms_effect/results/preregistration.md, sections 3-4).

Per cereal parcel in the analysis sample:
  entry_date    earliest start of an area-based CS or SFI option on the parcel (SFI snapped within 50 m)
  entry_year    calendar year of entry_date (the cohorts listed in the pre-registration)
  G             first full growing season under the agreement: entry_year if the contract starts on or before 1 March,
                otherwise entry_year + 1; never-treated parcels get G = 0
  family        A (management), B (land-use change), C (other) by the section 4 rule; 'never' for controls
  family_soh_a  the same with SOH (soil health) actions counted as A (exploratory version, decisions record (c))
Sample: cereal land; agreement parcels entering 2021-2026, never-treated parcels ('no agreement'); legacy CSS parcels,
'uncertain' and 'legacy ES' parcels excluded.

Input   shared/data/parcels/parcel_panel.parquet; scheme CSVs via shared/src/build_parcel_schemes.py
Output  wp3_elms_effect/data/treatment.parquet (gitignored); wp3_elms_effect/results/treatment_summary.md (counts)
"""
import os, re, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'shared', 'src'))
import build_parcel_schemes as bps

OUT = os.path.join(ROOT, 'wp3_elms_effect', 'data', 'treatment.parquet')
SUMMARY = os.path.join(ROOT, 'wp3_elms_effect', 'results', 'treatment_summary.md')
FAM_A = ('SAM1', 'SAM2', 'NUM', 'CNUM', 'IPM', 'CSAM1', 'CSAM2', 'CIPM', 'PRF')
FAM_B_SFI = ('SAM3', 'CSAM3', 'LIG', 'CLIG', 'AHL', 'CAHL')
FAM_B_CS = ('AB', 'GS', 'SW')


def base(code):
    return re.sub(r'_\d+$', '', str(code).strip().upper())


def in_family(code, fam, scheme):
    c = base(code)
    stem = re.sub(r'\d+[A-Z]?$', '', c)                      # NUM3 -> NUM, SAM1 stays SAM1 via the exact list
    if fam == 'A':
        return scheme == 'SFI' and (c in FAM_A or stem in FAM_A)
    if fam == 'B':
        return (scheme == 'SFI' and (c in FAM_B_SFI or stem in FAM_B_SFI)) or (scheme == 'CS' and stem in FAM_B_CS)
    if fam == 'SOH':
        return scheme == 'SFI' and stem == 'SOH'


def classify(codes, soh_as_a=False):
    """codes: list of (scheme, code). B if any in B, else A if any in A, else C."""
    if any(in_family(c, 'B', s) for s, c in codes):
        return 'B'
    if any(in_family(c, 'A', s) or (soh_as_a and in_family(c, 'SOH', s)) for s, c in codes):
        return 'A'
    return 'C'


def main():
    pan = pd.read_parquet(os.path.join(ROOT, 'shared', 'data', 'parcels', 'parcel_panel.parquet'))
    c = pan[pan.cereal_land & ~pan.css_legacy]
    agr = c[(c.parcel_group == 'agreement') & (c.entry_year >= 2021)]
    nev = c[c.parcel_group == 'no agreement']

    pts = pan[['parcref', 'x', 'y']].reset_index(drop=True)
    o = bps.options(); o['snap_m'] = 0.0
    allo = pd.concat([o, bps.sfi_snapped(pts)], ignore_index=True)
    allo = allo[allo.parcref.isin(agr.parcref) & allo.area_based & (allo.snap_m <= bps.SNAP_M) & allo.fam.isin(['CS', 'SFI'])]
    ent = allo.groupby('parcref').start.min().rename('entry_date')
    codes = allo.groupby('parcref').apply(lambda d: list(zip(d.fam, d.code)))

    t = agr[['parcref']].set_index('parcref').join(ent)
    t['entry_year'] = t.entry_date.dt.year
    cut = pd.to_datetime(t.entry_year.astype('Int64').astype(str) + '-03-01', errors='coerce')
    t['G'] = np.where(t.entry_date <= cut, t.entry_year, t.entry_year + 1)
    t['family'] = codes.reindex(t.index).map(classify)
    t['family_soh_a'] = codes.reindex(t.index).map(lambda x: classify(x, True))
    check = agr.set_index('parcref').entry_year
    mism = (t.entry_year != check.reindex(t.index)).sum()
    n = nev[['parcref']].set_index('parcref').assign(entry_date=pd.NaT, entry_year=np.nan, G=0, family='never',
                                                      family_soh_a='never')
    t = pd.concat([t, n]).reset_index()
    t['G'] = t.G.astype(int)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    t.to_parquet(OUT, index=False)

    a = t[t.G > 0]
    lines = ['# WP3 treatment table (counts only)', '',
             f'- Agreement parcels entering 2021-2026: {len(a):,}; never-treated: {(t.G == 0).sum():,}',
             f'- Entry year differs from the Stage 0 table: {mism:,} parcels (should be 0)', '',
             '## Entry year (cohort) by first full season', '',
             pd.crosstab(a.entry_year.astype(int), a.G).to_markdown(), '',
             '## Option family', '', a.family.value_counts().sort_index().to_frame('parcels').to_markdown(), '',
             'Family with SOH actions counted as A (exploratory):', '',
             a.family_soh_a.value_counts().sort_index().to_frame('parcels').to_markdown(), '',
             'First full season: the entry year if the contract starts on or before 1 March, otherwise the next season.']
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()

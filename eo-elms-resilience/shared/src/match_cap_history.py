"""Business-level scheme history: match the Companies House farms to Defra/CAP payment data for 2020 and 2021
(England sheets of the CAP beneficiary search export) and combine with the 2023/24-2024/25 register match.

CAP 2020/2021 (RPA sheets) list every English recipient: Basic Payment Scheme (BPS, ~ every active farm) and Rural
Development payments, incl. agri-environment (CS / ES). Names are given above the publication threshold; small
recipients are anonymised and cannot be matched. Matching uses the same normalised name + postcode district blocking
as match_payments.py (exact, then fuzzy >= FUZZY).

Input   shared/data/reference/payments/cap/20{20,21}_All_CAP_Search_Results_Data_P14.xlsx
        shared/data/farms/farms_all.csv, farm_payments.csv (2023-25 register match), farm_groups.csv
Output  shared/data/reference/payments/cap/cap_england_2020_2021.parquet   tidy England payments (private)
        shared/data/farms/farm_scheme_history.csv                           per farm: BPS / agri-env by year
        shared/results/scheme_history_summary.md                            counts only (safe to commit)
"""
import os
import numpy as np, pandas as pd
from rapidfuzz import fuzz, process
from match_payments import norm, district, FUZZY

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
CAP = os.path.join(D, 'reference', 'payments', 'cap')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 'scheme_history_summary.md')
SHEETS = {2020: ['RPA', 'RPA2'], 2021: ['RPA 1', 'RPA 2']}
AGRI_ENV = ['Agri-environment payments', 'Agri-environment-climate', 'Agri-environment-climate - UK funded']
BPS = ['Basic payment scheme', 'Basic payment scheme - UK funded']


def load_cap():
    out = []
    for y, sheets in SHEETS.items():
        f = os.path.join(CAP, f'{y}_All_CAP_Search_Results_Data_P14.xlsx')
        d = pd.concat([pd.read_excel(f, sheet_name=s) for s in sheets], ignore_index=True)
        num = lambda cols: d[[c for c in cols if c in d]].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1)
        out.append(pd.DataFrame({'year': y, 'name': d.BeneficiaryName_F201.astype(str).str.strip(' "\''),
                                 'district': d.PostcodePrefix_F202B.astype(str).str.upper().str.strip(),
                                 'bps': num(BPS), 'agri_env': num(AGRI_ENV),
                                 'rural_dev': pd.to_numeric(d.RuralDevelopmentTotal, errors='coerce').fillna(0),
                                 'total': pd.to_numeric(d.Total, errors='coerce').fillna(0)}))
    c = pd.concat(out, ignore_index=True)
    c = c[c.name.ne('*******')]                     # anonymised small recipients cannot be matched
    c['key'] = c.name.map(norm)
    return c


def match(farms, payees):
    """farm_id -> payee row index (exact name in district, else fuzzy)."""
    by_d = {k: g for k, g in payees.groupby('district')}
    hits = {}
    for r in farms.itertuples():
        g = by_d.get(r.district)
        if g is None:
            continue
        ex = g.index[g.key == r.key]
        if len(ex):
            hits[r.farm_id] = (ex[0], 'exact')
            continue
        m = process.extractOne(r.key, g.key.tolist(), scorer=fuzz.token_sort_ratio, score_cutoff=FUZZY)
        if m:
            hits[r.farm_id] = (g.index[m[2]], 'fuzzy')
    return hits


def main():
    cap = load_cap()
    cap.drop(columns='key').to_parquet(os.path.join(CAP, 'cap_england_2020_2021.parquet'), index=False)
    farms = pd.read_csv(os.path.join(D, 'farms', 'farms_all.csv'), dtype={'company_number': str})
    farms = farms[farms.country == 'England'].copy()
    farms['district'] = farms.postcode.map(district)
    farms['key'] = farms.company_name.map(norm)

    h = farms[['farm_id']].copy()
    for y in SHEETS:
        p = cap[cap.year == y].groupby(['district', 'key']).agg(name=('name', 'first'), bps=('bps', 'sum'),
                                                                 agri_env=('agri_env', 'sum'), total=('total', 'sum')).reset_index()
        hits = match(farms, p)
        idx = h.farm_id.map(lambda f: hits.get(f, (None, None))[0])
        h[f'cap{y}_match'] = h.farm_id.map(lambda f: hits.get(f, (None, 'none'))[1])
        for col in ('bps', 'agri_env'):
            h[f'{col}_{y}'] = idx.map(lambda i: p.at[i, col] if i is not None and not pd.isna(i) else 0.0)
        h[f'bps_{y}_paid'] = h[f'bps_{y}'] > 0
        h[f'agri_env_{y}'] = h[f'agri_env_{y}'] > 0
        h = h.drop(columns=[f'bps_{y}'])

    reg = pd.read_csv(os.path.join(D, 'farms', 'farm_payments.csv'))
    for fy in ('23/24', '24/25'):
        h[f'sfi_cs_{fy.replace("/", "_")}'] = h.farm_id.map(
            reg.set_index('farm_id').apply(lambda r: bool(r.pay_agri_env) and fy in str(r.pay_years), axis=1)).fillna(False)
    h['any_cap_match'] = h[[f'cap{y}_match' for y in SHEETS]].ne('none').any(axis=1)
    h['active_farm_bps'] = h[[f'bps_{y}_paid' for y in SHEETS]].any(axis=1)
    h['agri_env_2020_21'] = h.agri_env_2020 | h.agri_env_2021
    h['agri_env_2023_25'] = h.sfi_cs_23_24 | h.sfi_cs_24_25
    h['first_agri_env_period'] = np.select([h.agri_env_2020_21, h.agri_env_2023_25], ['2020-21', '2023-25'], 'none seen')
    groups = pd.read_csv(os.path.join(D, 'farms', 'farm_groups.csv'), usecols=['farm_id', 'group_final'])
    h = h.merge(groups, on='farm_id', how='left')
    h.to_csv(os.path.join(D, 'farms', 'farm_scheme_history.csv'), index=False)

    t = lambda s: s.value_counts().rename_axis('').to_frame('farms').to_markdown()
    nag = h[h.group_final == 'no agreement']
    lines = ['# Stage 0 · Business-level scheme history (counts only)', '',
             f'- CAP payment data, England: {cap.year.value_counts().sort_index().to_dict()} named recipients '
             f'(anonymised small recipients excluded)',
             f'- English companies matched in 2020: {(h.cap2020_match != "none").sum():,}; in 2021: '
             f'{(h.cap2021_match != "none").sum():,}; in either: {h.any_cap_match.sum():,} of {len(h):,}',
             f'- Receiving BPS in 2020 or 2021 (active farms): {h.active_farm_bps.sum():,}',
             f'- With agri-environment payments: 2020 {h.agri_env_2020.sum():,}, 2021 {h.agri_env_2021.sum():,}, '
             f'2023/24 {h.sfi_cs_23_24.sum():,}, 2024/25 {h.sfi_cs_24_25.sum():,}', '',
             '## First period with agri-environment payments', '', t(h.first_agri_env_period), '',
             '## Agri-environment history by analysis group', '',
             pd.crosstab(h.group_final.fillna('n/a'), [h.agri_env_2020_21.map({True: 'agri-env 2020-21', False: 'none 2020-21'})]).to_markdown(), '',
             f'- **No agreement** farms that did receive agri-environment payments in 2020 or 2021 (earlier CS / ES): '
             f'{nag.agri_env_2020_21.sum():,} of {len(nag):,} ({nag.agri_env_2020_21.mean():.0%})',
             f'- **No agreement** farms confirmed as active farms (BPS 2020/21): {nag.active_farm_bps.sum():,}', '',
             'A farm absent from the CAP data may be anonymised (small payments) or paid under another name.']
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()

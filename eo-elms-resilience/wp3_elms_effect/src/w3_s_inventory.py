"""W3-S Part A, step 1: inventory of every option or action code (protocol: w3_s_option_stacks_protocol.md, Part A).

Scheme metadata only: code, description, unit and the number of parcels carrying the code. No outcome or EO feature is
read. Scope: CS options and SFI actions starting 2021-2024; ES options live at any time in 2021-2024 (end on or after
1 January 2021, start on or before 31 December 2024). SFI actions are snapped to parcel points as in the treatment table
(within 50 m). SFI descriptions come from Defra's SFI action summaries (SFI23 and SFI24 sheets).

Output: wp3_elms_effect/results/w3_s_inventory.csv (codes and counts only; public);
        wp3_elms_effect/data/w3_s_parcel_codes.parquet (parcel-code pairs; private).
"""
import os, re, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'shared', 'src'))
import build_parcel_schemes as bps

NAT = os.path.join(ROOT, 'shared', 'data', 'schemes', 'national')
ODS = os.path.join(ROOT, 'shared', 'data', 'reference', 'SFI_option_data2025-11-04.ods')
OUT = os.path.join(ROOT, 'wp3_elms_effect', 'results', 'w3_s_inventory.csv')
PAIRS = os.path.join(ROOT, 'wp3_elms_effect', 'data', 'w3_s_parcel_codes.parquet')   # private
Y0, Y1 = pd.Timestamp('2021-01-01'), pd.Timestamp('2024-12-31')


def base(code):
    return re.sub(r'_\d+$', '', str(code).strip().upper())


def descriptions():
    cs = pd.read_csv(os.path.join(NAT, 'cs_options.csv'), dtype=str, usecols=['OPTION_CODE', 'OPTION_DESCRIPTION', 'UNIT_OF_MEASURE'])
    cs = cs.assign(code=cs.OPTION_CODE.map(base), desc=cs.OPTION_DESCRIPTION.str.replace(r'^\S+ - ', '', regex=True),
                   unit=cs.UNIT_OF_MEASURE.str.upper())
    es = pd.read_csv(os.path.join(NAT, 'es_options.csv'), dtype=str, usecols=['OPTCODE', 'OPTTITLE', 'UOM'])
    es = es.assign(code=es.OPTCODE.map(base), desc=es.OPTTITLE, unit=es.UOM.str.upper())
    sfi = []
    for sh in ('Number_of_agreements_SFI23', 'Number_of_agreements_SFI24'):
        x = pd.read_excel(ODS, engine='odf', sheet_name=sh, header=None).iloc[2:, :2].dropna()
        sfi.append(pd.DataFrame({'code': x[0].map(base), 'desc': x[1]}))
    sfi = pd.concat(sfi).drop_duplicates('code')
    su = pd.read_csv(os.path.join(NAT, 'sfi_actions.csv'), dtype=str, usecols=['option_code', 'uom_desc'])
    su = su.assign(code=su.option_code.map(base), unit=su.uom_desc.str.upper()).groupby('code').unit.agg(lambda s: s.mode().iat[0])
    mode = lambda d: d.groupby('code').agg(desc=('desc', lambda s: s.mode().iat[0] if s.notna().any() else ''),
                                           unit=('unit', lambda s: s.mode().iat[0] if s.notna().any() else ''))
    return {'CS': mode(cs), 'ES': mode(es), 'SFI': sfi.set_index('code').join(su, how='outer')}


def main():
    pan = pd.read_parquet(os.path.join(ROOT, 'shared', 'data', 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y'])
    o = bps.options(); o['snap_m'] = 0.0
    allo = pd.concat([o, bps.sfi_snapped(pan.reset_index(drop=True))], ignore_index=True)
    allo['code'] = allo.code.map(base)
    starts = allo.start.between(Y0, Y1); live = (allo.end >= Y0) & (allo.start <= Y1)
    keep = ((allo.fam.isin(['CS', 'SFI']) & starts) | ((allo.fam == 'ES') & live)) & (allo.snap_m <= bps.SNAP_M)
    a = allo[keep].drop_duplicates(['fam', 'code', 'parcref'])
    os.makedirs(os.path.dirname(PAIRS), exist_ok=True)
    a[['parcref', 'fam', 'code']].rename(columns={'fam': 'scheme'}).to_parquet(PAIRS, index=False)
    n = a.groupby(['fam', 'code']).size().rename('parcels').reset_index()
    D = descriptions()
    n['description'] = [D[f].desc.get(c, '') for f, c in zip(n.fam, n.code)]
    n['unit'] = [D[f].unit.get(c, '') for f, c in zip(n.fam, n.code)]
    n = n.rename(columns={'fam': 'scheme'}).sort_values(['scheme', 'code'])
    n.to_csv(OUT, index=False)
    print(n.groupby('scheme').agg(codes=('code', 'size'), parcels=('parcels', 'sum'), no_desc=('description', lambda s: (s.fillna('') == '').sum())))
    print('codes with >= 1,000 parcels:', (n.parcels >= 1000).sum())


if __name__ == '__main__':
    main()

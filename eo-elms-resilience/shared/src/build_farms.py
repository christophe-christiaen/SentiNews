"""Stage 0: assemble the farm list from Companies House search exports, deduplicate, and geocode by postcode.

Input   shared/data/farms/raw/companies_house/*.csv   Companies House advanced-search exports (SIC 01110, 01500, ...)
        shared/data/reference/codepoint_open/          OS Code-Point Open (postcode -> BNG easting/northing, country)
Output  shared/data/farms/farms_all.csv               every unique company, with postcode, XY and flags
        shared/data/farms/farms_england.csv/.gpkg     English companies with coordinates (the Stage 1-2 farm list)
        shared/results/farms_stage0_summary.md        counts only (safe to commit)

Geocoding is local (postcode centroid from Code-Point Open): no address leaves this machine.
Caveat: the point is the company's REGISTERED OFFICE, which is often the farm but sometimes an accountant or agent.
Each record gets an address_kind flag so office-like addresses can be checked or replaced (e.g. by a holding location).
"""
import glob, os, re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
DATA = os.path.join(ROOT, 'shared', 'data')
RAW = os.path.join(DATA, 'farms', 'raw', 'companies_house')
CPO = os.path.join(DATA, 'reference', 'codepoint_open', 'x', 'Data', 'CSV')
OUT = os.path.join(DATA, 'farms')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 'farms_stage0_summary.md')

# exports are not properly quoted (commas inside names and addresses), so anchor on the company number
ROW = re.compile(r'^(?P<company_name>.*?),(?P<company_number>(?:[A-Z]{1,2}\d{6,7}|\d{8})),(?P<company_status>[^,]*),'
                 r'(?P<company_type>[^,]*),(?P<company_subtype>[^,]*),(?P<dissolution_date>[^,]*),'
                 r'(?P<incorporation_date>[^,]*),(?P<removed_date>[^,]*),(?P<registered_date>[^,]*),'
                 r'(?P<sic>"?\[[^\]]*\]"?|[^,]*),(?P<address>.*)$')
POSTCODE = re.compile(r'([A-Z]{1,2}[0-9][A-Z0-9]?) ?([0-9][A-Z]{2})\W*$')
SIC_NAMES = {'01110': 'cereals', '01500': 'mixed farming', '01130': 'vegetables', '01610': 'crop support',
             '01410': 'dairy', '01420': 'cattle', '01450': 'sheep', '01270': 'beverage crops'}
STRONG_OFFICE = re.compile(r'\b(c/o|suite|floor|chambers|accountants?|chartered|solicitors?|business (park|centre|center)|plaza|tower)\b', re.I)
OFFICE = re.compile(r'\b(unit \d|office|house,? \d|\d+[a-z]? [a-z]+ (street|road|square|place|lane)|high street)\b', re.I)
SHARED = 5   # a postcode shared by this many companies or more is an agent's / accountant's address
FARM = re.compile(r'\b(farm|farms|hall|manor|grange|barn|barns|estate|lodge|mill|court farm|house farm|cottage|abbey|priory)\b', re.I)
COUNTRY = {'E92000001': 'England', 'W92000004': 'Wales', 'S92000003': 'Scotland'}


def read_exports():
    rows, bad = [], 0
    for fn in sorted(glob.glob(os.path.join(RAW, '*.csv'))):
        with open(fn, encoding='utf-8-sig') as fh:
            next(fh)
            for line in fh:
                line = line.rstrip('\r\n')
                if not line.strip():
                    continue
                m = ROW.match(line)
                if m:
                    rows.append(dict(m.groupdict(), source_file=os.path.basename(fn)))
                else:
                    bad += 1
    d = pd.DataFrame(rows)
    for c in d.columns:
        d[c] = d[c].str.strip('" ')
    return d, bad


def address_kind(a):
    if STRONG_OFFICE.search(a):
        return 'office-like'
    if FARM.search(a):            # includes 'The Farm Office, X Farm'
        return 'farm-like'
    if OFFICE.search(a):
        return 'office-like'
    return 'unclear'


def main():
    d, bad = read_exports()
    n_rows = len(d)
    d['sic_codes'] = d.sic.str.findall(r'\d{5}').str.join(';')
    files = d.groupby('company_number').source_file.agg(lambda s: ';'.join(sorted(set(s))))
    d = d.drop_duplicates('company_number').drop(columns=['sic', 'source_file']).merge(files, on='company_number')
    m = d.address.str.upper().str.extract(POSTCODE)
    d['postcode'] = (m[0] + ' ' + m[1]).where(m[0].notna())
    d['address_kind'] = d.address.map(address_kind)
    d['companies_at_postcode'] = d.groupby('postcode').company_number.transform('size').where(d.postcode.notna())
    d.loc[d.companies_at_postcode >= SHARED, 'address_kind'] = 'agent (shared postcode)'
    d['cereals'] = d.sic_codes.str.contains('01110')
    d['mixed_farming'] = d.sic_codes.str.contains('01500')
    # possible duplicates: different companies with the same normalised name stem at the same postcode
    stem = d.company_name.str.upper().str.replace(r'\b(LIMITED|LTD|LLP|PLC|THE|AND|&|CO|COMPANY)\b|[^A-Z0-9 ]', '', regex=True) \
        .str.split().str.join(' ')
    d['possible_duplicate'] = d.assign(stem=stem).duplicated(['stem', 'postcode'], keep=False) & d.postcode.notna()

    cpo = pd.concat(pd.read_csv(f, header=None, usecols=[0, 1, 2, 3, 4], dtype={0: str, 4: str},
                                names=['pc', 'pq', 'x_bng', 'y_bng', 'country_code']) for f in glob.glob(os.path.join(CPO, '*.csv')))
    cpo['postcode'] = cpo.pc.str.replace(' ', '').str.replace(r'^(.+)(\d[A-Z]{2})$', r'\1 \2', regex=True)
    d = d.merge(cpo[['postcode', 'pq', 'x_bng', 'y_bng', 'country_code']], on='postcode', how='left')
    d.loc[d.pq >= 90, ['x_bng', 'y_bng']] = None            # 90 = no coordinates for this postcode
    d['country'] = d.country_code.map(COUNTRY)
    d.loc[d.country.isna() & d.postcode.str.startswith('BT', na=False), 'country'] = 'Northern Ireland'
    d.loc[d.country.isna() & d.company_number.str.match(r'^(NI|R0)'), 'country'] = 'Northern Ireland'
    d['geocoded'] = d.x_bng.notna()
    d['farm_id'] = 'CH' + d.company_number
    cols = ['farm_id', 'company_number', 'company_name', 'company_type', 'incorporation_date', 'sic_codes', 'cereals',
            'mixed_farming', 'address', 'postcode', 'country', 'x_bng', 'y_bng', 'pq', 'geocoded', 'address_kind',
            'companies_at_postcode', 'possible_duplicate', 'source_file']
    d = d[cols].sort_values('farm_id')
    os.makedirs(OUT, exist_ok=True)
    d.to_csv(os.path.join(OUT, 'farms_all.csv'), index=False)
    e = d[(d.country == 'England') & d.geocoded].copy()
    e.to_csv(os.path.join(OUT, 'farms_england.csv'), index=False)
    try:
        import geopandas as gpd
        gpd.GeoDataFrame(e, geometry=gpd.points_from_xy(e.x_bng, e.y_bng), crs=27700) \
            .to_file(os.path.join(OUT, 'farms_england.gpkg'), layer='farms', driver='GPKG')
    except ImportError:
        pass

    # summary: counts only
    t = lambda s: s.value_counts(dropna=False).rename_axis('').to_frame('companies').to_markdown()
    lines = ['# Stage 0 · Farm list (counts only)', '',
             f'- Rows in the Companies House exports: {n_rows:,} ({bad} unparseable lines); unique companies: {len(d):,}',
             f'- Postcode found in the address: {d.postcode.notna().mean():.1%}; matched to Code-Point Open: {d.geocoded.mean():.1%}',
             f'- **English companies with coordinates: {len(e):,}** (cereals SIC 01110: {e.cereals.sum():,}; '
             f'mixed farming 01500: {e.mixed_farming.sum():,})',
             f'- Possible duplicates (same name stem and postcode, different company numbers): {d.possible_duplicate.sum():,} '
             '(kept, flagged)', '', '## By country', '', t(d.country.fillna('not matched')), '',
             '## Registered-office type (England)', '', t(e.address_kind), '',
             f'Office-like and shared-postcode addresses (accountants, agents, town-centre offices; {SHARED}+ companies at one '
             'postcode) do not locate the farm. Use farm-like and unclear addresses first; the others need another location '
             '(e.g. a scheme holding).', '', '## Postcode positional quality (England)', '',
             t(e.pq.map({10: '10 within a building', 20: '20 same street', 30: '30 approximate', 40: '40 estimated',
                         50: '50 postcode sector', 60: '60 sector', 90: '90 none'}).fillna('other')), '',
             '## Main SIC codes (all companies)', '']
    sic = d.sic_codes.str.split(';').explode().value_counts().head(10)
    lines += ['| SIC | Activity | Companies |', '|---|---|---|'] + \
             [f'| {k} | {SIC_NAMES.get(k, "")} | {v:,} |' for k, v in sic.items()]
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()

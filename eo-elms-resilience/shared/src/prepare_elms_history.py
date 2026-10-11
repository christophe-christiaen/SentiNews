"""Stage 0: tidy the agreement-history extract ELMS_all.csv (Environmental Stewardship options, parcel level).

Input   shared/data/schemes/raw/ELMS_all.csv
Output  shared/data/schemes/history/es_options_history.parquet   one row per option x parcel, dates parsed
        shared/results/elms_all_summary.md                         counts only (safe to commit)

The extract holds 1,048,575 rows, exactly Excel's row limit, and its last line is cut mid-record: it was almost
certainly truncated when saved from Excel. Treat it as a partial history and prefer the full national download
(fetch_schemes.py --national es_options) where both cover the same agreements.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'shared', 'data', 'schemes', 'raw', 'ELMS_all.csv')
OUT = os.path.join(ROOT, 'shared', 'data', 'schemes', 'history')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 'elms_all_summary.md')
EXCEL_MAX_ROWS = 1_048_576
KEEP = ['agref', 'appstat', 'scheme', 'startdat', 'enddate', 'workstart', 'workend', 'optcode', 'opttitle', 'caprevid',
        'optlevel', 'parcref', 'holdpref', 'parcelx', 'parcely', 'holdx', 'holdy', 'quantity', 'uom', 'areaha', 'nca',
        'bus_flag', 'withheld']


def main():
    with open(SRC, 'rb') as fh:
        n_lines = sum(1 for _ in fh)
    d = pd.read_csv(SRC, dtype=str, usecols=KEEP, on_bad_lines='skip', encoding_errors='replace')
    last_complete = d.iloc[-1].notna().sum() == len(KEEP)
    for c in ('startdat', 'enddate', 'workstart', 'workend'):
        d[c] = pd.to_datetime(d[c], format='%m/%d/%Y %H:%M:%S', errors='coerce')
    for c in ('parcelx', 'parcely', 'holdx', 'holdy', 'quantity', 'areaha'):
        d[c] = pd.to_numeric(d[c], errors='coerce')
    for c in ('parcelx', 'parcely', 'holdx', 'holdy'):
        d.loc[d[c] <= 0, c] = None
    os.makedirs(OUT, exist_ok=True)
    d.to_parquet(os.path.join(OUT, 'es_options_history.parquet'), index=False)

    truncated = n_lines >= EXCEL_MAX_ROWS or not last_complete
    t = lambda s: s.value_counts().sort_index().rename_axis('').to_frame('rows').to_markdown()
    lines = ['# Stage 0 · ELMS_all.csv (agreement history extract)', '',
             f'- Rows: {len(d):,}; agreements: {d.agref.nunique():,}; holdings: {d.holdpref.nunique():,}; '
             f'option codes: {d.optcode.nunique():,}',
             f'- **Probably truncated: {"yes" if truncated else "no"}** ({n_lines:,} lines incl. header = Excel row limit; '
             'last record incomplete). Ask for the original export, or rely on the national ES download.',
             '- Schemes: ' + '; '.join(f'{k} ({v:,})' for k, v in d.scheme.value_counts().items()),
             f'- Agreement starts {d.startdat.dt.year.min()}–{d.startdat.dt.year.max()}, ends {d.enddate.dt.year.min()}–'
             f'{d.enddate.dt.year.max()}: Environmental Stewardship only (no Countryside Stewardship or SFI)',
             f'- Holding coordinates present: {d.holdx.notna().mean():.1%} of rows; withheld rows: {(d.withheld == "YES").sum():,}',
             '- No names or contact details in the file (agreement, parcel and holding references only).', '',
             '## Rows by agreement start year', '', t(d.startdat.dt.year.astype('Int64')), '',
             '## Rows by agreement end year', '', t(d.enddate.dt.year.astype('Int64')), '']
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:9]))


if __name__ == '__main__':
    main()

"""Inventory of the pilot scheme layers: start-year spread, top options, per-site counts.
Writes wp3_elms_effect/results/scheme_inventory_pilot.md and shared/data/schemes/pilot/site_inventory.csv."""
import json, os
import pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
D = os.path.join(ROOT, 'shared', 'data', 'schemes', 'pilot')
START = dict(cs_options='STARTDATE', cs_management_areas='STARTDATE', es_options='STARTDAT', es_agreements='STARTDAT',
             sfi_actions='contract_start', sfi_agreement_areas='contract_start')
CODE = dict(cs_options='OPTION_CODE', es_options='OPTCODE', sfi_actions='option_code')
DESC = dict(cs_options='OPTION_DESCRIPTION', es_options='OPTTITLE')

def start_year(s):
    s = s.astype(str)
    num = pd.to_numeric(s, errors='coerce')
    ms = pd.to_datetime(num.where(num > 1e11), unit='ms', errors='coerce')            # epoch milliseconds
    ymd = pd.to_datetime(s.where(s.str.fullmatch(r'\d{8}')), format='%Y%m%d', errors='coerce')
    iso = pd.to_datetime(s.where(s.str.contains('-')), errors='coerce', utc=True).dt.tz_localize(None)
    return ms.fillna(ymd).fillna(iso).dt.year

lines = ['# Scheme layers in the 40 English pilot windows', '',
         'Live snapshots (ended agreements are not included). Source: Natural England / RPA (OGL v3).', '']
inv = []
for layer, col in START.items():
    fc = json.load(open(os.path.join(D, f'{layer}.geojson')))
    df = pd.DataFrame([f['properties'] for f in fc['features']])
    if df.empty: continue
    df['start_year'] = start_year(df[col])
    lines += [f'## {layer} ({len(df):,} records, {df.groupby(["region", "site"]).ngroups} sites)', '',
              'Start years: ' + ', '.join(f'{int(y)}: {n}' for y, n in df.start_year.value_counts().sort_index().items()), '']
    if layer in CODE:
        top = df.groupby(CODE[layer]).size().sort_values(ascending=False).head(12)
        desc = df.drop_duplicates(CODE[layer]).set_index(CODE[layer])[DESC[layer]] if layer in DESC else None
        lines += ['| Code | Records | Description |', '|---|---|---|']
        lines += [f'| {c} | {n} | {str(desc.get(c, "")).replace("|", "/")[:70] if desc is not None else ""} |' for c, n in top.items()] + ['']
    g = df.groupby(['region', 'site']).size().rename(layer)
    inv.append(g)
site = pd.concat(inv, axis=1).fillna(0).astype(int).reset_index()
site['points_total'] = site[[c for c in ('cs_options', 'es_options', 'sfi_actions') if c in site]].sum(axis=1)
site = site.sort_values('points_total', ascending=False)
site.to_csv(os.path.join(D, 'site_inventory.csv'), index=False)
lines += ['## Sites with most option/action points', '', site.head(10).to_markdown(index=False), '']
out = os.path.join(ROOT, 'wp3_elms_effect', 'results', 'scheme_inventory_pilot.md')
open(out, 'w').write('\n'.join(lines)); print('\n'.join(lines))

"""Data check (1 November 2026): are "never-treated" parcels really never in a scheme?

The ES history extract (shared/data/schemes/raw/ELMS_all.csv) has exactly 1,048,575 rows, Excel's limit, so it is
probably truncated. This checks the never-treated parcels of parcel_panel.parquet against older Natural England
snapshots held by the project lead (~/Downloads): option points by PARCREF, and agreement outlines by containment of
the RPA parcel point. Reads scheme records and geometry only; no outcome. Changes nothing; writes aggregates.
Usage: python check_never_treated_snapshots.py
"""
import json, os
from pathlib import Path
import geopandas as gpd, pandas as pd, pyogrio

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'shared' / 'data'
DL = Path.home() / 'Downloads'
OUT = ROOT / 'wp3_elms_effect' / 'results' / 'never_treated_snapshot_check.json'

pan = pd.read_parquet(D / 'parcels' / 'parcel_panel.parquet', columns=['parcref', 'x', 'y', 'parcel_group', 'cereal_land'])
never = pan[pan.parcel_group == 'no agreement']
cer = set(never.parcref[never.cereal_land])
allnever = set(never.parcref)


def zpath(z):
    return f'/vsizip/{DL / z}'


def first_layer(src):
    return pyogrio.list_layers(src)[0][0]


# option snapshots: (label, source path, layer or None, parcel-reference column, start-date column)
OPT = [('ES options Oct 2023', zpath('Environmental_Stewardship_Scheme_Options_-5671551631491542539.zip') + '/Environmental_Stewardship_Scheme_Options_(England)___Natural_England.shp', 'PARCREF', 'STARTDAT'),
       ('ES options Nov 2025 (gdb)', zpath('Environmental_Stewardship_Scheme_Options_1394686066374668060.zip') + '/de361e5f-c146-4c28-a60a-a863b9563de2.gdb', 'PARCREF', 'STARTDAT'),
       ('ES options elms.gpkg (Nov 2025)', str(DL / 'elms.gpkg'), 'PARCREF', 'STARTDAT'),
       ('CS options Mar 2024', zpath('Countryside_Stewardship_Scheme_Options_629916221128040189.zip') + '/Countryside_Stewardship_Scheme_Options___Natural_England.shp', 'PARC_REF', 'STARTDAT'),
       ('CS options gpkg (Aug 2025)', str(DL / 'Countryside_Stewardship_Scheme_2016_Options_England_4881680122048640024.gpkg'), 'PARCREF', 'STARTDATE')]
AGR = [('ES agreements Oct 2022', zpath('Environmental_Stewardship_Agreements_England_-3405005387259729334.zip') + '/Environmental_Stewardship_Scheme_Agreements_(England)___Natural_England.shp'),
       ('ES agreements Oct 2023', zpath('Environmental_Stewardship_Agreements_England_-3405005387259729334(1).zip') + '/Environmental_Stewardship_Scheme_Agreements_(England)___Natural_England.shp'),
       ('CS agreements Mar 2024', zpath('Countryside_Stewardship_Scheme_Agreements_2591408201934897153.zip') + '/Countryside_Stewardship_Scheme_Agreements___Natural_England.shp')]

res, hits_cer, hits_all = {}, set(), set()
for label, src, pc, sc in OPT:
    lay = first_layer(src)
    cols = [c for c in pyogrio.read_info(src, layer=lay)['fields'] if c.upper() in (pc, sc)]
    df = pyogrio.read_dataframe(src, layer=lay, columns=cols, read_geometry=False)
    df.columns = [c.upper() for c in df.columns]
    p = set(df[pc].dropna().astype(str).str.replace(' ', ''))
    hc, ha = cer & p, allnever & p
    hits_cer |= hc; hits_all |= ha
    res[label] = dict(records=int(len(df)), parcels=len(p), never_cereal_found=len(hc), never_all_found=len(ha))
    print(label, res[label], flush=True)

P = gpd.GeoDataFrame(never[['parcref', 'cereal_land']], geometry=gpd.points_from_xy(never.x, never.y), crs=27700)
for label, src in AGR:
    a = pyogrio.read_dataframe(src, columns=['AGREF']).to_crs(27700)  # agreement ID only; names and other fields not read
    j = gpd.sjoin(P, a, predicate='within')
    ha = set(j.parcref); hc = ha & cer
    res[label] = dict(outlines=int(len(a)), never_cereal_inside=len(hc), never_all_inside=len(ha))
    print(label, res[label], flush=True)
    res[label + ' (not in any option snapshot)'] = dict(never_cereal=len(hc - hits_cer), never_all=len(ha - hits_all))

res['summary'] = dict(never_cereal=len(cer), never_all=len(allnever),
                      never_cereal_in_any_option_snapshot=len(hits_cer), share_cereal=round(len(hits_cer) / len(cer), 4),
                      never_all_in_any_option_snapshot=len(hits_all), share_all=round(len(hits_all) / len(allnever), 4))
OUT.write_text(json.dumps(res, indent=1))
print(json.dumps(res['summary'], indent=1))

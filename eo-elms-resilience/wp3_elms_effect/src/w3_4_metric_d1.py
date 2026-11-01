"""W3-4 detection rerun under deviation D1 (decisions record, 1 November 2026): comparison A with never-treated parcels
found in older option snapshots removed (primary rule). Everything else as w3_4_metric.py; registered files untouched;
outputs w3_4_metric_d1.{json,md}.
"""
import os, sys, shutil, tempfile
import pandas as pd, pyogrio

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import option_detection as od
import w3_4_metric as m
from wp3_d1_clean_controls import OPT


def contaminated():
    refs = set()
    for src, pc, _ in OPT:
        lay = pyogrio.list_layers(src)[0][0]
        col = [c for c in pyogrio.read_info(src, layer=lay)['fields'] if c.upper() == pc]
        refs |= set(pyogrio.read_dataframe(src, layer=lay, columns=col, read_geometry=False).iloc[:, 0].astype(str).str.replace(' ', ''))
    return refs


bad = contaminated()
_load = od.load
def load_clean():
    agr, never, mgmt = _load()
    print('never-treated', len(never), 'dropped', int(never.parcref.isin(bad).sum()), flush=True)
    return agr, never[~never.parcref.isin(bad)].copy(), mgmt
od.load = load_clean

res = m.RES
with tempfile.TemporaryDirectory() as tmp:
    m.RES = tmp
    m.main()
    shutil.copy(os.path.join(tmp, 'w3_4_metric.json'), os.path.join(res, 'w3_4_metric_d1.json'))
    md = open(os.path.join(tmp, 'w3_4_metric.md')).read()
    note = ('> **Deviation D1 (1 November 2026):** comparison A (never-treated) with parcels found in older Natural England option '
            'snapshots removed. Registered results: [w3_4_metric.md](w3_4_metric.md). Comparison B is unchanged.\n\n')
    open(os.path.join(res, 'w3_4_metric_d1.md'), 'w').write(md.replace('\n\n', '\n\n' + note, 1))
print('written w3_4_metric_d1')

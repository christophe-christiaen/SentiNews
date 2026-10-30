"""Which years of the precomputed OlmoEarth v1.3 embeddings cover England? (addendum 5, gate for OE13)

Reads only the public provenance tables (one row per 20.48 km window per year), never the embeddings or any label.
A window counts as England if its centre falls in lon -5.8..1.8, lat 49.9..55.8 (a box; includes parts of Wales).
Usage: python check_olmoearth13_coverage.py OUT_DIR   (downloads windows/<year>.parquet, 7-20 MB each, into OUT_DIR)
"""
import json, sys, urllib.request
from pathlib import Path
import pandas as pd, pyarrow.parquet as pq

BASE = 'https://data.source.coop/olmoearth/olmoearth-v1-3-embeddings/provenance/windows'
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
res = {}
for y in range(2017, 2026):
    f = out / f'windows_{y}.parquet'
    req = urllib.request.Request(f'{BASE}/{y}.parquet', headers={'User-Agent': 'curl/8'})  # the proxy refuses urllib's default agent
    f.write_bytes(urllib.request.urlopen(req).read())
    t = pq.read_table(f, columns=['written', 'bbox']).to_pandas()
    t = pd.concat([t.drop(columns='bbox'), pd.json_normalize(t['bbox'])], axis=1)
    cx, cy = (t.xmin + t.xmax) / 2, (t.ymin + t.ymax) / 2
    e = t[(cx > -5.8) & (cx < 1.8) & (cy > 49.9) & (cy < 55.8)]
    res[y] = dict(windows=int(len(e)), written=int(e.written.sum()))
full = max(v['windows'] for v in res.values())
for y, v in res.items():
    v['complete'] = v['written'] == full
print(json.dumps(res, indent=1))

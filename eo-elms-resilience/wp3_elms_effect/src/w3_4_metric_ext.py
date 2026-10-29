"""W3-4 addendum (wp3_elms_effect/results/w3_4_metric_protocol.md, record of 18 October 2026, written before
extraction): the placebo-adjusted detection metric rerun with two further feature families, same families,
comparisons, sample, model, bootstrap and reading rules as w3_4_metric.py.

  TESSERA v1.1 (128-d annual): pre = mean of 2018-2019 (2017 missing in the store); I0 year 2020; post 2025
  Presto (128-d, farm seasons October-September): pre = mean of seasons 2018-2019; I0 season 2020; post season 2025

Output  wp3_elms_effect/results/w3_4_metric_ext.md, .json
"""
import glob, json, os
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
import option_detection as od
import w3_4_metric as m

EMB = os.path.join(od.D, 'embeddings')
SOURCES = {'TESSERA': ('tessera_parcels', 't', 'T'), 'Presto': ('presto_parcels', 'p', 'P')}


def load(name, years, keep):
    folder, pre, col = SOURCES[name]
    parts = []
    for y in years:
        for f in sorted(glob.glob(os.path.join(EMB, folder, f'{pre}_*_{y}.parquet'))):
            parts.append(pd.read_parquet(f))
    d = pd.concat(parts, ignore_index=True)
    d = d[d.parcref.isin(keep)]
    cols = [c for c in d.columns if c.startswith(col)]
    d[cols] = d[cols].astype('float32')
    return d.groupby('parcref')[cols].mean()


def main():
    agr, never, mgmt = od.load()
    keep = set(agr.parcref) | set(never.parcref)
    feats = {n: {'pre': load(n, [2018, 2019], keep), 'y2020': load(n, [2020], keep), 'post': load(n, [2025], keep)} for n in SOURCES}
    print({n: {k: v.shape for k, v in F.items()} for n, F in feats.items()}, flush=True)
    out = {}
    for fam, cs in od.FAMILIES.items():
        cs = set(cs)
        pos = agr[agr.codes.map(lambda c: len(c & cs) > 0)]
        comps = {'A': never}
        if fam != 'Management only (control)':
            comps['B'] = mgmt[~mgmt.parcref.isin(pos.parcref)]
        for clab, comp in comps.items():
            df = od.sample(pos, comp).reset_index(drop=True)
            for flab, F in feats.items():
                g = lambda k: F[k].reindex(df.parcref).values
                sets = {'pre': g('pre'), 'post': g('post'), 'pre+post': np.hstack([g('pre'), g('post')]),
                        'pre+2020': np.hstack([g('pre'), g('y2020')]), 'change': g('post') - g('pre')}
                preds = {k: m.loro_pred(df, X) for k, X in sets.items()}
                r = m.assess(df, {k: v for k, v in preds.items() if k != 'change'})
                ok = np.isfinite(preds['change'])
                r['auc_change'] = float(roc_auc_score(df.y.values[ok], preds['change'][ok]))
                out[f'{fam} | {clab} | {flab}'] = r
                print(fam, clab, flab, {k: round(r[k], 3) for k in ('I', 'I0', 'I*', 'G')}, flush=True)
    json.dump(out, open(os.path.join(m.RES, 'w3_4_metric_ext.json'), 'w'), indent=1, default=float)
    report_ext(out)                                   # same tables and reading rules as the original report


def report_ext(out):
    import io, contextlib
    tmp = os.path.join(m.RES, 'w3_4_metric.md')
    saved = open(tmp).read()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            m.report({k.replace('TESSERA', 'AlphaEarth').replace('Presto', 'Sentinel-2'): v for k, v in out.items()})
        txt = open(tmp).read()
    finally:
        open(tmp, 'w').write(saved)
    txt = txt.replace('## AlphaEarth', '## TESSERA (pre = 2018–2019)').replace('## Sentinel-2', '## Presto (seasons October–September; pre = 2018–2019)')
    txt = txt.replace('Reading (AlphaEarth,', 'Reading (TESSERA,').replace('Reading (Sentinel-2,', 'Reading (Presto,')
    txt = txt.replace('# W3-4: a placebo-adjusted detection metric', '# W3-4 addendum: the metric with TESSERA and Presto')
    txt = txt.replace('Protocol: [w3_4_metric_protocol.md](w3_4_metric_protocol.md), written before any model.',
                      'Protocol: [w3_4_metric_protocol.md](w3_4_metric_protocol.md) and its addendum of 18 October 2026, written before '
                      'extraction. Pre-entry record 2018–2019 for both (TESSERA has no 2017); I₀ from 2020 (Presto: season October 2019–September 2020).')
    open(os.path.join(m.RES, 'w3_4_metric_ext.md'), 'w').write(txt)
    print(txt)


if __name__ == '__main__':
    main()

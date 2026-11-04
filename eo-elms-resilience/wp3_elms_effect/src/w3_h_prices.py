"""W3-H: state the Step 3 contrasts in £/ha at Defra's average prices (protocol, record row of 4 November 2026).

Input   wp3_elms_effect/results/w3_h_harvest.json; data/raw/auk_2026/AUK-chapter7-20260709.ods (Agriculture in the UK, Tables 7.2b, 7.3b)
Output  wp3_elms_effect/results/w3_h_harvest.md, .json: £/ha added
"""
import json, os
import numpy as np, pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
RES = os.path.join(ROOT, 'wp3_elms_effect', 'results')
SEASONS = range(2021, 2026)


def prices():
    x = pd.ExcelFile(os.path.join(ROOT, 'data', 'raw', 'auk_2026', 'AUK-chapter7-20260709.ods'), engine='odf')
    out = {}
    for sheet, names in (('Table_7_2', ('Milling wheat', 'Feed wheat')), ('Table_7_3', ('Malting barley', 'Feed barley'))):
        w = x.parse(sheet, header=None)
        h = next(i for i in range(len(w)) if str(w.iloc[i, 0]).strip() == 'Type')
        yrs = {int(str(v)[:4]): c for c, v in enumerate(w.iloc[h]) if str(v)[:4].isdigit()}
        for i in range(h + 1, h + 3):
            name = str(w.iloc[i, 0]).strip()
            assert name in names, name
            out[name] = {y: float(w.iloc[i, yrs[y]]) for y in SEASONS}
    return out


def main():
    p = prices()
    path = os.path.join(RES, 'w3_h_harvest.json')
    o = json.load(open(path))
    feed = float(np.mean(list(p['Feed wheat'].values())))
    allp = [v for s in p.values() for v in s.values()]
    rows = []
    for r in o['step3']['rows']:
        if r['decides']:
            a = r['frozen']
            rows.append(dict(family=r['family'], gbp_ha=a['est'] * feed, lo=a['lo'] * feed, hi=a['hi'] * feed, cheapest=a['est'] * min(allp), dearest=a['est'] * max(allp)))
    o['step3']['prices'] = dict(gbp_per_t=p, feed_wheat_mean=feed, rows=rows)
    json.dump(o, open(path, 'w'), indent=1, default=float)
    L = ['- **£/ha:** the t/ha contrast times Defra\'s mean UK feed wheat price for 2021–2025, '
         f'£{feed:.0f}/t (*Agriculture in the UK*, sales-weighted; 2025 provisional). Across all crop prices in those seasons, £{min(allp):.0f}–£{max(allp):.0f}/t. Revenue only; costs are not counted.', '',
         '| Family | £/ha (95% interval) | At lowest and highest price |', '|---|---|---|']
    for x in rows:
        L.append(f"| {x['family']} | {x['gbp_ha']:+.1f} ({x['lo']:+.1f}, {x['hi']:+.1f}) | {x['cheapest']:+.1f} to {x['dearest']:+.1f} |")
    m = os.path.join(RES, 'w3_h_harvest.md')
    s = open(m).read()
    old = "- **£/ha: not stated yet.** Defra's farm-gate price series is not held locally.\n"
    if old in s:
        a, b = s.split(old)
        open(m, 'w').write(a.rstrip('\n') + '\n\n' + b.rstrip('\n') + '\n\n### £/ha\n\n' + '\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

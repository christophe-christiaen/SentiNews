"""Score the 2026 nowcast (results/wp1_nowcast_2026.csv, commit 8427362, written 11 October 2026 without looking at
any official figure) against Defra's provisional 2026 regional yields, published 8 October 2026
(UK-cops-webseries_261008.ods). Also scores the spring barley re-issue (wp1_nowcast_2026_grainfill.csv).

Output  wp1_regional_signal/results/wp1_score_2026.md, wp1_score_2026.csv
"""
import os, re
import numpy as np, pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
RES = os.path.join(ROOT, 'wp1_regional_signal', 'results')
ODS = os.path.join(ROOT, 'data', 'raw', 'defra_cops_2026', 'UK-cops-webseries_261008.ods')
SHEETS = {'wheat': 'Regional_wheat', 'winter barley': 'Regional_winter_barley', 'spring barley': 'Regional_spring_barley'}
REGIONS = ['North East', 'North West and Merseyside', 'Yorkshire & The Humber', 'East Midlands', 'West Midlands',
           'Eastern', 'South East and London', 'South West']


def actual():
    x = pd.ExcelFile(ODS, engine='odf'); rows = []
    for crop, sh in SHEETS.items():
        d = pd.read_excel(x, sh, header=None)
        hr = next(i for i in range(len(d)) if str(d.iloc[i, 0]).strip().startswith('Yields'))
        col = next(c for c in range(1, d.shape[1]) if re.fullmatch(r'2026(\.0)?(\(\d\))?', str(d.iloc[hr, c]).strip()))
        for r in range(hr + 1, hr + 14):
            name = str(d.iloc[r, 0]).strip()
            if name in REGIONS + ['England']:
                rows.append(dict(crop=crop, region=name, actual=float(d.iloc[r, col])))
    return pd.DataFrame(rows)


def main():
    a = actual()
    first = pd.read_csv(os.path.join(RES, 'wp1_nowcast_2026.csv')).assign(version='first nowcast (11 Oct)')
    gf = pd.read_csv(os.path.join(RES, 'wp1_nowcast_2026_grainfill.csv')).assign(version='spring barley re-issue (12 Oct)')
    n = pd.concat([first, gf], ignore_index=True).merge(a, on=['crop', 'region'])
    n['error'] = n.nowcast_t_ha - n.actual
    n['in80'] = n.actual.between(n.lo80, n.hi80)
    n['in90'] = np.where(n.lo90.notna(), n.actual.between(n.lo90, n.hi90), np.nan)
    n['abs_error'] = n.error.abs()
    n['direction_ok'] = np.sign(n.nowcast_t_ha - n.mean_2017_2025) == np.sign(n.actual - n.mean_2017_2025)
    n.round(3).to_csv(os.path.join(RES, 'wp1_score_2026.csv'), index=False)
    eng = a[a.region == 'England'].set_index('crop').actual
    g = n.groupby(['version', 'crop', 'cutoff'])
    s = pd.DataFrame({'mean error': g.error.mean(), 'mean abs. error': g.abs_error.mean(), 'in 80% interval': g.in80.mean(),
                      'in 90% interval': g.in90.mean(), 'direction vs mean right': g.direction_ok.mean(),
                      'nowcast, mean of regions': g.nowcast_t_ha.mean(), 'actual, mean of regions': g.actual.mean()})
    L = ['# Scoring the 2026 nowcast against Defra\'s provisional figures', '',
         'Nowcast written 11 October 2026 (commit 8427362) **without looking at** Defra\'s provisional 2026 estimates; '
         'note those were **already published on 8 October 2026**, three days earlier, so this is a blind forecast, not '
         'a forecast made before publication. Defra figures from UK-cops-webseries_261008.ods.', '',
         '## Summary (8 English regions)', '', s.round(2).to_markdown(), '',
         'England (Defra, area-weighted): ' + ', '.join(f'{c} {v:.2f} t/ha' for c, v in eng.items()) + '.', '',
         '## By region', '',
         '| Version | crop | cutoff | region | nowcast | 80% interval | Defra 2026 | error |', '|---|---|---|---|---|---|---|---|'] + \
        [f'| {r.version} | {r.crop} | {r.cutoff} | {r.region} | {r.nowcast_t_ha:.2f} | {r.lo80:.2f}–{r.hi80:.2f} | {r.actual:.2f} | {r.error:+.2f} |'
         for r in n.itertuples()]
    open(os.path.join(RES, 'wp1_score_2026.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L[:14 + len(s)]))


if __name__ == '__main__':
    main()

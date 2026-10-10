"""Back-test of satellite-targeted outreach: if a relationship team contacted only the sites flagged by this year's
stress signals, how much of next year's trouble would they have reached?

No model is fitted: sites are ranked within each year by current stress S(t) or stress debt D(t), and the top 20% are
flagged. Targets at t+1: (a) bottom 20% of sites that year (relative hit), (b) a shock, S <= -1 SD (absolute),
(c) among sites in shock at t, still unrecovered at t+1 (S < -0.5). Sites are the 50 pilot windows, not farms.
"""
import json, os
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'results', 'outreach')
FLAG = 0.2


def main():
    d = pd.read_csv(os.path.join(ROOT, 'results', 'cumulative', 'site_stress_index.csv'))
    d = d[d.year <= 2026].sort_values(['region', 'site', 'year'])
    g = d.groupby(['region', 'site'])
    d['S_next'], d['year_next'] = g.S.shift(-1), g.year.shift(-1)
    d = d[d.year_next == d.year + 1].copy()
    d['bottom_next'] = d.groupby('year').S_next.rank(pct=True) <= FLAG
    d['shock_next'] = d.S_next <= -1.0
    res = {'n_site_years': len(d), 'years': [int(d.year.min()), int(d.year.max())], 'flag_share': FLAG, 'by_signal': {}}
    for sig, col in (('Current stress S(t)', 'S'), ('Stress debt D(t)', 'D')):
        d['flag'] = d.groupby('year')[col].rank(pct=True, method='first') <= FLAG   # most negative = top risk
        prec = d.loc[d.flag, 'bottom_next'].mean()
        rec_shock = d.loc[d.shock_next, 'flag'].mean()
        sh = d[d.S <= -1.0]
        auc_unrec = roc_auc_score(sh.S_next < -0.5, -sh[col]) if sh[col].nunique() > 1 else np.nan
        res['by_signal'][sig] = dict(
            precision_bottom20_next=round(prec, 3), lift=round(prec / FLAG, 2),
            share_of_next_year_shocks_reached=round(rec_shock, 3), shocks_next=int(d.shock_next.sum()),
            auc_unrecovered_after_shock=round(auc_unrec, 3), n_shocked=len(sh),
            # within-year AUC for next year's relative position (averaged over years)
            auc_bottom20_next=round(np.nanmean([roc_auc_score(x.bottom_next, -x[col]) for _, x in d.groupby('year')
                                                if x.bottom_next.nunique() > 1]), 3))
    # current list: sites flagged by 2026 debt
    last = pd.read_csv(os.path.join(ROOT, 'results', 'cumulative', 'site_stress_index.csv'))
    last = last[last.year == last.year.max()]
    k = int(round(FLAG * len(last)))
    top = last.nsmallest(k, 'D')
    res['flagged_now'] = dict(year=int(last.year.max()), n=k, by_region=top.region.value_counts().to_dict())
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, 'outreach_backtest.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()


def triage():
    """After a shock (S <= -1 in year t), rank shocked sites by stress debt; how well does the top half pick out those
    still unrecovered next year?"""
    d = pd.read_csv(os.path.join(ROOT, 'results', 'cumulative', 'site_stress_index.csv')).sort_values(['region', 'site', 'year'])
    d['S_next'] = d.groupby(['region', 'site']).S.shift(-1)
    sh = d[(d.S <= -1.0) & d.S_next.notna()].copy()
    sh['unrec'] = sh.S_next < -0.5
    out = dict(n_shocked=len(sh), base_rate_unrecovered=round(sh.unrec.mean(), 3))
    for col, name in (('S', 'current_stress'), ('D', 'stress_debt')):
        sh['top'] = sh.groupby('year')[col].rank(pct=True, method='first') <= 0.5
        out[name] = dict(precision_top_half=round(sh.loc[sh.top, 'unrec'].mean(), 3),
                         precision_bottom_half=round(sh.loc[~sh.top, 'unrec'].mean(), 3),
                         share_unrecovered_in_top_half=round(sh.loc[sh.unrec, 'top'].mean(), 3))
    res = json.load(open(os.path.join(OUT, 'outreach_backtest.json')))
    res['triage_after_shock'] = out
    json.dump(res, open(os.path.join(OUT, 'outreach_backtest.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    triage()

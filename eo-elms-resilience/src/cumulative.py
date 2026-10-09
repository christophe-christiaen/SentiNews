"""Cumulative and compound shocks (reviewer comment: some regions bounced back,
others were hit again before they could recover).

Stress index S (per site-year): mean of the peak-season and July NDVI anomalies,
each a z-score against the site's own 2001-2015 baseline, averaged over the
site's cropland and grassland masks. Region S = mean of its sites.

  shock          S <= -1.0
  recovered      S >= -0.5
  compound hit   a shock in year t when S(t-1) < -0.5 (land not yet recovered)
  stress debt    D(t) = 0.5 * D(t-1) + min(S(t), 0)   (half of a deficit carries over)
  episode        consecutive years with S < -0.5 containing at least one shock

Typology over 2016-2026 (precedence top to bottom):
  persistent stress   an episode lasting >= 3 years (never back to normal)
  back-to-back hits   shocks in two consecutive years
  slow recovery       an episode lasting 2 years with a single shock
  bounced back        every shock recovered the next year
  little affected     no shock

Tests (site level, 50 sites x 2002-2026, standard errors clustered by site):
  T1 legacy      S(t) ~ S(t-1) + year FE           (do deficits persist beyond the common weather?)
  T2 compound    in national shock years, S(t) ~ S(t-1) + year FE   (are unrecovered sites hit harder?)
  T3 rebound     S(t+1) - S(t) ~ D(t-1) + S(t) + year FE, shock years (does debt slow rebound?)
  T4 AR1         lag-1 autocorrelation of region S, 2002-2013 vs 2014-2026 (rising = slower recovery)
"""
import json, os, warnings, numpy as np, pandas as pd, statsmodels.formula.api as smf
warnings.filterwarnings('ignore')
ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'results', 'cumulative'); os.makedirs(OUT, exist_ok=True)
SHOCK, RECOV, LAM, BASE = -1.0, -0.5, 0.5, 2015

def stress_index(nd):
    nd = nd.copy()
    for col in ('peak', 'july'):
        def z(g):
            b = g[g.year <= BASE][col]; return (g[col] - b.mean()) / b.std()
        nd[col + '_z'] = nd.groupby(['region', 'site', 'cover'], group_keys=False).apply(z)
    nd['S'] = nd[['peak_z', 'july_z']].mean(axis=1)
    return nd.groupby(['region', 'site', 'year']).S.mean().reset_index()

def debt(s):
    d, out = 0.0, []
    for v in s:
        d = LAM * d + min(v, 0.0); out.append(d)
    return np.array(out)

def episodes(years, s):
    eps, cur = [], []
    for y, v in zip(years, s):
        if v < RECOV: cur.append((y, v))
        else:
            if cur: eps.append(cur); cur = []
    if cur: eps.append(cur)
    return [e for e in eps if min(v for _, v in e) <= SHOCK]

def profile(g, start=2016):
    g = g.sort_values('year'); yrs, s = g.year.values, g.S.values
    ev = []
    for k in range(1, len(yrs)):
        if s[k] <= SHOCK:
            rec = next((yrs[j] - yrs[k] for j in range(k + 1, len(yrs)) if s[j] >= RECOV), None)
            ev.append(dict(year=int(yrs[k]), S=s[k], prior=s[k - 1], compound=bool(s[k - 1] < RECOV),
                           recovery_years=rec, censored=rec is None))
    eps = [e for e in episodes(yrs, s) if e[-1][0] >= start]
    lens = [len(e) for e in eps]
    shock_years = {y for e in eps for y, v in e if v <= SHOCK}
    b2b = any(y - 1 in shock_years for y in shock_years)
    if any(L >= 3 for L in lens): typ = 'Persistent stress'
    elif b2b: typ = 'Back-to-back hits'
    elif any(L == 2 for L in lens): typ = 'Slow recovery'
    elif eps: typ = 'Bounced back'
    else: typ = 'Little affected'
    return ev, eps, typ

def main():
    nd = pd.read_csv(os.path.join(ROOT, 'data/processed/ndvi_site_year.csv'))
    site = stress_index(nd)
    site['D'] = site.sort_values('year').groupby(['region', 'site']).S.transform(lambda s: debt(s.values))
    site = site.sort_values(['region', 'site', 'year'])
    reg = site.groupby(['region', 'year']).S.mean().reset_index()
    reg['D'] = reg.groupby('region').S.transform(lambda s: debt(s.values))
    site.to_csv(f'{OUT}/site_stress_index.csv', index=False); reg.to_csv(f'{OUT}/region_stress_index.csv', index=False)
    out = {'definitions': dict(shock=SHOCK, recovered=RECOV, carryover=LAM, baseline=f'2001-{BASE}')}

    # regional events, episodes, typology
    rows, ev_rows = [], []
    for r, g in reg.groupby('region'):
        ev, eps, typ = profile(g)
        for e in ev: ev_rows.append(dict(region=r, **e))
        rows.append(dict(region=r, typology=typ, shocks_2016_2026=sum(e['year'] >= 2016 for e in ev),
                         compound_hits=sum(e['compound'] and e['year'] >= 2016 for e in ev),
                         longest_episode=max([len(e) for e in eps], default=0),
                         episode_years=';'.join(f'{e[0][0]}-{e[-1][0]}' for e in eps),
                         peak_debt=round(g.D.min(), 2), peak_debt_year=int(g.loc[g.D.idxmin(), 'year']),
                         debt_2026=round(g[g.year == 2026].D.iloc[0], 2)))
    rt = pd.DataFrame(rows).sort_values('debt_2026'); rt.to_csv(f'{OUT}/region_typology.csv', index=False)
    pd.DataFrame(ev_rows).to_csv(f'{OUT}/region_shock_events.csv', index=False)
    out['region_typology'] = rt.to_dict('records')
    # site typology
    st = []
    for (r, i), g in site.groupby(['region', 'site']):
        ev, eps, typ = profile(g); st.append(dict(region=r, site=i, typology=typ, debt_2026=g[g.year == 2026].D.iloc[0],
                                                  compound_hits=sum(e['compound'] and e['year'] >= 2016 for e in ev)))
    st = pd.DataFrame(st); st.to_csv(f'{OUT}/site_typology.csv', index=False)
    out['site_typology_counts'] = st.typology.value_counts().to_dict()

    # statistical tests
    p = site.sort_values(['region', 'site', 'year']).copy()
    p['uid'] = p.region + '_' + p.site.astype(str)
    p['S_lag'] = p.groupby('uid').S.shift(1); p['D_lag'] = p.groupby('uid').D.shift(1)
    p['S_next'] = p.groupby('uid').S.shift(-1)
    p = p.dropna(subset=['S_lag'])
    cl = lambda d: dict(cov_type='cluster', cov_kwds={'groups': pd.factorize(d.uid)[0]})
    m1 = smf.ols('S ~ S_lag + C(year)', p).fit(**cl(p))
    nat = p.groupby('year').S.mean(); shock_years = [int(y) for y in nat[nat <= SHOCK].index]
    q = p[p.year.isin(shock_years)]
    m2 = smf.ols('S ~ S_lag + C(year)', q).fit(**cl(q))
    r_ = p[p.year.isin(shock_years)].dropna(subset=['S_next', 'D_lag']).copy(); r_['rebound'] = r_.S_next - r_.S
    m3 = smf.ols('rebound ~ D_lag + S + C(year)', r_).fit(**cl(r_))
    out['tests'] = dict(
        national_shock_years=shock_years,
        T1_legacy=dict(n=int(m1.nobs), coef=m1.params['S_lag'], p=m1.pvalues['S_lag']),
        T2_unrecovered_hit_harder=dict(n=int(m2.nobs), coef=m2.params['S_lag'], p=m2.pvalues['S_lag'],
            note='+1 SD better pre-shock state -> coef SD better state in the shock year'),
        T3_debt_slows_rebound=dict(n=int(m3.nobs), coef=m3.params['D_lag'], p=m3.pvalues['D_lag'],
            note='positive coef: more debt (more negative D) -> smaller rebound'))
    ar = {}
    for r, g in reg.groupby('region'):
        g = g.set_index('year').S
        a1 = g.loc[2002:2013]; a2 = g.loc[2014:2026]
        ar[r] = dict(early=round(a1.autocorr(1), 2), late=round(a2.autocorr(1), 2))
    out['T4_AR1_by_region'] = ar
    json.dump(out, open(f'{OUT}/cumulative_results.json', 'w'), indent=2, default=float)
    print(json.dumps({k: out[k] for k in ('tests', 'site_typology_counts', 'T4_AR1_by_region')}, indent=1, default=lambda x: round(float(x), 3)))
    print(rt.to_string(index=False))

if __name__ == '__main__':
    main()

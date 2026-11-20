"""W3-E: payments, income and output from published Farm Business Survey aggregates (descriptive).
Protocol: wp3_elms_effect/results/w3_e_fbs_payments_protocol.md. Data: FBS, Defra, OGL v3.0.

Output  wp3_elms_effect/results/w3_e_fbs_payments.md, .json
"""
import json, os
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
D = os.path.join(ROOT, 'shared', 'data', 'fbs')
RES = os.path.join(ROOT, 'wp3_elms_effect', 'results')
FILES = {'DP': 'fbs_direct_payments_per_ha_by_type.csv', 'AE': 'fbs_agrienv_payments_per_ha_by_type.csv',
         'FBI': 'fbs_farm_business_income_per_ha_by_type.csv', 'OUT': 'fbs_output_per_ha_by_region.csv'}
NARR = ['All', 'Cereals', 'General cropping', 'Dairy', 'LFA Grazing Livestock', 'Lowland Grazing Livestock', 'Mixed']
OTHER = ['Horticulture', 'Pigs', 'Poultry']
T_TYP = {'SGM': 0, '2007': 1, '2010': 2, '2013': 3, '2017': 4}


def load(k):
    d = pd.read_csv(os.path.join(D, FILES[k]), dtype={'Typology': str})
    d['rank'] = d.Typology.map(T_TYP)
    dup = d.groupby(['Year', 'Level']).Typology.nunique()
    overlap = {}
    for (y, lev), n in dup[dup > 1].items():
        g = d[(d.Year == y) & (d.Level == lev)].sort_values('rank')
        overlap.setdefault(int(y), {})[lev] = float(g.Value.iloc[-1] - g.Value.iloc[0])
    d = d.sort_values('rank').groupby(['Year', 'Level']).tail(1)
    return d.set_index(['Year', 'Level']), overlap


def main():
    S, OV = {}, {}
    for k in FILES:
        S[k], OV[k] = load(k)
    v = lambda k, y, lev: float(S[k].loc[(y, lev), 'Value'])
    ci = lambda k, y, lev: float(S[k].loc[(y, lev), 'Confidence interval'])
    years = sorted({y for y, _ in S['DP'].index})
    types = NARR + OTHER
    series = {lev: {int(y): dict(DP=v('DP', y, lev), AE=v('AE', y, lev), FBI=v('FBI', y, lev),
                                 FBI_ci=ci('FBI', y, lev), AE_ci=ci('AE', y, lev), DP_ci=ci('DP', y, lev))
                    for y in years} for lev in types}
    for lev in types:
        for y, r in series[lev].items():
            r['PAY'] = r['DP'] + r['AE']
            r['share'] = r['PAY'] / r['FBI'] if r['FBI'] > 0 else None
    for y in years:
        series['All'][int(y)]['OUT'] = v('OUT', y, 'All')
        series['All'][int(y)]['AE_over_OUT'] = series['All'][int(y)]['AE'] / series['All'][int(y)]['OUT']
    change = {lev: {k: series[lev][2024][k] - series[lev][2019][k] for k in ('DP', 'AE', 'PAY', 'FBI')} for lev in types}
    out = dict(source='Farm Business Survey, Defra (OGL v3.0); real prices, GBP per hectare', typology_overlap_differences=OV,
               series=series, change_2019_20_to_2024_25=change,
               scale=dict(harvest_t_ha=0.04, price_gbp_t=[150, 250], gbp_ha=[0.04 * 150, 0.04 * 250]))
    json.dump(out, open(os.path.join(RES, 'w3_e_fbs_payments.json'), 'w'), indent=1)

    sy = lambda y: f'{y}/{str(y + 1)[2:]}'
    L = ['# W3-E: payments, income and output (Farm Business Survey aggregates, descriptive)', '',
         'Protocol: [w3_e_fbs_payments_protocol.md](w3_e_fbs_payments_protocol.md). Source: Farm Business Survey, Defra, '
         'Open Government Licence v3.0. England, real prices, £ per hectare; newer farm-type classification in overlap years.', '',
         '## All farms', '', '| Year | Direct payments | Agri-environment | Combined | Farm business income (±CI) | Payments ÷ income | Agri-env ÷ output |',
         '|---|---|---|---|---|---|---|']
    for y in range(2015, 2025):
        r = series['All'][y]
        L.append(f"| {sy(y)} | {r['DP']:.0f} | {r['AE']:.0f} | {r['PAY']:.0f} | {r['FBI']:.0f} (±{r['FBI_ci']:.0f}) | {r['share']:.0%} | {r['AE_over_OUT']:.1%} |")
    L += ['', '## By farm type, 2019/20 → 2024/25', '',
          '| Farm type | Direct payments | Agri-environment | Combined | Income 2024/25 (±CI) | Payments ÷ income 2019/20 | 2021/22 | 2023/24 | 2024/25 |',
          '|---|---|---|---|---|---|---|---|---|']
    f = lambda s: '—' if s is None else f'{s:.0%}'
    for lev in types:
        a, b = series[lev][2019], series[lev][2024]
        L.append(f"| {lev}{' *' if lev in OTHER else ''} | {a['DP']:.0f} → {b['DP']:.0f} | {a['AE']:.0f} → {b['AE']:.0f} | {a['PAY']:.0f} → {b['PAY']:.0f} | "
                 f"{b['FBI']:.0f} (±{b['FBI_ci']:.0f}) | {f(a['share'])} | {f(series[lev][2021]['share'])} | {f(series[lev][2023]['share'])} | {f(b['share'])} |")
    c = change['All']
    L += ['', '\\* tabulated, not discussed (protocol rule 3).', '',
          f"All farms, 2019/20 → 2024/25: direct payments {c['DP']:+.0f}, agri-environment {c['AE']:+.0f}, combined {c['PAY']:+.0f} £/ha "
          f"({c['PAY'] / series['All'][2019]['PAY']:+.0%}).", '',
          f"**Scale (illustrative, assumed prices):** a harvest difference of 0.04 t/ha at £150–250/t is £{0.04 * 150:.0f}–{0.04 * 250:.0f} per hectare.", '',
          'Payments ÷ income is a ratio of published means, shown without an interval. Agri-environment payments are gross. '
          'Averages include non-participants; nothing here is linked to scheme fields.', '',
          '## Classification overlaps (newer minus older, All farms)', '']
    for k in ('DP', 'AE', 'FBI'):
        L.append(f"- {k}: " + ', '.join(f"{sy(y)} {d.get('All', 0):+.0f}" for y, d in sorted(OV[k].items())))
    open(os.path.join(RES, 'w3_e_fbs_payments.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

"""Stage 0: check the spatial agreement groups against Defra's farm and land payment register.

The register names every business that received >= GBP 1,250 of scheme payments in a financial year (SFI, CS, grants),
with its postcode district (e.g. NG32). A company found there with SFI or CS payments certainly holds an agreement, so
the match is independent evidence for the 500 m spatial link, and shows how many 'no agreement' farms are misclassed.

Matching: company names and payee names are normalised (case, punctuation, legal suffixes, '&' -> 'and'), blocked on
postcode district, then matched exactly or by fuzzy token-sort ratio >= FUZZY within the same district.

Input   shared/data/farms/farms_all.csv, shared/data/farms/farm_schemes.csv (if present)
        shared/data/reference/payments/ffc-payment-data.csv  (find-farm-and-land-payment-data.defra.gov.uk, OGL)
Output  shared/data/farms/farm_payments.csv          per company: matched payee, schemes, years, amounts (private)
        shared/data/farms/farm_groups.csv            final analysis groups (agreement / no agreement / uncertain)
        shared/results/payment_check_summary.md      counts only (safe to commit)
"""
import os, re
import pandas as pd
from rapidfuzz import fuzz, process

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
PAY = os.path.join(D, 'reference', 'payments', 'ffc-payment-data.csv')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 'payment_check_summary.md')
FUZZY = 92
AGRI_ENV = {'Sustainable Farming Incentive', 'Countryside Stewardship'}
SUFFIX = re.compile(r'\b(LIMITED|LTD|LLP|PLC|CO|COMPANY|THE|T/A.*|TRADING AS.*)\b')


def norm(s):
    s = str(s).upper().replace('&', ' AND ')
    s = SUFFIX.sub(' ', s)
    s = re.sub(r'[^A-Z0-9 ]', ' ', s)
    return ' '.join(s.split())


def district(pc):
    return str(pc).upper().split()[0] if isinstance(pc, str) and pc.strip() else None


def main():
    pay = pd.read_csv(PAY, dtype=str, on_bad_lines='skip')
    pay['amount'] = pd.to_numeric(pay.amount, errors='coerce')
    pay['district'] = pay.part_postcode.str.upper().str.strip()
    pay['key'] = pay.payee_name.map(norm)
    payees = pay.groupby(['district', 'key', 'payee_name']).agg(
        schemes=('scheme', lambda s: ';'.join(sorted(set(s)))), years=('financial_year', lambda s: ';'.join(sorted(set(s)))),
        amount=('amount', 'sum'), agri_env=('scheme', lambda s: bool(set(s) & AGRI_ENV))).reset_index()

    farms = pd.read_csv(os.path.join(D, 'farms', 'farms_all.csv'), dtype={'company_number': str})
    farms = farms[farms.country == 'England'].copy()
    farms['district'] = farms.postcode.map(district)
    farms['key'] = farms.company_name.map(norm)

    by_d = {k: g for k, g in payees.groupby('district')}
    rows = []
    for r in farms.itertuples():
        g = by_d.get(r.district)
        hit, how, score = None, 'none', None
        if g is not None:
            ex = g[g.key == r.key]
            if len(ex):
                hit, how, score = ex.iloc[0], 'exact', 100
            else:
                m = process.extractOne(r.key, g.key.tolist(), scorer=fuzz.token_sort_ratio, score_cutoff=FUZZY)
                if m:
                    hit, how, score = g.iloc[m[2]], 'fuzzy', round(m[1], 1)
        rows.append(dict(farm_id=r.farm_id, match=how, score=score,
                         payee_name=None if hit is None else hit.payee_name,
                         pay_schemes=None if hit is None else hit.schemes, pay_years=None if hit is None else hit.years,
                         pay_amount=None if hit is None else round(hit.amount, 2),
                         pay_agri_env=False if hit is None else bool(hit.agri_env)))
    m = pd.DataFrame(rows)
    m.to_csv(os.path.join(D, 'farms', 'farm_payments.csv'), index=False)

    out = farms[['farm_id', 'address_kind']].merge(m, on='farm_id')
    lines = ['# Stage 0 · Payment register check (counts only)', '',
             f'- Payment register: {len(pay):,} payment rows, {pay.payee_name.nunique():,} payees, years '
             f'{", ".join(sorted(pay.financial_year.dropna().unique()))}; schemes: ' +
             ', '.join(f'{k} ({v:,})' for k, v in pay.scheme.value_counts().items()),
             f'- English companies matched to a payee in the same postcode district: {(m.match != "none").sum():,} of {len(m):,} '
             f'({(m.match != "none").mean():.1%}; exact {(m.match == "exact").sum():,}, fuzzy {(m.match == "fuzzy").sum():,})',
             f'- Of those, with SFI or CS payments: {m.pay_agri_env.sum():,}', '']
    fs = os.path.join(D, 'farms', 'farm_schemes.csv')
    if os.path.exists(fs):
        g = pd.read_csv(fs, usecols=['farm_id', 'group']).merge(m, on='farm_id')
        tab = pd.crosstab(g.group, g.pay_agri_env.map({True: 'paid SFI/CS', False: 'not in register'}), margins=True)
        # final analysis groups: register evidence first, spatial link second; nothing is forced
        g['group_final'] = 'uncertain'
        # register-confirmed only: spatial links alone proved weak (only ~40% confirmed even within 300 m),
        # so spatial-only farms stay 'uncertain' and are used only in sensitivity checks
        g.loc[g.pay_agri_env, 'group_final'] = 'agreement'
        g.loc[~g.pay_agri_env & (g.group == 'no agreement'), 'group_final'] = 'no agreement'
        g.loc[g.group == 'excluded (office address)', 'group_final'] = 'excluded (office address)'
        g['agreement_evidence'] = (g.pay_agri_env.map({True: 'register', False: ''}) + '+' +
                                   (g.group == 'agreement').map({True: 'spatial', False: ''})).str.strip('+')
        g[['farm_id', 'group', 'pay_agri_env', 'group_final', 'agreement_evidence']] \
            .to_csv(os.path.join(D, 'farms', 'farm_groups.csv'), index=False)
        fin = g[g.group_final != 'excluded (office address)']
        lines += ['## Final analysis groups', '', g.group_final.value_counts().rename_axis('').to_frame('farms').to_markdown(), '',
                  '- **agreement**: paid SFI or CS in the payment register (spatial-only links are uncertain); '
                  '**no agreement**: not in the register and no agreement assigned within 1 km; **uncertain**: the rest '
                  '(left out of both groups, incl. spatial-only links); office addresses excluded because the point does not locate the farm.',
                  '- Evidence for the agreement group: ' + ', '.join(
                      f'{k} {v:,}' for k, v in fin[fin.group_final == 'agreement'].agreement_evidence.value_counts().items()), '',
                  '## Spatial group vs payment register', '', tab.to_markdown(), '',
                  '- Share of the **agreement** group confirmed by SFI/CS payments: '
                  f'{g[g.group == "agreement"].pay_agri_env.mean():.0%}',
                  '- Share of the **no agreement** group that does receive SFI/CS payments (misclassed controls): '
                  f'{g[g.group == "no agreement"].pay_agri_env.mean():.0%}', '']
    lines += ['Caveats: the register covers only recent financial years and payments of GBP 1,250 or more, and a business '
              'may be paid under a trading or partner name, so "not in register" does not prove there is no agreement. '
              'ES (pre-2016) agreements are not in this register.']
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()

"""WP3 exploratory E4 (decisions record, 17 October 2026, specified before running): drought-season effects of the
two options visible from space (herbal leys, no-till) against management-only scheme land.

Groups among agreement fields: herbal leys (SAM3, CSAM3), no-till (SOH1; fields with both count as herbal leys),
management only (only SAM1, IPM, CIPM, NUM, CNUM, PRF options), other. H1 contrast per group against never-treated
fields on the embedding-matched sample (E3), frozen-plan estimator; key tests = herbal leys minus management-only and
no-till minus management-only. Within-cohort version with its before-entry placebo.

Output  wp3_elms_effect/results/wp3_e4_visible_options.md, .json
"""
import json, os, re
import numpy as np, pandas as pd
import wp3_did as w
import wp3_within_cohort as wc

LEYS, NOTILL = {'SAM3', 'CSAM3'}, {'SOH1'}
MGMT = {'SAM1', 'IPM2', 'IPM3', 'IPM4', 'CIPM2', 'CIPM3', 'CIPM4', 'NUM2', 'NUM3', 'CNUM2', 'CNUM3', 'PRF1', 'PRF2', 'PRF3', 'PRF4'}


def group(row):
    if row.G == 0:
        return 'never'
    c = set()
    for col in ('CS_land_codes', 'SFI_land_codes'):
        if isinstance(row[col], str):
            c |= {re.sub(r'_\d+$', '', x.strip()) for x in row[col].split(';') if x.strip()}
    if c & LEYS:
        return 'leys'
    if c & NOTILL:
        return 'notill'
    if c and c <= MGMT:
        return 'mgmt'
    return 'other'


def main():
    d = w.Data()
    t = d.t
    grp = t.apply(group, axis=1).values
    M = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet')).in_matched_sample.values
    counts = pd.Series(grp[M & (d.G > 0)]).value_counts().to_dict()
    w.log('groups in matched sample', counts)
    names = {'leys': 'herbal leys', 'notill': 'no-till', 'mgmt': 'management only', 'other': 'other options'}

    E = d.est('ndvi_july_z', pmask=M, fam=grp)
    TR = E.TR; post = (TR.e >= 0).values; sh = TR.shock.values
    def contrast(g):
        m = (TR.fam == g).values & post
        return E.weights(m & sh, m & ~sh)
    W = [contrast(g) for g in ('leys', 'notill', 'mgmt', 'other')]
    W += [W[0] - W[2], W[1] - W[2]]
    labels = ['herbal leys', 'no-till', 'management only', 'other options', 'herbal leys minus management only', 'no-till minus management only']
    th, V, G, _ = E.run(W)
    frozen = {lab: w.row(lab, th, V, k, G, int(TR.nT.values[(W[k] != 0) & (TR.fam.isin(['leys', 'notill', 'mgmt', 'other'])).values].sum()) if k < 4 else None)
              for k, lab in enumerate(labels)}

    Eu = d.est('ndvi_july_z', pmask=M, fam=grp, universal=True)
    TU = Eu.TR; e = TU.e.values; shu = TU.shock.values
    within = {}
    for win, wlab in ((e >= 0, 'after entry'), (np.isin(e, [-4, -3, -2]), 'before entry (placebo)')):
        vs = {}
        for g in ('leys', 'notill', 'mgmt'):
            m = (TU.fam == g).values & win
            vs[g], _ = wc.within(Eu, m & shu, m & ~shu, ['g'])
        Wu = [vs['leys'], vs['notill'], vs['mgmt'], vs['leys'] - vs['mgmt'], vs['notill'] - vs['mgmt']]
        thu, Vu, Gu, _ = Eu.run(Wu)
        within[wlab] = {lab: w.row(lab, thu, Vu, k, Gu) for k, lab in enumerate(['herbal leys', 'no-till', 'management only',
                                                                                    'herbal leys minus management only', 'no-till minus management only'])}
    out = {'matched_agreement_fields_by_group': {names.get(k, k): int(v) for k, v in counts.items()}, 'frozen_plan_estimator': frozen, 'within_cohort': within}
    json.dump(out, open(os.path.join(w.RES, 'wp3_e4_visible_options.json'), 'w'), indent=1, default=float)
    f = lambda r: f"{r['est']:+.3f} | {r['se']:.3f} | [{r['lo']:+.3f}, {r['hi']:+.3f}] | {r['p']:.3f}"
    L = ['# WP3 E4: drought-season effects of the options visible from space (exploratory)', '',
         'Specified in the decisions record before running. Embedding-matched sample (E3). H1 contrast = effect on July NDVI '
         'in shock seasons minus other seasons, against never-treated fields; SD of each field\'s 2017–2020 normal; SE '
         'clustered by ERA5 cell.', '',
         'Matched agreement fields: ' + ', '.join(f'{k} {v:,}' for k, v in out['matched_agreement_fields_by_group'].items()) + '.', '',
         '## Frozen-plan estimator', '', '| Group | estimate | SE | 95% CI | p |', '|---|---|---|---|---|'] + \
        [f'| {k} | {f(v)} |' for k, v in frozen.items()]
    for wl, r in within.items():
        L += ['', f'## Within cohort, {wl}', '', '| Group | estimate | SE | 95% CI | p |', '|---|---|---|---|---|'] + [f'| {k} | {f(v)} |' for k, v in r.items()]
    open(os.path.join(w.RES, 'wp3_e4_visible_options.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

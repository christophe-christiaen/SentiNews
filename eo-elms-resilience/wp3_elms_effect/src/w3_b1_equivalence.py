"""W3-B1 equivalence tests (protocol: w3_b1_equivalence_protocol.md): limits of 0.10 t/ha and 0.10 SD, on cell errors and on the shuffled-season
spread. Reproduces the permutation draws of w3_b1_inference.py exactly (same order of results, same seed) and saves them.

Input   as w3_b1_inference.py, plus results/w3_b1_inference.json
Output  wp3_elms_effect/results/w3_b1_equivalence.md, .json, w3_b1_equivalence_draws.json (aggregates only)
"""
import json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
from w3_z_partf import members
from w3_h_step3 import index_matrix

B, SEED = 1999, 20261105
S25, S26 = range(2017, 2026), range(2017, 2027)
LOSS, PRICE, NOTILL = 0.85, 204, 73
FREQ = dict(C=.47, D=.30)
# Placebo from each result's registered run: X2 and W3-B1 section 4 (A, B), w3_h_harvest.md (C), w3_z_partf_harvest.md (D), w3_z_partf.md (E)
PLACEBO = {'A: H1 July NDVI, frozen': ('+0.079 (+0.048, +0.110)', 'fails'), 'B: H1 July NDVI, E3 sample': ('+0.080 (+0.049, +0.111)', 'fails'),
           'C: dry or heat harvest, All agreement land': ('-0.081 (-0.162, +0.001)', 'passes narrowly'), 'C: dry or heat harvest, Management-only': ('-0.095 (-0.191, +0.001)', 'passes narrowly'),
           'D: wet-winter harvest, All agreement land': ('-0.128 (-0.194, -0.061)', 'fails'), 'D: wet-winter harvest, Management-only': ('-0.139 (-0.224, -0.054)', 'fails'),
           'D: wet-winter harvest, Buffer strips': ('-0.162 (-0.246, -0.078)', 'fails'), 'E: wet-winter July NDVI, All agreement land': ('-0.038 (-0.076, +0.000)', 'passes narrowly'),
           'E: wet-winter July NDVI, Buffer strips': ('-0.025 (-0.070, +0.020)', 'passes')}


def report():
    rows = json.load(open(os.path.join(w.RES, 'w3_b1_equivalence.json')))['rows']
    f = lambda c: f"({c['lo']:+.3f}, {c['hi']:+.3f}) {'pass' if c['passes'] else 'fail'}"
    L = ['# W3-B1 equivalence tests', '', 'Protocol: [w3_b1_equivalence_protocol.md](w3_b1_equivalence_protocol.md). Labels beside registered results; no registered reading changes. Exploratory. The limits were chosen after the estimates were public, anchored on numbers written earlier. Script reproduced the published estimates and permutation p values exactly.', '',
         '90% intervals. A result is within the limit only if both parts pass. X is the smallest effect ruled out, the larger of the two parts.', '',
         '| Result | Limit | Estimate | Cell errors | Shuffled-season spread | Reading | X | Placebo |', '|---|---:|---:|---|---|---|---:|---|']
    for r in rows:
        pl = PLACEBO[r['name']]
        read = "can't rule out" if not r['within_limit'] else ('within the limit, in a design that failed its placebo' if pl[1] == 'fails' else 'within the limit')
        L.append(f"| {r['name']} | {r['limit']:.2f} {r['unit']} | {r['est']:+.3f} | {f(r['cell'])} | {f(r['shuffled'])} | {read} | {r['X']:.3f} | {pl[0]}, {pl[1]} |")
    L += ['', '## Readings of X, harvest', '', '| Result | X, t/ha | £/ha in a shock season | Share of a bad season\'s loss (0.85 t/ha) | Share of the no-till payment, annualised |', '|---|---:|---:|---:|---:|']
    for r in rows:
        if 'readings' in r:
            q = r['readings']; L.append(f"| {r['name']} | {r['X']:.3f} | £{q['gbp_per_ha_shock_season']:.0f} | {q['share_of_bad_season_loss']:.0%} | {q['share_of_notill_payment_annualised']:.0%} |")
    L += ['', '## How to read this', '',
          '- **Three harvest results pass, and they are the ones with the weakest claim to be clean.** Equivalence measures noise around the estimate, not bias.',
          '- **Dry-or-heat placebos pass only narrowly and are themselves close to the limit** (-0.081 and -0.095 t/ha). Not a registered calculation: if a bias of that size carried into the contrast, the estimate would be about +0.12 to +0.14 t/ha, above the limit. So the pass is conditional on the placebo being noise.',
          '- **Wet-winter, all land, passes in a design that failed its placebo** (-0.128).',
          '- **HonestDiD isn\'t included:** at M̄ = 0.25 the 95% sets on the averages are (-0.032, +0.122) for dry or heat, all land, and (-0.101, +0.012) for wet, all land, both past the limit.',
          '- **The index isn\'t measured yield.** It is fitted to regional yields and tested only at regional level, and predictions of this kind can understate real differences between fields; this wasn\'t measured. If so, a limit in index t/ha is less demanding than the same limit in real t/ha.',
          '- **Centring:** using the raw draws instead of centred ones changes no pass or fail.']
    open(os.path.join(w.RES, 'w3_b1_equivalence.md'), 'w').write('\n'.join(L) + '\n')


def main():
    d = w.Data(); t = d.t
    pub = {x['name']: x for x in json.load(open(os.path.join(w.RES, 'w3_b1_inference.json')))['targets']}
    m0 = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet')).set_index('parcref').in_matched_sample
    M0 = m0.reindex(t.parcref).fillna(False).values.astype(bool)
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    ME = ms.in_matched_sample.values
    H, _ = index_matrix(t)
    Mem = members(t)
    main_sh = w.shock_table(**w.MAIN_SHOCK)
    wet_sh = w.shock_table(**w.MAIN_SHOCK); wet_sh['shock'] = wet_sh['wet']
    J = d.Y['ndvi_july_z']
    fam_of = lambda f: (np.where(Mem[f], 'F', 'O'), True) if f != 'All agreement land' else (d.fam, False)
    def T(name, Y, pm, f, sh, sn, use_crop, lim, unit): return dict(name=name, Y=Y, pm=pm, f=f, sh=sh, sn=sn, use_crop=use_crop, lim=lim, unit=unit)
    targets = [T('A: H1 July NDVI, frozen', J, M0, 'All agreement land', main_sh, S25, True, .10, 'SD'), T('B: H1 July NDVI, E3 sample', J, ME, 'All agreement land', main_sh, S25, True, .10, 'SD')]
    targets += [T(f'C: dry or heat harvest, {f}', H, ME, f, main_sh, S25, False, .10, 't/ha') for f in ('All agreement land', 'Management-only')]
    targets += [T(f'D: wet-winter harvest, {f}', H, ME, f, wet_sh, S25, False, .10, 't/ha') for f in ('All agreement land', 'Management-only', 'Buffer strips')]
    targets += [T(f'E: wet-winter July NDVI, {f}', J, ME, f, wet_sh, S26, False, .10, 'SD') for f in ('All agreement land', 'Buffer strips')]

    rng = np.random.default_rng(SEED)
    res, saved = [], {}
    for x in targets:
        fam, sel = fam_of(x['f'])
        TR0, CO = w.blocks(x['Y'], d.G, d.cell, d.crop, x['use_crop'], list(x['sn']), fam, x['pm'], None, False)
        E = w.Est(w.attach_shocks(TR0, d.cells, x['sh']), CO, d.cluster)
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        sk, nT, tau, cell = TR.shock.values, TR.nT.values, TR.tau_sum.values, TR.cell.values
        W = E.weights(p & sk, p & ~sk)
        th0 = float((W * tau).sum())
        _, V, _, _ = E.run([W], clusters=E.clu)
        se = float(np.sqrt(V[0, 0]))
        sn = list(x['sn'])
        SH = x['sh'].shock.reindex(pd.MultiIndex.from_product([d.cells, sn])).fillna(False).values.reshape(len(d.cells), len(sn)).astype(bool)
        tix = TR.t.values - sn[0]; draws = []
        for _ in range(B):
            pi = rng.permutation(len(sn)); s2 = SH[cell, pi[tix]]
            a, b = p & s2, p & ~s2
            if not a.any() or not b.any(): continue
            draws.append(tau[a].sum() / nT[a].sum() - tau[b].sum() / nT[b].sum())
        draws = np.array(draws); pperm = float((1 + (np.abs(draws) >= abs(th0)).sum()) / (1 + len(draws)))
        q = pub[x['name']]
        assert abs(th0 - q['est']) < 1e-9, (x['name'], th0, q['est'])
        assert pperm == q['permutation']['p'], (x['name'], pperm, q['permutation']['p'])
        D = draws - draws.mean()
        c1 = (th0 - 1.645 * se, th0 + 1.645 * se)
        c2 = (th0 + float(np.quantile(D, .05)), th0 + float(np.quantile(D, .95)))
        ins = lambda c: bool(-x['lim'] < c[0] and c[1] < x['lim'])
        x1, x2 = max(map(abs, c1)), max(map(abs, c2))
        r = dict(name=x['name'], est=th0, limit=x['lim'], unit=x['unit'], cell=dict(se=se, lo=c1[0], hi=c1[1], passes=ins(c1), smallest_ruled_out=x1),
                 shuffled=dict(sd=float(draws.std(ddof=1)), mean_of_draws=float(draws.mean()), q05=float(np.quantile(D, .05)), q95=float(np.quantile(D, .95)), lo=c2[0], hi=c2[1], passes=ins(c2), smallest_ruled_out=x2, draws=len(draws)),
                 within_limit=ins(c1) and ins(c2), X=max(x1, x2))
        k = x['name'][0]
        if k in FREQ:
            r['readings'] = dict(share_of_bad_season_loss=r['X'] / LOSS, share_of_notill_payment_annualised=r['X'] * PRICE * FREQ[k] / NOTILL, gbp_per_ha_shock_season=r['X'] * PRICE)
        res.append(r); saved[x['name']] = [round(float(v), 6) for v in draws]
        w.log(x['name'], round(th0, 3), 'cell', c1, ins(c1), 'shuffled', c2, ins(c2), 'X', round(r['X'], 3))
    json.dump(dict(rows=res), open(os.path.join(w.RES, 'w3_b1_equivalence.json'), 'w'), indent=1, default=float)
    json.dump(saved, open(os.path.join(w.RES, 'w3_b1_equivalence_draws.json'), 'w'))
    report()
    w.log('done')


if __name__ == '__main__':
    main()

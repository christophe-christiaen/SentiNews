"""W3-T Stage 2: heat apart from drought (protocol: w3_t_heat_only_protocol.md, with the before-entry check fixed in its record).
Rows that Stage 1 found unreadable are written with their estimates but carry no reading.

Input   as w3_t_heat_power.py, plus results/w3_t_heat_power.json
Output  wp3_elms_effect/results/w3_t_heat_only.md, .json (aggregates only)
"""
import json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'wp1_regional_signal', 'src'))
import wp3_did as w
import wp3_within_cohort as wc
from w3_z_partf import members
from w3_h_step3 import index_matrix
from w3_h_prices import prices
from w3_t_heat_power import categories, FAMS, OUTCOMES, SP, K
from w3_z_partf_harvest import index_checks
from wp1_nowcast import CROPS, YEARS


def main():
    d = w.Data(); t = d.t
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    M = ms.in_matched_sample.values
    H, C = index_matrix(t)
    Y = {'July NDVI (SD)': d.Y['ndvi_july_z'], 'Harvest index (t/ha)': H}
    Mem = members(t); Mem['All agreement land'] = np.ones(len(t), bool)
    power = {(r['outcome'], r['contrast'], r['family']): r for r in json.load(open(os.path.join(w.RES, 'w3_t_heat_power.json')))['rows']}
    cats = {h: categories(h) for h in (5, 3, 8)}
    Gp, tmax = np.where(d.G > 0, d.G - 2, 0), np.where(d.G > 0, d.G, 9999)

    def est(y, fam, c, sn, G=None, tm=None, uni=False, use_crop=False, never=False, heat=5):
        G0 = d.G if G is None else G
        try:
            if never:
                P = [w.blocks(y, G0, d.cell, d.crop, use_crop, list(sn), fam, M & ((G0 == g) | (G0 == 0)), tm, uni) for g in sorted(set(G0[(G0 > 0) & M]) & set(sn))]
                TR, CO = pd.concat([x[0] for x in P], ignore_index=True), pd.concat([x[1] for x in P], ignore_index=True)
            else:
                TR, CO = w.blocks(y, G0, d.cell, d.crop, use_crop, list(sn), fam, M, tm, uni)
        except ValueError:
            return None
        ix = pd.MultiIndex.from_arrays([d.cells[TR.cell.values], TR.t.values])
        TR['shock'] = cats[heat][c + 'a'].reindex(ix).fillna(False).values.astype(bool)
        TR['prev'] = cats[heat][c + 'b'].reindex(ix).fillna(False).values.astype(bool)
        return w.Est(TR, CO, d.cluster)

    def con(E, sel):
        if E is None: return None
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        a, b = p & TR.shock.values, p & TR.prev.values
        if not a.any() or not b.any(): return None
        th, V, G, _ = E.run([E.weights(a, b), E.weights(a), E.weights(b)])
        return w.row('', th, V, 0, G, int(TR.nT.values[a | b].sum())) | dict(in_hazard=float(th[1]), in_other=float(th[2]))

    def before(E, sel):
        if E is None: return None
        TR = E.TR; p = np.isin(TR.e.values, wc.PRE) & (TR.t.values <= 2020) & (TR.fam.values == 'F' if sel else True)
        a, b = p & TR.shock.values, p & TR.prev.values
        if not a.any() or not b.any(): return None
        th, V, G, _ = E.run([E.weights(a, b)])
        return w.row('', th, V, 0, G, int(TR.nT.values[a | b].sum())) | dict(mde=K * float(np.sqrt(V[0, 0])))

    def wcon(E, sel, pre):
        if E is None: return None
        TR = E.TR; m = (TR.fam.values == 'F') if sel else np.ones(len(TR), bool)
        win = (np.isin(TR.e.values, wc.PRE) & (TR.t.values <= 2020)) if pre else TR.e.values >= 0
        v, k = wc.within(E, win & m & TR.shock.values, win & m & TR.prev.values, ['g'])
        if k == 0: return None
        th, V, G, _ = E.run([v])
        return w.row('', th, V, 0, G, int(TR.nT.values[v != 0].sum())) | dict(cohorts=k)

    def by_season(E, sel):
        """T1 inside each season, and pooled by treated fields on the hot side."""
        if E is None: return None
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        vs, ns, out = [], [], {}
        for s in sorted(set(TR.t.values[p & TR.shock.values])):
            a, b = p & TR.shock.values & (TR.t.values == s), p & TR.prev.values & (TR.t.values == s)
            if not a.any() or not b.any(): continue
            v = E.weights(a, b); th, V, G, _ = E.run([v])
            out[int(s)] = w.row('', th, V, 0, G, int(TR.nT.values[a | b].sum())); vs.append(v); ns.append(TR.nT.values[a].sum())
        if vs:
            pi = np.array(ns) / sum(ns)
            th, V, G, _ = E.run([sum(a * b for a, b in zip(pi, vs))])
            out['pooled'] = w.row('', th, V, 0, G)
        return out

    def read(a, chk, lim, rd, c):
        if not rd: return 'underpowered, not read'
        if not a or not chk: return 'not shown'
        ok = chk['lo'] <= 0 <= chk['hi']
        out = 'holds better under heat' if a['lo'] > 0 and ok else 'heat cost indicated' if a['hi'] < 0 and ok else 'not shown'
        if c == 'T1' and out != 'not shown' and chk['mde'] > lim: out += ', weak before-entry check'
        return out

    res = []
    for out, (sn, lim) in OUTCOMES.items():
        for c, lab in (('T1', 'T1 heat on top of drought'), ('T2', 'T2 literal heat-only')):
            for f in FAMS:
                sel = f != 'All agreement land'
                fam = np.where(Mem[f], 'F', 'O') if sel else d.fam
                E = est(Y[out], fam, c, sn); Eu = est(Y[out], fam, c, sn, uni=True)
                pw = power[(out, lab, f)]
                r = dict(outcome=out, contrast=lab, family=f, readable=pw['readable'], mde=pw['mde'], main=con(E, sel), within=wcon(Eu, sel, False), within_before=wcon(Eu, sel, True),
                         never_only=con(est(Y[out], fam, c, sn, never=True), sel), crop_strata=con(est(Y[out], fam, c, sn, use_crop=True), sel),
                         heat3=con(est(Y[out], fam, c, sn, heat=3), sel), heat8=con(est(Y[out], fam, c, sn, heat=8), sel))
                r['check'] = before(Eu, sel) if c == 'T1' else con(est(Y[out], fam, c, SP, G=Gp, tm=tmax), sel)
                if c == 'T1': r['by_season'] = by_season(E, sel)
                if out.startswith('Harvest'):
                    for k in CROPS: r[k] = con(est(C[k], fam, c, sn), sel)
                r['reading'] = read(r['main'], r['check'], lim, pw['readable'], c)
                res.append(r); a = r['main']
                w.log(out, c, f, a and (round(a['est'], 3), round(a['lo'], 3), round(a['hi'], 3)), r['check'] and round(r['check']['est'], 3), r['reading'])
    hot = cats[5]
    x = pd.read_parquet(os.path.join(w.D, 'weather', 'cell_year_shocks.parquet')).assign(h=lambda s: s.hot_days_28 >= 5).set_index(['cell_id', 'year']).h
    hm = x.reindex(pd.MultiIndex.from_product([d.cells, w.SEASONS])).fillna(False).values.reshape(len(d.cells), len(w.SEASONS))[d.cell].astype(bool)
    chk, hot_rs = index_checks(d, hm[:, :len(YEARS)])
    p = prices(); feed = float(np.mean(list(p['Feed wheat'].values()))); allp = [v for s in p.values() for v in s.values()]
    json.dump(dict(rows=res, index_checks=chk, hot_region_seasons=hot_rs, feed_wheat=feed, price_low=min(allp), price_high=max(allp)), open(os.path.join(w.RES, 'w3_t_heat_only.json'), 'w'), indent=1, default=float)
    c_ = lambda x: '' if not x else f"{x['est']:+.3f} ({x['lo']:+.3f}, {x['hi']:+.3f})"
    L = ['# W3-T Stage 2: heat apart from drought', '', 'Protocol: [w3_t_heat_only_protocol.md](w3_t_heat_only_protocol.md); power: [w3_t_heat_power.md](w3_t_heat_power.md). Exploratory; no multiple-testing correction. E3 matched sample; strata ERA5 cell × season; SE clustered by ERA5 cell; wet-shock cell-seasons dropped from both sides. T1 is hot and dry minus dry, not hot; T2 is hot, not dry, minus calm, and rests on 2022 alone. T1\'s check is before entry, resting on 2018; T2\'s is the registered placebo, resting on 2019. Estimates on rows marked "not read" aren\'t findings.', '']
    for out in OUTCOMES:
        L += [f'## {out}', '', '| Contrast | Family | MDE | Contrast (95% interval) | Check | Reading | Within cohort | Never-treated only | Crop strata | Heat ≥ 3 days | Heat ≥ 8 days |', '|---|---|---:|---|---|---|---|---|---|---|---|']
        for r in res:
            if r['outcome'] == out:
                L.append(f"| {r['contrast'][:2]} | {r['family']} | {r['mde']:.3f} | {c_(r['main'])} | {c_(r['check'])} | {r['reading']} | {c_(r['within'])} | {c_(r['never_only'])} | {c_(r['crop_strata'])} | {c_(r['heat3'])} | {c_(r['heat8'])} |")
        L += ['', '### T1 within each season', '', '| Family | ' + ' | '.join(['2022', '2025', '2026', 'Pooled']) + ' |', '|---|---|---|---|---|']
        for r in res:
            if r['outcome'] == out and r['contrast'].startswith('T1') and r['readable'] and r['by_season']:
                b = r['by_season']; L.append(f"| {r['family']} | {c_(b.get(2022))} | {c_(b.get(2025))} | {c_(b.get(2026))} | {c_(b.get('pooled'))} |")
        L.append('')
    L += ['## Harvest index by crop, readable T1 rows', '', '| Family | ' + ' | '.join(CROPS) + ' |', '|---|' + '---|' * len(CROPS)]
    for r in res:
        if r['outcome'].startswith('Harvest') and r['contrast'].startswith('T1') and r['readable']:
            L.append(f"| {r['family']} | " + ' | '.join(c_(r[k]) for k in CROPS) + ' |')
    L += ['', '## £/ha, readable T1 rows', '', f'Feed wheat mean 2021–2025, £{feed:.0f}/t; all crop prices £{min(allp):.0f}–£{max(allp):.0f}/t. Revenue only.', '', '| Family | £/ha (95% interval) |', '|---|---|']
    for r in res:
        if r['outcome'].startswith('Harvest') and r['contrast'].startswith('T1') and r['readable']:
            a = r['main']; L.append(f"| {r['family']} | {a['est'] * feed:+.1f} ({a['lo'] * feed:+.1f}, {a['hi'] * feed:+.1f}) |")
    L += ['', '## Index check in hot region-seasons, does not change the reading', '', '| Crop | Hot region-seasons | MAE hot (t/ha) | MAE other (t/ha) | Ratio | Bias hot (t/ha) | Bias other (t/ha) |', '|---|---:|---:|---:|---:|---:|---:|']
    for k, v in chk.items():
        L.append(f"| {k} | {v['wet_region_seasons']} | {v['mae_wet']:.2f} | {v['mae_other']:.2f} | {v['ratio']:.2f} | {v['bias_wet']:+.2f} | {v['bias_other']:+.2f} |")
    L += ['', 'Hot region-seasons by harvest year: ' + ', '.join(f'{y}: {n}' for y, n in hot_rs.items()) + '.', '']
    open(os.path.join(w.RES, 'w3_t_heat_only.md'), 'w').write('\n'.join(L))
    w.log('done')


if __name__ == '__main__':
    main()

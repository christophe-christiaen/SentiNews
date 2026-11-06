"""W3-B1 resilience indices, post-hoc look at Rs after dry or heat, specified after the main results were seen (protocol record, 6 November 2026):
season weights on both sides of the contrast, the share of each side in wet-shock cells, each season's mean effect, and leave one season out.

Input   as w3_b1_resilience_indices.py
Output  wp3_elms_effect/results/w3_b1_resilience_posthoc.json (aggregates only)
"""
import json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
from w3_z_partf import members
from w3_b1_resilience_indices import half_months, integrate, indices, S26, FAMS


def main():
    d = w.Data(); t = d.t
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    ME = ms.in_matched_sample.values
    Mem = members(t); sh = w.shock_table(**w.MAIN_SHOCK)
    A, _ = half_months(t); Rs = indices(integrate(A, 5, True))['Rs']
    out = {}
    for f in FAMS:
        sel = f != 'All agreement land'
        fam = np.where(Mem[f], 'F', 'O') if sel else d.fam
        TR, CO = w.blocks(Rs, d.G, d.cell, d.crop, False, list(S26), fam, ME, None, False)
        E = w.Est(w.attach_shocks(TR, d.cells, sh), CO, d.cluster)
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        a, b = p & ~TR.shock.values & TR.prev.values, p & ~TR.shock.values & ~TR.prev.values
        nT, tau, yr, wet = TR.nT.values, TR.tau_sum.values, TR.t.values, TR.wet.values
        def side(m):
            return {str(y): dict(weight=float(nT[m & (yr == y)].sum() / nT[m].sum()), wet_share=float(nT[m & (yr == y) & wet].sum() / max(nT[m & (yr == y)].sum(), 1)),
                                 mean_effect=float(tau[m & (yr == y)].sum() / nT[m & (yr == y)].sum())) for y in sorted(set(yr[m]))}
        def con(x, y):
            th, V, G, _ = E.run([E.weights(x, y)]); se = float(np.sqrt(V[0, 0]))
            return dict(est=float(th[0]), se=se, lo=float(th[0] - 1.96 * se), hi=float(th[0] + 1.96 * se))
        loo = {str(y): con(a & (yr != y), b & (yr != y)) for y in sorted(set(yr[a | b])) if (a & (yr != y)).any() and (b & (yr != y)).any()}
        out[f] = dict(main=con(a, b), after_hazard=side(a), after_calm=side(b), wet_share_after_hazard=float(nT[a & wet].sum() / nT[a].sum()),
                      wet_share_after_calm=float(nT[b & wet].sum() / nT[b].sum()), leave_one_season_out=loo,
                      no_wet_seasons=con(a & ~wet, b & ~wet))
        w.log(f, out[f]['main'], out[f]['wet_share_after_hazard'], out[f]['wet_share_after_calm'])
    json.dump(out, open(os.path.join(w.RES, 'w3_b1_resilience_posthoc.json'), 'w'), indent=1)
    print(json.dumps(out, indent=0)[:6000])


if __name__ == '__main__':
    main()

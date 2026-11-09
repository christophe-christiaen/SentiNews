"""W3-B1 baseline-variability check on H1 (protocol: w3_b1_baseline_sd_protocol.md): do agreement fields have more variable 2017-2020 July NDVI
than their comparison fields, does NDVI fall in shock seasons, and does H1 survive strata by baseline-SD tercile?

Input   as wp3_did.py, plus data/matched_sample.parquet, data/matched_sample_e3.parquet
Output  wp3_elms_effect/results/w3_b1_baseline_sd.json (aggregates only)
"""
import json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp3_did as w
from w3_b1_h1h2_checks import raw


def main():
    d = w.Data(); t = d.t
    m0 = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet')).set_index('parcref').in_matched_sample
    M0 = m0.reindex(t.parcref).fillna(False).values.astype(bool)
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    ME = ms.in_matched_sample.values
    J = raw(t, 'ndvi_july')
    b = J[:, :4]; n = (~np.isnan(b)).sum(1)
    with np.errstate(all='ignore'):
        import warnings; warnings.simplefilter('ignore')
        sd = np.nanstd(b, 1, ddof=1)
    sd[n < 2] = np.nan
    zero = sd == 0
    lsd = np.where(zero, np.nan, np.log(sd))
    q = np.nanquantile(sd, [1 / 3, 2 / 3])
    terc = np.where(np.isnan(sd), 3, np.digitize(sd, q))
    crop_t = d.crop * 4 + terc[:, None]
    sh = w.shock_table(**w.MAIN_SHOCK)
    out = dict(tercile_cuts=[float(x) for x in q], fields_sd_zero=int(zero.sum()))

    for lab, pm in (('X2 sample (frozen)', M0), ('E3 sample', ME)):
        T = pm & (d.G > 0) & (d.G <= 2025); C = pm & ((d.G == 0) | (d.G > 2025))
        df = pd.DataFrame(dict(cell=d.cell, y=lsd, T=T, C=C))[(T | C) & ~np.isnan(lsd)]
        vT, vC = df[df['T']].y.var(), df[df['C']].y.var()
        g = df.groupby(['cell', 'T']).y.agg(['mean', 'var', 'size']).unstack('T')
        g = g.dropna(subset=[('mean', True), ('mean', False)])
        nt, nc = g[('size', True)], g[('size', False)]
        wt = nt / nt.sum()
        diff = g[('mean', True)] - g[('mean', False)]
        var = g[('var', True)].where(nt > 1, vT).fillna(vT) / nt + g[('var', False)].where(nc > 1, vC).fillna(vC) / nc
        est, se = float((wt * diff).sum()), float(np.sqrt((wt ** 2 * var).sum()))
        part1 = dict(est_log_sd=est, se=se, lo=est - 1.96 * se, hi=est + 1.96 * se, ratio_of_sd=float(np.exp(est)), cells=int(len(g)),
                     floor_share_agreement=float(np.mean(sd[T & ~np.isnan(sd)] <= .02)), floor_share_comparison=float(np.mean(sd[C & ~np.isnan(sd)] <= .02)),
                     median_sd_agreement=float(np.nanmedian(sd[T])), median_sd_comparison=float(np.nanmedian(sd[C])))
        # part 2: comparison fields' mean change in raw July NDVI, shock minus other seasons after 2020
        E = d.est(Ymat=J, pmask=pm); CO = E.CO.copy()
        cid = d.cells[CO.cell.values]
        CO['shock'] = sh.shock.reindex(pd.MultiIndex.from_arrays([cid, CO.t.values])).fillna(False).values.astype(bool)
        CO = CO[CO.t >= 2021]; CO['y'] = CO.meanC * CO.nC
        A, B = CO[CO.shock], CO[~CO.shock]
        ma, mb = A.y.sum() / A.nC.sum(), B.y.sum() / B.nC.sum()
        Ia = (A.y - ma * A.nC).groupby(A.cell).sum() / A.nC.sum(); Ib = (B.y - mb * B.nC).groupby(B.cell).sum() / B.nC.sum()
        I = Ia.sub(Ib, fill_value=0); se2 = float(np.sqrt((I ** 2).sum()))
        part2 = dict(est=float(ma - mb), se=se2, lo=float(ma - mb - 1.96 * se2), hi=float(ma - mb + 1.96 * se2), mean_change_shock=float(ma), mean_change_other=float(mb))
        # part 3: H1 with SD-tercile strata
        def h1(E):
            TR = E.TR; post = TR.e.values >= 0
            th, V, G, _ = E.run([E.weights(post & TR.shock.values, post & ~TR.shock.values)]); s = float(np.sqrt(V[0, 0]))
            return dict(est=float(th[0]), se=s, lo=float(th[0] - 1.96 * s), hi=float(th[0] + 1.96 * s))
        base = h1(d.est('ndvi_july_z', pmask=pm))
        part3 = h1(d.est('ndvi_july_z', pmask=pm, crop=crop_t))
        p1 = part1['lo'] > 0; p2 = part2['hi'] < 0; p3 = part3['lo'] <= 0 <= part3['hi'] or part3['est'] <= base['est'] / 2
        label = 'scaling artefact supported' if p1 and p2 and p3 else 'not supported' if part1['lo'] <= 0 else 'partly supported'
        out[lab] = dict(part1=part1, part2=part2, h1_frozen=base, part3=part3, conditions=dict(sd_higher=bool(p1), ndvi_falls=bool(p2), h1_weakened=bool(p3)), label=label)
        w.log(lab, out[lab])
    assert abs(out['X2 sample (frozen)']['h1_frozen']['est'] - .082) < .0006
    json.dump(out, open(os.path.join(w.RES, 'w3_b1_baseline_sd.json'), 'w'), indent=1)
    w.log('done')


if __name__ == '__main__':
    main()

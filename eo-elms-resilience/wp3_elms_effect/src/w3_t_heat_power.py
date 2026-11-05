"""W3-T Stage 1: power of the heat contrasts, with no estimate (protocol: w3_t_heat_only_protocol.md). Writes parcel-seasons,
contributing cells and seasons, standard errors and minimum detectable effects. Stage 2 runs only after this is reported.

Input   as wp3_did.py, plus matched_sample_e3.parquet, w3_h_field_index.parquet, w3_s_parcel_codes.parquet, results/w3_s_crosswalk.csv
Output  wp3_elms_effect/results/w3_t_heat_power.md, .json (aggregates only, no estimates)
"""
import json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'wp1_regional_signal', 'src'))
import wp3_did as w
from w3_z_partf import members
from w3_h_step3 import index_matrix

FAMS = ['All agreement land', 'Management-only', 'Cover crops', 'No-till']
OUTCOMES = {'July NDVI (SD)': (range(2017, 2027), 0.10), 'Harvest index (t/ha)': (range(2017, 2026), 0.10)}
MIN_CELLS, K = 30, 2.8
SP = range(2017, 2021)


def categories(heat=5):
    s = pd.read_parquet(os.path.join(w.D, 'weather', 'cell_year_shocks.parquet'))
    dry = (s.spring_anom_pct <= -20) | (s.soil_moist_z <= -1.0)
    hot, wet = s.hot_days_28 >= heat, s.wet_shock.astype(bool)
    s['T1a'], s['T1b'] = hot & dry & ~wet, dry & ~hot & ~wet
    s['T2a'], s['T2b'] = hot & ~dry & ~wet, ~hot & ~dry & ~wet
    return s.set_index(['cell_id', 'year'])[['T1a', 'T1b', 'T2a', 'T2b']]


def main():
    d = w.Data(); t = d.t
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'))
    assert (ms.parcref.values == t.parcref.values).all()
    M = ms.in_matched_sample.values
    H, _ = index_matrix(t)
    Y = {'July NDVI (SD)': d.Y['ndvi_july_z'], 'Harvest index (t/ha)': H}
    Mem = members(t); Mem['All agreement land'] = np.ones(len(t), bool)
    cat = categories()
    Gp, tmax = np.where(d.G > 0, d.G - 2, 0), np.where(d.G > 0, d.G, 9999)

    def est(y, fam, c, sn, G=None, tm=None):
        try:
            TR, CO = w.blocks(y, d.G if G is None else G, d.cell, d.crop, False, list(sn), fam, M, tm, False)
        except ValueError:
            return None
        ix = pd.MultiIndex.from_arrays([d.cells[TR.cell.values], TR.t.values])
        TR['shock'] = cat[c + 'a'].reindex(ix).fillna(False).values.astype(bool)
        TR['prev'] = cat[c + 'b'].reindex(ix).fillna(False).values.astype(bool)     # second side, so each side keeps its own effect
        return w.Est(TR, CO, d.cluster)

    def power(E, sel):
        """Only the standard error is kept from the estimator's output."""
        if E is None: return None
        TR = E.TR; p = (TR.e.values >= 0) & (TR.fam.values == 'F' if sel else True)
        a, b = p & TR.shock.values, p & TR.prev.values
        if not a.any() or not b.any(): return None
        _, V, G, _ = E.run([E.weights(a, b)])
        side = lambda m: dict(parcel_seasons=int(TR.nT.values[m].sum()), cells=int(np.unique(TR.cell.values[m]).size),
                              seasons={int(k): int(v) for k, v in pd.Series(TR.nT.values[m]).groupby(TR.t.values[m]).sum().items()})
        return dict(se=float(np.sqrt(V[0, 0])), clusters=int(G), hazard=side(a), other=side(b))

    rows = []
    for out, (sn, lim) in OUTCOMES.items():
        for c, lab in (('T1', 'T1 heat on top of drought'), ('T2', 'T2 literal heat-only')):
            for f in FAMS:
                sel = f != 'All agreement land'
                fam = np.where(Mem[f], 'F', 'O') if sel else d.fam
                r = dict(outcome=out, contrast=lab, family=f, limit=lim, main=power(est(Y[out], fam, c, sn), sel),
                         placebo=power(est(Y[out], fam, c, SP, G=Gp, tm=tmax), sel))
                x = r['main']
                r['mde'] = K * x['se'] if x else None
                r['readable'] = bool(x and r['mde'] <= lim and x['hazard']['cells'] >= MIN_CELLS and x['other']['cells'] >= MIN_CELLS)
                rows.append(r); w.log(out, lab, f, r['mde'] and round(r['mde'], 3), r['readable'])
    json.dump(dict(rows=rows, k=K, min_cells=MIN_CELLS), open(os.path.join(w.RES, 'w3_t_heat_power.json'), 'w'), indent=1, default=float)
    L = ['# W3-T Stage 1: power of the heat contrasts', '',
         f'Protocol: [w3_t_heat_only_protocol.md](w3_t_heat_only_protocol.md). **No estimate has been computed for reading or written here.** Minimum detectable effect (MDE) = {K} × SE, for 80% power at 5% two-sided. '
         f'A row is read only if its MDE is within 0.10 SD or 0.10 t/ha and each side has at least {MIN_CELLS} weather cells. E3 matched sample; strata ERA5 cell × season; SE clustered by ERA5 cell. "Hazard" is hot and dry (T1) or hot, not dry (T2); "other" is dry, not hot (T1) or calm (T2). Parcel-seasons are after entry.', '']
    for out in OUTCOMES:
        L += [f'## {out}', '', '| Contrast | Family | Hazard side: parcel-seasons, cells | Other side: parcel-seasons, cells | Seasons on hazard side | SE | MDE | Placebo SE | Readable |', '|---|---|---|---|---|---:|---:|---:|---|']
        for r in rows:
            if r['outcome'] != out: continue
            x, p = r['main'], r['placebo']
            if not x:
                L.append(f"| {r['contrast']} | {r['family']} | none | none | none |  |  |  | no |"); continue
            ss = ', '.join(f'{k}: {v:,}' for k, v in x['hazard']['seasons'].items())
            L.append(f"| {r['contrast']} | {r['family']} | {x['hazard']['parcel_seasons']:,}, {x['hazard']['cells']} | {x['other']['parcel_seasons']:,}, {x['other']['cells']} | {ss} | {x['se']:.3f} | {r['mde']:.3f} | {'none' if not p else format(p['se'], '.3f')} | {'yes' if r['readable'] else 'no'} |")
        L.append('')
    open(os.path.join(w.RES, 'w3_t_heat_power.md'), 'w').write('\n'.join(L))
    w.log('done')


if __name__ == '__main__':
    main()

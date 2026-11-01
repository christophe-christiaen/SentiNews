"""WP3 deviation D2 (decisions record, 1 November 2026, fixed before this was run): agreement entry re-dated to the
earliest start of an area-based option in any snapshot, on top of D1's primary cleaned controls.

Primary: re-date, recompute G (1 March rule), drop parcels whose re-dated entry is before 2021.
Sensitivity: drop every agreement parcel with an earlier snapshot start.
Outputs wp3_d2_redate.{md,json}; registered files untouched.
"""
import json, os, sys, tempfile
import numpy as np, pandas as pd, pyogrio

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wp3_did as w
import wp3_d1_clean_controls as d1

HA = {'HA', 'H', 'HECTARES', 'HECTARE'}                    # 'H' in the legacy CSS file


def parse_start(x):
    """Snapshot dates: YYYYMMDD (ES 2025 geodatabase) or UK day-first text (dd/mm/yyyy, dd-mm-yyyy hh:mm:ss)."""
    x = x.astype(str).str.strip()
    ymd = x.str.fullmatch(r'\d{8}')
    out = pd.to_datetime(x.where(~ymd), dayfirst=True, errors='coerce', format='mixed')
    out[ymd] = pd.to_datetime(x[ymd], format='%Y%m%d', errors='coerce')
    return out


def earliest_area_start():
    parts = []
    for src, pc, sc in d1.OPT:
        lay = pyogrio.list_layers(src)[0][0]
        pick = {f.upper(): f for f in pyogrio.read_info(src, layer=lay)['fields']}
        df = pyogrio.read_dataframe(src, layer=lay, columns=[pick[pc], pick[sc], pick['UOM']], read_geometry=False)
        df = df.rename(columns={pick[pc]: 'parcref', pick[sc]: 'start', pick['UOM']: 'uom'})   # by name: pyogrio keeps file order
        df = df[df.uom.astype(str).str.strip().str.upper().isin(HA)]
        parts.append(pd.DataFrame({'parcref': df.parcref.astype(str).str.replace(' ', ''), 'start': parse_start(df.start)}))
    return pd.concat(parts).dropna().groupby('parcref').start.min()


def main():
    t = pd.read_parquet(os.path.join(w.ROOT, 'wp3_elms_effect', 'data', 'treatment.parquet'))
    snap_opt, _ = d1.snapshots(t)
    t = t[~((t.G == 0) & t.parcref.isin(snap_opt.index))].copy()               # D1 primary controls
    s = earliest_area_start()
    tr = t.G > 0
    old = pd.to_datetime(t.loc[tr, 'entry_date'])
    new = pd.concat([old, s.reindex(t.loc[tr, 'parcref']).set_axis(old.index)], axis=1).min(axis=1)
    earlier = new < old
    t2 = t.copy()
    t2.loc[tr, 'entry_date'] = new
    t2.loc[tr, 'entry_year'] = new.dt.year
    cut = pd.to_datetime(new.dt.year.astype(str) + '-03-01')
    t2.loc[tr, 'G'] = np.where(new <= cut, new.dt.year, new.dt.year + 1)
    pre2021 = tr & (t2.entry_year < 2021)
    prim = t2[~pre2021].copy(); prim['G'] = prim.G.astype(int)
    sens = t[~(tr & t.parcref.isin(t.loc[tr].parcref[earlier.values]))].copy()
    counts = {'agreement_parcels': int(tr.sum()), 're_dated_earlier': int(earlier.sum()),
              'dropped_entry_before_2021': int(pre2021.sum()),
              're_dated_within_2021_2026': int(earlier.sum() - pre2021.sum()),
              'cohort_moves': {f'{a}->{b}': int(n) for (a, b), n in pd.Series(list(zip(old.dt.year[earlier], new.dt.year[earlier]))).value_counts().head(12).items()},
              'never_treated_D1': int((t.G == 0).sum())}
    w.log(counts)
    res = {'counts': counts}
    with tempfile.TemporaryDirectory() as tmp:
        res['D2 primary (re-dated)'] = d1.run_sample('D2 primary', prim, tmp)
        res['D2 sensitivity (dropped)'] = d1.run_sample('D2 sensitivity', sens, tmp)
    reg = json.load(open(os.path.join(w.RES, 'wp3_e3_embeddings.json')))['estimates']
    dd1 = json.load(open(os.path.join(w.RES, 'wp3_d1_clean_controls.json')))['primary']
    res['registered'] = {'section 7 matching': reg['original matching'], 'matching + embeddings (E3)': reg['matching + embeddings (E3)']}
    json.dump(res, open(os.path.join(w.RES, 'wp3_d2_redate.json'), 'w'), indent=1, default=float)
    f = lambda r: f"{r['est']:+.3f} ({r['se']:.3f})"
    c = counts
    L = ['# WP3 deviation D2: agreement entry re-dated to the earliest snapshot start', '',
         'Fixed in the decisions record (1 November 2026) before this was run; on top of D1\'s cleaned never-treated '
         'comparison. Registered estimates remain the registered results.', '',
         f"- Agreement parcels: {c['agreement_parcels']:,}; {c['re_dated_earlier']:,} have an earlier area-based start in a snapshot. "
         f"{c['dropped_entry_before_2021']:,} re-date to before 2021 (already treated before entry; leave the analysis); "
         f"{c['re_dated_within_2021_2026']:,} move to an earlier 2021–2026 cohort.",
         f"- Never-treated (D1 primary): {c['never_treated_D1']:,}.", '']
    keys = ['H1', 'H1 within cohort', 'H1 within cohort, before entry', 'H2', 'H3', 'H2 within cohort', 'H3 within cohort']
    for lab in ('section 7 matching', 'matching + embeddings (E3)'):
        L += [f'## {lab}', '', '| Estimate | registered | D1 | D2 re-dated | D2 dropped |', '|---|---|---|---|---|']
        for k in keys:
            L.append(f"| {k} | {f(res['registered'][lab][k])} | {f(dd1[lab][k])} | {f(res['D2 primary (re-dated)'][lab][k])} | "
                     f"{f(res['D2 sensitivity (dropped)'][lab][k])} |")
        p, q = res['D2 primary (re-dated)'][lab]['matched'], res['D2 sensitivity (dropped)'][lab]['matched']
        L += ['', f"Matched: re-dated {p['treated']:,} agreement / {p['control']:,} never-treated (largest standardised difference "
              f"{p['max_smd_after']:.2f}); dropped {q['treated']:,} / {q['control']:,}.", '']
    L += ['Estimate (SE), SE clustered by ERA5 cell.']
    open(os.path.join(w.RES, 'wp3_d2_redate.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

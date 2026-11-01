"""W3-1 woody edge outside the field outline (record row of 1 November 2026, fixed before any value was computed).

Ring = 0-25 m outside the UKFields outline minus every other UKFields polygon; from the VOM windows on Drive
(int16 cm, nodata -32768). Per field: outside woody share (> 1 m), outside mean height, ring pixels. Then the
registered check: hedge management against never-treated (A), 95% bootstrap interval (2,000 resamples, seed 30).
Usage: w3_1_outside_band.py LIDAR_DIR. Per-field values go to shared/data/parcels (private); aggregates to results/w3_1_outside_band.{md,json}.
"""
import glob, json, os, sys
import numpy as np, pandas as pd, geopandas as gpd, shapely

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RES = os.path.join(ROOT, 'wp3_elms_effect', 'results'); PAR = os.path.join(ROOT, 'shared', 'data', 'parcels')
L = sys.argv[1]                                     # the project Drive's lidar folder (windows, fields, inside-band summary)
MIN_PIX = 200


def rings():
    F = gpd.read_parquet(f'{L}/w3_1_fields.parquet').to_crs(27700)
    F['ukfields_id'] = F.ukfields_id.astype(str)
    U = gpd.read_parquet(os.path.join(PAR, 'ukfields.parquet'), columns=['id', 'geometry']).to_crs(27700)
    U['id'] = U.id.astype(str)
    buf = F.geometry.buffer(25)
    U = U.iloc[np.unique(U.sindex.query(buf, predicate='intersects')[1])]
    tree, ug, uid = U.sindex, U.geometry.values, U.id.values
    out = {}
    for fid, g, b in zip(F.ukfields_id, F.geometry, buf):
        r = b.difference(g)
        nb = [ug[j] for j in tree.query(r, predicate='intersects') if uid[j] != fid]
        if nb: r = r.difference(shapely.union_all(nb))
        out[fid] = r
    return out


def main():
    R = rings(); print('rings', len(R), flush=True)
    acc = {}
    files = sorted(glob.glob(f'{L}/windows/*.npz'))
    for n, f in enumerate(files):
        z = np.load(f)
        for k in [k for k in z.files if not k.endswith('_tr')]:
            r = R.get(k)
            if r is None or r.is_empty: continue
            a = z[k]; t = z[k + '_tr']; ok = a != -32768
            jj, ii = np.meshgrid(np.arange(a.shape[1]) + .5, np.arange(a.shape[0]) + .5)
            shapely.prepare(r)
            m = shapely.contains_xy(r, t[2] + jj * t[0], t[5] + ii * t[4]) & ok
            h = a[m].astype('float32') / 100
            s = acc.setdefault(k, [0, 0, 0.0]); s[0] += int(m.sum()); s[1] += int((h > 1).sum()); s[2] += float(np.clip(h, 0, None).sum())
        if n % 500 == 0: print(n, '/', len(files), flush=True)
    W = pd.DataFrame.from_dict(acc, orient='index', columns=['out_n', 'out_gt1', 'out_hsum']); W.index.name = 'ukfields_id'
    W['outside_woody_share'] = W.out_gt1 / W.out_n; W['outside_mean_height'] = W.out_hsum / W.out_n
    inside = pd.read_parquet(f'{L}/w3_1_woody_edge.parquet'); inside.index = inside.index.astype(str)
    W = W.join(inside[['woody_edge_share', 'band_mean_height', 'any_post2020']], how='left')
    W.reset_index().to_parquet(os.path.join(PAR, 'w3_1_woody_outside.parquet'), index=False)

    s = pd.read_parquet(os.path.join(PAR, 'w3_1_sample.parquet')); s['ukfields_id'] = s.ukfields_id.astype(str)
    d = s.merge(W.reset_index(), on='ukfields_id', how='left')
    d['usable'] = d.out_n >= MIN_PIX
    rng = np.random.default_rng(30)

    def diff(x, y):
        x, y = x.dropna().values, y.dropna().values
        bs = [rng.choice(x, len(x)).mean() - rng.choice(y, len(y)).mean() for _ in range(2000)]
        return dict(diff=float(x.mean() - y.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)), n=[len(x), len(y)])

    u = d[d.usable]
    hm = u[(u.family == 'hedge_management') & (u.role == 'positive')]
    A = u[(u.family == 'hedge_management') & (u.role == 'A')]; B = u[(u.family == 'management_only') & (u.role == 'positive')]
    pre = lambda x: x[~x.any_post2020.astype(bool)]
    res = dict(fields=int(len(d)), with_ring=int(d.out_n.notna().sum()), usable=int(d.usable.sum()),
               by_group=u.groupby(['family', 'role']).agg(n=('ukfields_id', 'size'), outside_share=('outside_woody_share', 'mean'),
                                                          outside_median=('outside_woody_share', 'median'), outside_height=('outside_mean_height', 'mean'),
                                                          inside_share=('woody_edge_share', 'mean')).round(4).reset_index().to_dict('records'),
               check_vs_A=diff(hm.outside_woody_share, A.outside_woody_share),
               check_vs_B=diff(hm.outside_woody_share, B.outside_woody_share),
               check_vs_A_pre2021_surveys=diff(pre(hm).outside_woody_share, pre(A).outside_woody_share),
               families_vs_own_A={f: diff(u[(u.family == f) & (u.role == 'positive')].outside_woody_share,
                                          u[(u.family == f) & (u.role == 'A')].outside_woody_share)
                                  for f in ('new_hedges', 'area_strips', 'hedge_management', 'walls_banks')})
    res['check_passed'] = res['check_vs_A']['lo'] > 0
    json.dump(res, open(os.path.join(RES, 'w3_1_outside_band.json'), 'w'), indent=1)
    c = lambda r: f"{r['diff']:+.4f} ({r['lo']:+.4f} to {r['hi']:+.4f}; n {r['n'][0]:,} / {r['n'][1]:,})"
    Lm = ['# W3-1: existing woody edge outside the field outline (LiDAR VOM)', '',
          'Record row of 1 November 2026 (a deviation, fixed before any value was computed): ring 0–25 m outside the UKFields '
          'outline minus other UKFields polygons; share of ring pixels above 1 m. Aggregates only.', '',
          f"- Sampled fields {res['fields']:,}; with a ring {res['with_ring']:,}; usable (≥ {MIN_PIX} valid ring pixels) {res['usable']:,}.", '',
          '| Family | role | n | outside share (mean) | median | outside mean height (m) | inside-band share |', '|---|---|---|---|---|---|---|']
    Lm += [f"| {r['family']} | {r['role']} | {r['n']:,} | {r['outside_share']:.3f} | {r['outside_median']:.3f} | {r['outside_height']:.2f} | {r['inside_share']:.4f} |" for r in res['by_group']]
    Lm += ['', '**Registered check** (hedge management minus never-treated A; difference in mean outside share, 95% bootstrap interval):', '',
           f"- vs A: {c(res['check_vs_A'])} → **{'passed' if res['check_passed'] else 'failed'}**",
           f"- vs management-only B: {c(res['check_vs_B'])}",
           f"- vs A, pre-2021 surveys only: {c(res['check_vs_A_pre2021_surveys'])}", '', 'Each family against its own comparison A:', '']
    Lm += [f"- {f}: {c(r)}" for f, r in res['families_vs_own_A'].items()]
    open(os.path.join(RES, 'w3_1_outside_band.md'), 'w').write('\n'.join(Lm) + '\n'); print('\n'.join(Lm))


if __name__ == '__main__':
    main()

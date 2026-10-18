"""U3 (wp1_regional_signal/results/u3_protocol.md, written 18 October 2026 before extraction): the WP1 nowcast in
Scotland and Northern Ireland.

Steps: (1) crop classifier trained on England (CROME labels on the cereal-land panel, plus the U1 grassland sample as
'grass'); (2) crop per UKFields field and season; (3) validation gate against official crop areas; (4) region-year
features; (5) designs D1 transfer, D2 local, D3 pooled UK, leave-one-year-out; (6) blind 2026 nowcast.

Input   shared/data/s2/gee_local_ukfields/*.csv, gee_local_grass/*.csv; shared/data/parcels/ukfields_sample.parquet;
        shared/data/weather/{ukfields_era5_cell,cell_year_shocks_ukfields}.parquet; shared/data/yields/uk_nation_yields.csv;
        data/raw/scotland_harvest/regional_1991_2025.xlsx; data/raw/cops.ods; data/raw/boundaries/itl2_{2021,2025}_buc.geojson
Output  wp1_regional_signal/results/u3_scotland_ni.md, .json, u3_nowcast_2026.csv (aggregates only)
"""
import glob, json, os, re, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
import wp1_nowcast as w

ROOT, D, RES = w.ROOT, w.D, w.RES
sys.path.insert(0, os.path.join(ROOT, 'shared', 'src'))
import build_s2_panel as b

CROPS = list(w.CROPS)                                        # wheat, winter barley, spring barley
X12 = w.eo_cols(12)
MIN_FIELDS = 100
DROP = {'West Central Scotland', 'East Central Scotland'}
log = w.log


# ---------------------------------------------------------------- (1)-(2) crop labels
def load_dir(name):
    got = {}
    for f in glob.glob(os.path.join(D, 's2', name, 's2_*.csv')):
        m = re.search(r's2_(\d+_\d+)_(\d{4})\.csv$', f); got[(m.group(1), int(m.group(2)))] = f
    return b.load(got)


def classifiers(eng):
    from sklearn.ensemble import HistGradientBoostingClassifier
    rng = np.random.default_rng(18)
    grass = load_dir('gee_local_grass'); grass = grass[grass.year < w.NOW].assign(crop='grass')
    tr = eng[eng.year < w.NOW]
    tr = pd.concat([tr.iloc[rng.choice(len(tr), 600_000, replace=False)],
                    grass.iloc[rng.choice(len(grass), 150_000, replace=False)]], ignore_index=True)
    out = {}
    for kmax in (9, 12):
        X = w.eo_cols(kmax)
        out[kmax] = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, random_state=18).fit(tr[X], tr.crop)
        log('classifier k<=%d trained on %d rows' % (kmax, len(tr)))
    return out


def regions(fields):
    import geopandas as gpd
    pts = gpd.GeoDataFrame(fields, geometry=gpd.points_from_xy(fields.lon, fields.lat), crs=4326)
    for yr, f, col in (('2021', 'itl2_2021_buc.geojson', 'ITL221NM'), ('2025', 'itl2_2025_buc.geojson', 'ITL225NM')):
        itl = gpd.read_file(os.path.join(ROOT, 'data', 'raw', 'boundaries', f)).to_crs(4326)[[col, 'geometry']]
        j = gpd.sjoin(pts, itl, how='left', predicate='within').drop_duplicates('parcref')
        fields[f'region_{yr}'] = j[col].values
    ni = fields.nation == 'Northern Ireland'
    fields.loc[ni, ['region_2021', 'region_2025']] = 'Northern Ireland'
    return fields


def ukfields_panel(clf):
    f = regions(pd.read_parquet(os.path.join(D, 'parcels', 'ukfields_sample.parquet')))
    p = load_dir('gee_local_ukfields').merge(f[['parcref', 'nation', 'area_m2', 'frac', 'region_2021', 'region_2025']], on='parcref')
    p['region'] = np.where(p.year >= 2025, p.region_2025, p.region_2021)
    cell = pd.read_parquet(os.path.join(D, 'weather', 'ukfields_era5_cell.parquet'))[['parcref', 'cell_id_data']]
    p = p.merge(cell, on='parcref', how='left')
    hist = p.year < w.NOW
    p.loc[hist, 'crop'] = clf[12].predict(p.loc[hist, X12])
    p.loc[~hist, 'crop_k9'] = clf[9].predict(p.loc[~hist, w.eo_cols(9)])
    p.loc[~hist, 'crop_k12'] = clf[12].predict(p.loc[~hist, X12])
    return p


# ---------------------------------------------------------------- (3) validation gate
def official_areas():
    rows = []
    f = os.path.join(ROOT, 'data', 'raw', 'scotland_harvest', 'regional_1991_2025.xlsx')
    for sheet in ('Table 4', 'Table 7'):
        raw = pd.read_excel(f, sheet_name=sheet, header=None)
        h = raw.index[raw[0].astype(str).str.strip() == 'Crop'][0]
        t = raw.iloc[h + 1:].copy(); t.columns = [str(c).strip().split('.')[0] for c in raw.iloc[h]]
        for c in [c for c in t.columns if c.isdigit()]:
            for _, r in t.iterrows():
                crop = str(r['Crop']).strip().lower()
                v = pd.to_numeric(r[c], errors='coerce')
                if crop in CROPS and pd.notna(v):
                    rows.append(dict(nation='Scotland', crop=crop, region=str(r['Region']).strip(), year=int(c), area_ha=float(v)))
    x = pd.ExcelFile(os.path.join(ROOT, 'data', 'raw', 'cops.ods'), engine='odf')
    for crop, (_, sheet) in w.CROPS.items():
        v = pd.read_excel(x, sheet, header=None)
        yrs = {j: int(a) for j, a in v.iloc[2].items() if isinstance(a, (int, float)) and pd.notna(a) and 1990 < a < 2100}
        r = v.index[v[0].astype(str).str.strip() == 'Northern Ireland'][0]          # first block = areas (hectares)
        for j, y in yrs.items():
            val = pd.to_numeric(v.iloc[r, j], errors='coerce')
            if pd.notna(val):
                rows.append(dict(nation='Northern Ireland', crop=crop, region='Northern Ireland', year=y, area_ha=float(val)))
    a = pd.DataFrame(rows)
    a.loc[(a.nation == 'Scotland') & (a.area_ha < 1000) & (a.region == 'Scotland'), 'area_ha'] *= 1000   # tables in 000 ha
    return a


def gate(p):
    off = official_areas()
    h = p[p.year < w.NOW]
    cls = h[h.crop.isin(CROPS)].assign(ha=lambda d: d.area_m2 / 1e4 / d.frac)
    nat = cls.groupby(['nation', 'crop', 'year']).ha.sum().rename('classified_ha').reset_index()
    o_nat = off[off.region.isin(['Scotland', 'Northern Ireland'])].rename(columns={'area_ha': 'official_ha'})
    m = nat.merge(o_nat[['nation', 'crop', 'year', 'official_ha']], on=['nation', 'crop', 'year'])
    m = m[((m.nation == 'Scotland') & m.year.between(2018, 2025)) | ((m.nation == 'Northern Ireland') & m.year.between(2017, 2025))]
    m['ratio'] = m.classified_ha / m.official_ha
    res = {}
    for (nation, crop), g in m.groupby(['nation', 'crop']):
        ok = int(g.ratio.between(1 / 1.5, 1.5).sum())
        r = dict(years_within=ok, years=int(len(g)), median_ratio=float(g.ratio.median()))
        passed = ok >= 6
        if nation == 'Scotland':
            reg = cls[(cls.nation == 'Scotland') & (cls.crop == crop) & cls.year.between(2018, 2024)].groupby('region').ha.sum()
            oreg = off[(off.nation == 'Scotland') & (off.crop == crop) & off.year.between(2018, 2024) & ~off.region.isin(['Scotland'] + list(DROP))].groupby('region').area_ha.sum()
            k = reg.index.intersection(oreg.index)
            rho = float(spearmanr(reg[k], oreg[k]).correlation) if len(k) >= 3 else float('nan')
            r['regional_spearman'] = rho
            passed = passed and rho >= 0.6
        r['passed'] = bool(passed)
        res[f'{nation} | {crop}'] = r
    return res, m


# ---------------------------------------------------------------- (4) features
def features(p, crop_col, shocks_file):
    sh = pd.read_parquet(shocks_file)[['cell_id', 'year'] + w.WEATHER].rename(columns={'cell_id': 'cell_id_data'})
    d = p[p[crop_col].isin(CROPS)].merge(sh, on=['cell_id_data', 'year'], how='left')
    g = d.groupby([crop_col, 'region', 'year'])
    f = g[X12].median().join(g[w.WEATHER].mean()).join(g.size().rename('parcels'))
    f.index = f.index.set_names(['crop', 'region', 'year'])
    return f.reset_index()


def targets():
    y = pd.read_csv(os.path.join(D, 'yields', 'uk_nation_yields.csv'))
    sc = y[(y.nation == 'Scotland') & y.year.between(2018, 2025) & ~y.region.isin(['Scotland'] + list(DROP))]
    sc = sc[(sc.year <= 2024) & (sc.geography == 'ITL2 (2018-2024)') | (sc.year == 2025)]
    ni = y[(y.nation == 'Northern Ireland') & y.year.between(2017, 2025)]
    return pd.concat([sc, ni])[['crop', 'region', 'year', 'yield_t_ha', 'method_flag']]


# ---------------------------------------------------------------- (5) designs
def transfer(eng, tgt, model, kmax):
    """D1: fit on England (years != y), apply to the target region-year, anomalies against each target region's
    mean over its other years."""
    rows = []
    cols = {'pilot': None, 'weather': w.WEATHER, 's2': w.eo_cols(kmax), 's2+weather': w.eo_cols(kmax) + w.WEATHER}[model]
    for y in sorted(tgt.year.unique()):
        tr, te, rest = eng[eng.year != y], tgt[tgt.year == y], tgt[tgt.year != y]
        ytr = (tr.yield_t_ha - tr.groupby('region').yield_t_ha.transform('mean')).values
        mu_t = rest.groupby('region')
        if model == 'pilot':
            pk = lambda d: d[[f'ndvi_p{k:02d}' for k in range(4, 10)]].max(axis=1)
            a = pk(tr) - tr.assign(pk=pk(tr)).groupby('region').pk.transform('mean')
            bt = pk(te).values - rest.assign(pk=pk(rest)).groupby('region').pk.mean().reindex(te.region).values
            pred = np.polyval(np.polyfit(a.fillna(0).values, ytr, 1), np.nan_to_num(bt))
        else:
            a, _ = w.anomalies(tr, tr, cols)
            bt = (te[cols] - mu_t[cols].mean().reindex(te.region).values).fillna(0.0)
            sc, m, _ = w.fit_ridge(a.values, ytr, tr.year.values)
            pred = m.predict(sc.transform(bt.values))
        obs = te.yield_t_ha.values - mu_t.yield_t_ha.mean().reindex(te.region).values
        rows.append(pd.DataFrame({'region': te.region.values, 'year': y, 'obs': obs, 'pred': pred}))
    return pd.concat(rows, ignore_index=True).dropna(subset=['obs'])


def score(r):
    r2 = 1 - ((r.obs - r.pred) ** 2).sum() / ((r.obs - r.obs.mean()) ** 2).sum()
    return dict(r2=float(r2), rmse=float(np.sqrt(((r.obs - r.pred) ** 2).mean())),
                r=float(np.corrcoef(r.obs, r.pred)[0, 1]) if len(r) > 2 else None, n=int(len(r)))


def coverage80(r):
    hit = []
    for y in r.year.unique():
        q = np.quantile((r.obs - r.pred)[r.year != y].abs(), 0.8)
        cur = r[r.year == y]; hit += list(((cur.obs - cur.pred).abs() <= q).values)
    return float(np.mean(hit))


def main():
    eng = w.panel()
    clf = classifiers(eng)
    p = ukfields_panel(clf)
    log('UKFields panel', len(p), p.groupby('nation').parcref.nunique().to_dict())
    gres, gtab = gate(p)
    log('gate', {k: v['passed'] for k, v in gres.items()})
    shocks_uk = os.path.join(D, 'weather', 'cell_year_shocks_ukfields.parquet')
    f_uk = features(p[p.year < w.NOW], 'crop', shocks_uk)
    f_eng = w.region_features(eng, 'crop')
    y_eng, y_uk = w.yields(), targets()
    out = dict(gate=gres, skill={}, coverage={}, sample=p.groupby('nation').parcref.nunique().to_dict())
    resid = {}
    for crop in CROPS:
        ok_nations = [n for n in ('Scotland', 'Northern Ireland') if gres.get(f'{n} | {crop}', {}).get('passed')]
        if not ok_nations:
            out['skill'][crop] = 'failed the validation gate in both nations'; continue
        regs = {'Scotland': set(y_uk.region) - {'Northern Ireland'}, 'Northern Ireland': {'Northern Ireland'}}
        keep = set().union(*[regs[n] for n in ok_nations])
        tgt = f_uk[(f_uk.crop == crop) & f_uk.region.isin(keep)].merge(y_uk[y_uk.crop == crop], on=['crop', 'region', 'year'])
        tgt = tgt[tgt.parcels >= MIN_FIELDS].reset_index(drop=True)
        eng_c = f_eng[f_eng.crop == crop].merge(y_eng[y_eng.crop == crop], on=['crop', 'region', 'year'])
        eng_c = eng_c[eng_c.year.isin(w.YEARS)].reset_index(drop=True)
        out['skill'][crop] = dict(nations=ok_nations, region_years=int(len(tgt)), fields_median=int(tgt.parcels.median()))
        for cut, k in (('mid-July', 9), ('end of August', 12)):
            for model in (['pilot', 'weather', 's2', 's2+weather'] if cut == 'mid-July' else ['s2', 's2+weather']):
                r1 = transfer(eng_c, tgt, model, k)
                r2 = w.loyo(tgt, model, k)
                pooled = pd.concat([eng_c, tgt], ignore_index=True)
                r3 = w.loyo(pooled, model, k); r3 = r3[r3.region.isin(tgt.region.unique())]
                for lab, r in (('D1 transfer', r1), ('D2 local', r2), ('D3 pooled UK', r3)):
                    out['skill'][crop][f'{lab} | {model} | {cut}'] = score(r)
                    resid[(crop, lab, model, cut)] = r
                    nf = r[~r.year.isin([2020, 2022])]
                    out['skill'][crop][f'{lab} | {model} | {cut} | without 2020, 2022'] = score(nf)
                    nl = r[r.year != 2025]
                    out['skill'][crop][f'{lab} | {model} | {cut} | without 2025'] = score(nl)
                log(crop, model, cut, {lab: round(out['skill'][crop][f'{lab} | {model} | {cut}']['r2'], 3) for lab in ('D1 transfer', 'D2 local', 'D3 pooled UK')})
        for lab in ('D1 transfer', 'D2 local', 'D3 pooled UK'):
            out['coverage'][f'{crop} | {lab}'] = coverage80(resid[(crop, lab, 's2+weather', 'mid-July')])
    reading = {}
    for crop in ('wheat', 'spring barley'):
        s = out['skill'].get(crop)
        if isinstance(s, dict):
            d1 = s['D1 transfer | s2+weather | mid-July']['r2']; d3 = s['D3 pooled UK | s2+weather | mid-July']['r2']
            reading[crop] = dict(D1_r2=d1, generalises=bool(d1 >= 0.30), D3_minus_D1=d3 - d1, local_helps=bool(d3 - d1 >= 0.10))
        else:
            reading[crop] = s
    out['reading'] = reading

    # (6) 2026 nowcast from the best design (s2+weather, by R2 at the cutoff)
    rows = []
    now = p[p.year == w.NOW]
    for crop in CROPS:
        s = out['skill'].get(crop)
        if not isinstance(s, dict):
            continue
        regs = {'Scotland': set(y_uk.region) - {'Northern Ireland'}, 'Northern Ireland': {'Northern Ireland'}}
        keep = set().union(*[regs[n] for n in s['nations']])
        tgt = f_uk[(f_uk.crop == crop) & f_uk.region.isin(keep)].merge(y_uk[y_uk.crop == crop], on=['crop', 'region', 'year'])
        tgt = tgt[tgt.parcels >= MIN_FIELDS].reset_index(drop=True)
        eng_c = f_eng[f_eng.crop == crop].merge(y_eng[y_eng.crop == crop], on=['crop', 'region', 'year'])
        eng_c = eng_c[eng_c.year.isin(w.YEARS)].reset_index(drop=True)
        for cut, k, col in (('mid-July', 9, 'crop_k9'), ('end of August', 12, 'crop_k12')):
            best = max(('D1 transfer', 'D2 local', 'D3 pooled UK'), key=lambda lab: s[f'{lab} | s2+weather | {cut}']['r2'])
            q80 = float(np.quantile((resid[(crop, best, 's2+weather', cut)].obs - resid[(crop, best, 's2+weather', cut)].pred).abs(), 0.8))
            t = features(now.assign(**{col: now[col]}), col, shocks_uk)
            t = t[(t.crop == crop) & t.region.isin(tgt.region.unique()) & (t.parcels >= MIN_FIELDS)].reset_index(drop=True)
            if t.empty:
                continue
            t['year'] = w.NOW; t['yield_t_ha'] = np.nan
            if best == 'D1 transfer':
                cols = w.eo_cols(k) + w.WEATHER
                a, _ = w.anomalies(eng_c, eng_c, cols)
                ytr = (eng_c.yield_t_ha - eng_c.groupby('region').yield_t_ha.transform('mean')).values
                sc, m, _ = w.fit_ridge(a.values, ytr, eng_c.year.values)
                bt = (t[cols] - tgt.groupby('region')[cols].mean().reindex(t.region).values).fillna(0.0)
                anom = m.predict(sc.transform(bt.values))
            else:
                train = tgt if best == 'D2 local' else pd.concat([eng_c, tgt], ignore_index=True)
                anom = w.predict('s2+weather', train, t, k)
            mean = tgt.groupby('region').yield_t_ha.mean().reindex(t.region).values
            for j in range(len(t)):
                rows.append(dict(crop=crop, cutoff=cut, design=best, region=t.region[j], fields=int(t.parcels[j]),
                                 nowcast_t_ha=round(mean[j] + anom[j], 2), lo80=round(mean[j] + anom[j] - q80, 2),
                                 hi80=round(mean[j] + anom[j] + q80, 2), mean_years=round(mean[j], 2)))
    nc = pd.DataFrame(rows)
    nc.to_csv(os.path.join(RES, 'u3_nowcast_2026.csv'), index=False)
    out['nowcast_written'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')
    json.dump(out, open(os.path.join(RES, 'u3_scotland_ni.json'), 'w'), indent=1, default=float)
    report(out, gtab, nc)


def report(o, gtab, nc):
    L = ['# U3: the WP1 nowcast in Scotland and Northern Ireland', '',
         'Protocol: [u3_protocol.md](u3_protocol.md), written before extraction (with its record). Fields: UKFields sample '
         f"(Scotland {o['sample'].get('Scotland', 0):,}, Northern Ireland {o['sample'].get('Northern Ireland', 0):,}); crops "
         'classified with a model trained on England. Aggregates only.', '',
         '## Validation gate (classified vs official crop area)', '',
         '| Nation · crop | years within ×1.5 | median ratio | regional Spearman | passed |', '|---|---|---|---|---|']
    for k, v in o['gate'].items():
        rs = v.get('regional_spearman'); rs = f'{rs:.2f}' if rs is not None and rs == rs else '–'
        L.append(f"| {k} | {v['years_within']}/{v['years']} | {v['median_ratio']:.2f} | {rs} | {'yes' if v['passed'] else 'no'} |")
    L += ['', '## Skill (out-of-sample R² of the yield anomaly; RMSE t/ha)', '',
          '| Crop | design | model | cutoff | R² | RMSE | r | n |', '|---|---|---|---|---|---|---|---|']
    for crop, s in o['skill'].items():
        if not isinstance(s, dict):
            L.append(f'| {crop} | {s} | | | | | | |'); continue
        for k, v in s.items():
            if not isinstance(v, dict) or ' | without' in k:
                continue
            d, m, c = k.split(' | ')
            L.append(f"| {crop} | {d} | {m} | {c} | {v['r2']:+.2f} | {v['rmse']:.2f} | {v['r'] if v['r'] is None else round(v['r'], 2)} | {v['n']} |")
    L += ['', '## Sensitivity (Sentinel-2 + weather, mid-July)', '', '| Crop | design | all years | without 2020, 2022 | without 2025 |', '|---|---|---|---|---|']
    for crop, s in o['skill'].items():
        if isinstance(s, dict):
            for d in ('D1 transfer', 'D2 local', 'D3 pooled UK'):
                k = f'{d} | s2+weather | mid-July'
                L.append(f"| {crop} | {d} | {s[k]['r2']:+.2f} | {s[k + ' | without 2020, 2022']['r2']:+.2f} | {s[k + ' | without 2025']['r2']:+.2f} |")
    L += ['', '80% interval coverage (nested, Sentinel-2 + weather, mid-July): ' + '; '.join(f'{k} {v:.0%}' for k, v in o['coverage'].items()), '',
          '## Reading (rules fixed in advance)', '']
    for crop, r in o['reading'].items():
        if isinstance(r, dict):
            L.append(f"- **{crop}:** D1 R² {r['D1_r2']:+.2f} → " + ('**generalises** (≥ 0.30)' if r['generalises'] else '**does not generalise** (< 0.30)')
                     + f"; D3 − D1 = {r['D3_minus_D1']:+.2f} → " + ('local data help.' if r['local_helps'] else 'local data do not add ≥ 0.10.'))
        else:
            L.append(f'- **{crop}:** {r}')
    L += ['', '## 2026 nowcast (blind; committed before any official 2026 Scottish or NI yield was looked at)', '',
          '| Crop | cutoff | design | region | fields | nowcast (t/ha) | 80% interval | mean of scored years |', '|---|---|---|---|---|---|---|---|']
    for r in nc.itertuples():
        L.append(f'| {r.crop} | {r.cutoff} | {r.design} | {r.region} | {r.fields:,} | {r.nowcast_t_ha:.2f} | {r.lo80:.2f}–{r.hi80:.2f} | {r.mean_years:.2f} |')
    L += ['', f"Nowcast written {o['nowcast_written']}. Limits: crops classified, not declared; UKFields boundaries are "
          'automatic (2021) and unofficial; Scottish regional yields are survey estimates (2020 and 2022 by a different method).']
    open(os.path.join(RES, 'u3_scotland_ni.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

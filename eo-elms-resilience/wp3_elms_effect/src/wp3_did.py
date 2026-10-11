"""WP3: do agri-environment agreements buffer cereal land against weather shocks? Runs the frozen pre-registration
(wp3_elms_effect/results/preregistration.md, commit b0f232b; implementation readings in its decisions record).

Design
  Sample      cereal parcels entering an area-based CS / SFI agreement in 2021-2026 and never-treated cereal parcels,
              matched (section 7) on a propensity score within ITL1 region; build_treatment.py gives G (first full season)
  Estimator   Callaway-Sant'Anna group-time comparisons. For cohort g and season t: change in outcome from the base
              season (g-1 after entry; t-1 before entry, 'varying base') for cohort g, minus the mean change of
              never-treated and not-yet-treated parcels (G > t) in the same stratum. Stratum = ERA5 cell x season x
              CROME crop of that season (main), or ERA5 cell x season (2026 version, hexagon check).
              Every treated parcel-season gets an effect; estimates are weighted means of these effects.
  Hypotheses  H1  July NDVI anomaly: effect in shock seasons minus effect in non-shock seasons (shock = dry or heat)
              H2  peak NDVI anomaly: effect in calm seasons after a shock minus effect in calm seasons after a calm one
              H3  the H1 contrast for family B (land-use change) minus family A (management)
              Two-sided, Holm-adjusted over the three.
  Inference   cluster-robust by ERA5 cell, from each estimate's linear influence function (stratum means and a common
              effect per cohort x season x shock x family fitted); 50 km wild block bootstrap as a check.

Input   wp3_elms_effect/data/treatment.parquet; shared/data/s2/s2_parcel_year.parquet; shared/data/parcels/*;
        shared/data/weather/{cell_year_shocks,parcel_era5_cell}.parquet; data/raw/boundaries/itl1_2021_buc.geojson
Output  wp3_elms_effect/results/wp3_results.md, wp3_estimates.json, wp3_event_study.png (aggregates only)
        wp3_elms_effect/data/matched_sample.parquet (gitignored)
"""
import json, os, time
import numpy as np, pandas as pd
from scipy import stats
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
W3 = os.path.join(ROOT, 'wp3_elms_effect')
RES = os.path.join(W3, 'results')
SEASONS = np.arange(2017, 2027)
ENG = ['TLC', 'TLD', 'TLE', 'TLF', 'TLG', 'TLH', 'TLI', 'TLJ', 'TLK']
ITL = {'TLC': 'North East', 'TLD': 'North West', 'TLE': 'Yorkshire and the Humber', 'TLF': 'East Midlands',
       'TLG': 'West Midlands', 'TLH': 'East of England', 'TLI': 'London', 'TLJ': 'South East', 'TLK': 'South West'}
MAIN_SHOCK = dict(rain=-20, soil=-1.0, heat=5)
RNG = np.random.default_rng(20261011)
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)


# ---------------------------------------------------------------- data
def load():
    t = pd.read_parquet(os.path.join(W3, 'data', 'treatment.parquet'))
    pan = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'))
    pan = pan.merge(pd.read_parquet(os.path.join(D, 'parcels', 'parcel_risk.parquet')), on='parcref', how='left')
    cell = pd.read_parquet(os.path.join(D, 'weather', 'parcel_era5_cell.parquet'))[['parcref', 'cell_id_data']]
    t = t.merge(pan, on='parcref', how='left').merge(cell, on='parcref', how='left')
    t = t[t.cell_id_data.notna()].reset_index(drop=True)
    cols = ['parcref', 'year', 'ndvi_july_z', 'ndvi_peak_z', 'ndmi_july_z', 'ndre_july_z', 'integral_z', 'senesc_k'] + \
           [f'ndvi_p{k:02d}' for k in range(1, 13)]
    s2 = pd.read_parquet(os.path.join(D, 's2', 's2_parcel_year.parquet'), columns=cols)
    s2 = s2[s2.parcref.isin(t.parcref)]
    idx = pd.Series(np.arange(len(t)), index=t.parcref)
    s2['i'], s2['j'] = idx.reindex(s2.parcref).values, s2.year.values - SEASONS[0]
    Y = {}
    for c in ['ndvi_july_z', 'ndvi_peak_z', 'ndmi_july_z', 'ndre_july_z', 'integral_z', 'senesc_k']:
        m = np.full((len(t), len(SEASONS)), np.nan, dtype='float64')
        m[s2.i.values, s2.j.values] = s2[c].values
        Y[c] = m
    base = Y['senesc_k'][:, :4]                                       # senescence timing vs the parcel's 2017-2020 mean
    ok = (~np.isnan(base)).sum(1) >= 2
    Y['senesc_anom'] = np.where(ok[:, None], Y.pop('senesc_k') - np.nanmean(np.where(ok[:, None], base, 0), 1, keepdims=True), np.nan)
    pre = s2[s2.year <= 2020].groupby('i')[[f'ndvi_p{k:02d}' for k in range(1, 13)]].mean()
    t = t.join(pre)
    region(t)
    t['fz3'] = t.flood_zone.fillna(0).astype(int) == 3
    t['deep_peat'] = t.peat_class.fillna('').str.lower().str.contains('deep')
    return t, Y


def region(t):
    import geopandas as gpd
    eng = gpd.read_file(os.path.join(ROOT, 'data', 'raw', 'boundaries', 'itl1_2021_buc.geojson')).to_crs(27700)
    eng = eng[eng.ITL121CD.isin(ENG)][['ITL121CD', 'geometry']]
    pts = gpd.GeoDataFrame(index=t.index, geometry=gpd.points_from_xy(t.x, t.y), crs=27700)
    j = gpd.sjoin_nearest(pts, eng, how='left').groupby(level=0).ITL121CD.first()
    t['region'] = j.map(ITL).reindex(t.index).values


def shock_table(rain=-20, soil=-1.0, heat=5, rain_only=False, soil_only=False):
    s = pd.read_parquet(os.path.join(D, 'weather', 'cell_year_shocks.parquet'))
    r, m = s.spring_anom_pct <= rain, s.soil_moist_z <= soil
    dry = r if rain_only else m if soil_only else (r | m)
    s['shock'] = dry | (s.hot_days_28 >= heat)
    s['wet'] = s.wet_shock
    return s.set_index(['cell_id', 'year'])[['shock', 'wet']]


def crop_matrix(t):
    codes = {}
    out = np.full((len(t), len(SEASONS)), -1, dtype='int64')
    for j, y in enumerate(SEASONS):
        c = f'crop_{y}'
        if c in t:
            v = t[c].fillna('NA').values
            out[:, j] = [codes.setdefault(x, len(codes)) for x in v]
    return out


# ---------------------------------------------------------------- matching (section 7)
def scheme_intensity(t):
    p = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_schemes.parquet'), columns=['x', 'y', 'parcel_group'])
    allt, agt = cKDTree(p[['x', 'y']].values), cKDTree(p.loc[p.parcel_group == 'agreement', ['x', 'y']].values)
    xy = t[['x', 'y']].values
    n_all = allt.query_ball_point(xy, 1000, return_length=True) - 1
    n_agr = agt.query_ball_point(xy, 1000, return_length=True) - (t.G > 0).values
    return np.where(n_all > 0, n_agr / np.maximum(n_all, 1), 0.0)


def covariates(t):
    X = pd.DataFrame(index=t.index)
    for k in range(1, 13):
        c = f'ndvi_p{k:02d}'
        X[c + '_missing'] = t[c].isna().astype(float)
        X[c] = t[c].fillna(t.groupby('region')[c].transform('median')).fillna(t[c].median())
    yrs = range(2016, 2021)
    for y in yrs:
        X[f'cereal_{y}'] = t[f'cereal_{y}'].astype(float)
    X['cereal_share_1620'] = X[[f'cereal_{y}' for y in yrs]].mean(1)
    top = pd.concat([t[f'crop_{y}'] for y in yrs]).value_counts().index[:6]
    for y in yrs:
        for c in top:
            X[f'crop_{y}_{c}'] = (t[f'crop_{y}'] == c).astype(float)
    fz = t.flood_zone.fillna(0).astype(int)
    X['fz2'], X['fz3'] = (fz == 2).astype(float), (fz == 3).astype(float)
    for c in t.peat_class.dropna().unique():
        X[f'peat_{c}'] = (t.peat_class == c).astype(float)
    X['scheme_1km'] = t.scheme_1km
    return X


def smd(X, treat, w=None):
    w = np.ones(len(X)) if w is None else w
    a, b = X[treat], X[~treat]; wb = w[~treat]
    mb = (b.mul(wb, axis=0)).sum() / wb.sum()
    sd = np.sqrt((a.var() + b.var()) / 2).replace(0, np.nan)
    return ((a.mean() - mb) / sd).abs()


def match(t):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    X = covariates(t)
    treat = (t.G > 0).values
    ctrl_count = np.zeros(len(t)); keep_t = np.zeros(len(t), bool)
    ps = np.full(len(t), np.nan)
    for r, g in t.groupby('region'):
        ix = g.index.values
        Xs = StandardScaler().fit_transform(X.loc[ix].values)
        m = LogisticRegression(C=1.0, max_iter=1000).fit(Xs, treat[ix])
        lp = m.decision_function(Xs); ps[ix] = lp
        tr, co = ix[treat[ix]], ix[~treat[ix]]
        if len(co) == 0:
            continue
        cal = 0.2 * lp.std()
        d, k = cKDTree(ps[co][:, None]).query(ps[tr][:, None], k=1)
        ok = d <= cal
        keep_t[tr[ok]] = True
        np.add.at(ctrl_count, co[k[ok]], 1)
    sample = keep_t | (ctrl_count > 0)
    before = smd(X, treat)
    after = smd(X[sample], treat[sample], ctrl_count[sample] + treat[sample])
    bal = pd.DataFrame({'smd_before': before, 'smd_after': after})
    return sample, bal, ps


# ---------------------------------------------------------------- estimator
def blocks(Y, G, cell, crop, use_crop, seasons, fam, pmask=None, tmax=None, universal=False):
    """Group-time 2x2 comparisons, aggregated to treated (stratum x family) and control (stratum) cells.
    pmask: parcels included; tmax: per-parcel last usable season for treated rows (placebo)."""
    n = len(G)
    pmask = np.ones(n, bool) if pmask is None else pmask
    cohorts = sorted(set(G[(G > 0) & pmask]) & set(seasons))
    TR, CO = [], []
    for g in cohorts:
        for t in seasons:
            e = t - g
            b = g - 1 if (e >= 0 or universal) else t - 1
            if b not in seasons or t == b:
                continue
            jt, jb = t - SEASONS[0], b - SEASONS[0]
            dy = Y[:, jt] - Y[:, jb]
            ok = pmask & ~np.isnan(dy)
            tr = ok & (G == g)
            if tmax is not None:
                tr &= (t < tmax) & (b < tmax)
            co = ok & ((G == 0) | (G > max(t, b))) & (G != g)     # untreated in both seasons compared
            if not tr.any() or not co.any():
                continue
            key = cell * 1000 + (crop[:, jt] + 1 if use_crop else 0)
            c = pd.DataFrame({'key': key[co], 'cell': cell[co], 'dy': dy[co]}).groupby('key').agg(
                cell=('cell', 'first'), nC=('dy', 'size'), meanC=('dy', 'mean'))
            r = pd.DataFrame({'key': key[tr], 'cell': cell[tr], 'fam': fam[tr], 'dy': dy[tr]}).groupby(['key', 'fam']).agg(
                cell=('cell', 'first'), nT=('dy', 'size'), sumY=('dy', 'sum')).reset_index()
            r = r[r.key.isin(c.index)]
            c = c[c.index.isin(r.key)].reset_index()
            r['g'], r['t'], r['e'] = g, t, e
            c['g'], c['t'] = g, t
            TR.append(r); CO.append(c)
    TR, CO = pd.concat(TR, ignore_index=True), pd.concat(CO, ignore_index=True)
    TR = TR.merge(CO[['g', 't', 'key', 'meanC']], on=['g', 't', 'key'])
    TR['tau_sum'] = TR.sumY - TR.nT * TR.meanC
    return TR, CO


def attach_shocks(TR, cells, sh):
    cid = cells[TR.cell.values]
    get = lambda y, col: sh[col].reindex(pd.MultiIndex.from_arrays([cid, y])).fillna(False).values.astype(bool)
    TR['shock'] = get(TR.t.values, 'shock')
    TR['prev'] = get(TR.t.values - 1, 'shock')
    TR['wet'] = get(TR.t.values, 'wet')
    return TR


class Est:
    """Weighted means of parcel-season effects, with cluster-robust covariance from linear influence functions."""

    def __init__(self, TR, CO, cluster_of_cell):
        self.TR, self.CO = TR.copy(), CO
        cat = ['g', 't', 'fam', 'shock', 'prev']
        g = TR.groupby(cat)
        self.TR['tau_hat'] = (g.tau_sum.transform('sum') / g.nT.transform('sum')).values
        s = TR.assign(adj=TR.sumY - TR.nT * self.TR.tau_hat).groupby(['g', 't', 'key']).agg(adj=('adj', 'sum'), nT=('nT', 'sum'))
        c = CO.set_index(['g', 't', 'key'])
        s = s.join(c[['nC', 'meanC', 'cell']])
        s['mu'] = (s.adj + s.nC * s.meanC) / (s.nT + s.nC)
        self.TR['mu'] = s.mu.reindex(pd.MultiIndex.from_frame(TR[['g', 't', 'key']])).values
        self.TR['R'] = self.TR.sumY - self.TR.nT * (self.TR.mu + self.TR.tau_hat)
        self.TR['Cres'] = self.TR.meanC - self.TR.mu          # per control obs, stratum level
        self.clu = cluster_of_cell[self.TR.cell.values]
        self.first = ~self.TR[['g', 't', 'key']].duplicated().values
        self.gkey = [self.TR.g.values, self.TR.t.values, self.TR.key.values]

    def weights(self, pos, neg=None):
        TR = self.TR
        w = np.zeros(len(TR))
        pos = np.asarray(pos, bool)
        npos = TR.nT.values[pos].sum(); w[pos] = 1 / npos if npos else 0
        if neg is not None:
            neg = np.asarray(neg, bool)
            nneg = TR.nT.values[neg].sum(); w[neg] -= 1 / nneg if nneg else 0
        return w

    def run(self, W, clusters=None):
        """W: list of weight vectors. Returns estimates, covariance, n clusters, influence matrix."""
        TR = self.TR
        clu = self.clu if clusters is None else clusters
        th = np.array([(w * TR.tau_sum).sum() for w in W])
        # influence per row: treated residuals + control residuals of the same stratum (weights summed in stratum)
        inf = []
        for w in W:
            wt = w * TR.nT
            sw = pd.Series(wt).groupby(self.gkey).transform('sum').values
            v = w * TR.R.values - np.where(self.first, sw * TR.Cres.values, 0.0)
            inf.append(pd.Series(v).groupby(clu).sum())
        I = pd.concat(inf, axis=1).fillna(0).values
        G = len(I)
        V = I.T @ I * G / (G - 1)
        return th, V, G, I


def z_p(th, se):
    z = th / se
    return z, 2 * stats.norm.sf(np.abs(z))


def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, min(1, (m - r) * p[i])); adj[i] = run
    return adj


# ---------------------------------------------------------------- analysis pieces
class Data:
    def __init__(self):
        t, Y = load()
        log('parcels', len(t))
        t['scheme_1km'] = scheme_intensity(t)
        self.t, self.Y = t, Y
        self.cells = np.array(sorted(t.cell_id_data.unique()))
        self.cell = np.searchsorted(self.cells, t.cell_id_data.values)
        self.crop = crop_matrix(t)
        self.G = t.G.values.astype(int)
        self.fam = t.family.values
        xy = t.groupby(self.cell)[['x', 'y']].mean()
        b = (xy.x // 50000).astype(int) * 1000 + (xy.y // 50000).astype(int)
        self.block50 = b.reindex(range(len(self.cells))).values
        self.cluster = np.arange(len(self.cells))

    def est(self, y='ndvi_july_z', use_crop=True, seasons=range(2017, 2026), pmask=None, shock=None, G=None, Ymat=None,
            fam=None, tmax=None, cell=None, crop=None, cells=None, cluster=None, universal=False):
        TR, CO = blocks(self.Y[y] if Ymat is None else Ymat, self.G if G is None else G,
                        self.cell if cell is None else cell, self.crop if crop is None else crop, use_crop,
                        list(seasons), self.fam if fam is None else fam, pmask, tmax, universal)
        TR = attach_shocks(TR, self.cells if cells is None else cells, shock_table(**(shock or MAIN_SHOCK)))
        return Est(TR, CO, self.cluster if cluster is None else cluster)


def h1(E, fam=None):
    TR = E.TR; post = TR.e >= 0
    if fam is not None:
        post &= TR.fam.isin(fam if isinstance(fam, (list, tuple)) else [fam])
    return [E.weights(post & TR.shock, post & ~TR.shock), E.weights(post & TR.shock), E.weights(post & ~TR.shock),
            E.weights(post)]


def h2(E):
    TR = E.TR; calm = (TR.e >= 0) & ~TR.shock
    return [E.weights(calm & TR.prev, calm & ~TR.prev), E.weights(calm & TR.prev), E.weights(calm & ~TR.prev)]


def h3(E):
    TR = E.TR; post = TR.e >= 0
    B, A = post & (TR.fam == 'B'), post & (TR.fam == 'A')
    return [E.weights(B & TR.shock, B & ~TR.shock) - E.weights(A & TR.shock, A & ~TR.shock)]


def row(name, th, V, i=0, G=None, n=None, extra=''):
    se = np.sqrt(V[i, i]); z, p = z_p(th[i], se)
    return dict(name=name, est=float(th[i]), se=float(se), lo=float(th[i] - 1.96 * se), hi=float(th[i] + 1.96 * se),
                p=float(p), clusters=G, n=n, note=extra)


def n_obs(E, w):
    return int(E.TR.nT[w != 0].sum())


def main():
    d = Data()
    t = d.t
    log('matching')
    sample, bal, ps = match(t)
    pd.DataFrame({'parcref': t.parcref, 'in_matched_sample': sample, 'logit_ps': ps}).to_parquet(
        os.path.join(W3, 'data', 'matched_sample.parquet'), index=False)
    out = {'sample': {'treated_all': int((d.G > 0).sum()), 'control_all': int((d.G == 0).sum()),
                      'treated_matched': int(((d.G > 0) & sample).sum()), 'control_matched': int(((d.G == 0) & sample).sum()),
                      'max_smd_before': float(bal.smd_before.max()), 'max_smd_after': float(bal.smd_after.max()),
                      'n_cov_smd_after_over_0.1': int((bal.smd_after > 0.1).sum())}}
    log(out['sample'])
    M = sample
    res = []

    # ---- confirmatory: H1, H2, H3 on the matched sample, main specification
    log('confirmatory')
    E1 = d.est('ndvi_july_z', pmask=M)
    W = h1(E1) + h3(E1)
    th, V, G, I1 = E1.run(W)
    conf = [row('H1 July NDVI: shock minus non-shock effect', th, V, 0, G, n_obs(E1, W[3])),
            row('H3 H1 contrast, family B minus family A', th, V, 4, G, n_obs(E1, W[4]))]
    comp = [row('  effect in shock seasons', th, V, 1, G, n_obs(E1, W[1])),
            row('  effect in non-shock seasons', th, V, 2, G, n_obs(E1, W[2])),
            row('  effect, all post-entry seasons', th, V, 3, G, n_obs(E1, W[3]))]
    E2 = d.est('ndvi_peak_z', pmask=M)
    W2 = h2(E2)
    th2, V2, G2, _ = E2.run(W2)
    conf.insert(1, row('H2 peak NDVI: calm-after-shock minus calm-after-calm effect', th2, V2, 0, G2, n_obs(E2, W2[1]) + n_obs(E2, W2[2])))
    comp += [row('  H2 effect after a shock', th2, V2, 1, G2, n_obs(E2, W2[1])),
             row('  H2 effect after a calm season', th2, V2, 2, G2, n_obs(E2, W2[2]))]
    for r, a in zip(conf, holm([c['p'] for c in conf])):
        r['p_holm'] = float(a)
    out['confirmatory'], out['components'] = conf, comp
    # family components for H3
    fam_rows = []
    for f in ['A', 'B', 'C']:
        th_f, V_f, G_f, _ = E1.run(h1(E1, f)[:1])
        fam_rows.append(row(f'H1 contrast, family {f}' + (' (not tested)' if f == 'C' else ''), th_f, V_f, 0, G_f,
                            n_obs(E1, h1(E1, f)[3])))
    out['families'] = fam_rows
    # 50 km wild block bootstrap on the same influence functions
    blk = d.block50[E1.TR.cell.values]
    _, Vb, Gb, Ib = E1.run(W, clusters=blk)
    _, Vb2, Gb2, Ib2 = E2.run(W2, clusters=d.block50[E2.TR.cell.values])
    def wild(I, k, B=1999):
        r = RNG.choice([-1.0, 1.0], size=(B, I.shape[0]))
        return float(np.std(r @ I[:, k]))
    out['block50'] = {'clusters': int(Gb), 'H1_se': wild(Ib, 0), 'H2_se': wild(Ib2, 0), 'H3_se': wild(Ib, 4),
                      'H1_se_cell': float(np.sqrt(V[0, 0])), 'H2_se_cell': float(np.sqrt(V2[0, 0])), 'H3_se_cell': float(np.sqrt(V[4, 4]))}

    # ---- check 1: pre-trends (event time -4..3), overall effect and shock contrast
    log('event study')
    ev = []
    TR = E1.TR
    es = list(range(-4, 4))
    We = [E1.weights(TR.e == e) for e in es] + [E1.weights((TR.e == e) & TR.shock, (TR.e == e) & ~TR.shock) for e in es]
    the, Ve, Ge, _ = E1.run(We)
    for k, e in enumerate(es):
        ev.append(dict(e=e, att=float(the[k]), se=float(np.sqrt(Ve[k, k])), contrast=float(the[k + 8]),
                       contrast_se=float(np.sqrt(Ve[k + 8, k + 8])), n=n_obs(E1, We[k])))
    def wald(ix):
        b = the[ix]; v = Ve[np.ix_(ix, ix)]
        ok = np.isfinite(b) & (np.diag(v) > 0); b, v = b[ok], v[np.ix_(ok, ok)]
        s = float(b @ np.linalg.pinv(v) @ b); return s, int(ok.sum()), float(stats.chi2.sf(s, ok.sum()))
    out['event'] = ev
    out['pretrend'] = {'att': wald([0, 1, 2, 3]), 'contrast': wald([8, 9, 10, 11])}

    # ---- checks
    log('checks')
    chk = []
    def h1h2(name, E1x=None, E2x=None, **kw):
        E1x = E1x or d.est('ndvi_july_z', **kw)
        a, Va, Ga, _ = E1x.run(h1(E1x)[:1] + h3(E1x))
        r = row(name, a, Va, 0, Ga, n_obs(E1x, h1(E1x)[3]))
        r['H3'], r['H3_se'] = float(a[1]), float(np.sqrt(Va[1, 1]))
        if E2x is not False:
            E2x = E2x or d.est('ndvi_peak_z', **kw)
            b, Vb_, _, _ = E2x.run(h2(E2x)[:1])
            r['H2'], r['H2_se'] = float(b[0]), float(np.sqrt(Vb_[0, 0]))
        chk.append(r); log(name, round(r['est'], 4), round(r['se'], 4))

    # 2 placebo entry two seasons earlier, using only seasons before real entry
    Gp = np.where(d.G > 0, d.G - 2, 0)
    tmax = np.where(d.G > 0, d.G, 9999)
    h1h2('Placebo: entry two seasons earlier', G=Gp, tmax=tmax, pmask=M, seasons=range(2017, 2026))
    # 3 synthetic +0.2 SD shock-season effect injected into random never-treated parcels
    nev = np.where((d.G == 0) & M)[0]
    pick = RNG.random(len(nev)) < 0.3
    Gs = np.zeros_like(d.G); dist = d.G[(d.G > 0) & (d.G <= 2025) & M]
    Gs[nev[pick]] = RNG.choice(dist, pick.sum())
    sh = shock_table(**MAIN_SHOCK).shock
    S = sh.reindex(pd.MultiIndex.from_product([d.cells, SEASONS])).fillna(False).values.reshape(len(d.cells), len(SEASONS))[d.cell]
    Ysyn = d.Y['ndvi_july_z'].copy()
    post = (Gs[:, None] > 0) & (SEASONS[None, :] >= Gs[:, None])
    Ysyn[post & S] += 0.2
    pm = (d.G == 0) & M
    Es = d.est(Ymat=Ysyn, G=Gs, pmask=pm)
    a, Va, Ga, _ = Es.run(h1(Es)[:1])
    chk.append(row('Synthetic: injected +0.20 in shock seasons (should recover 0.20)', a, Va, 0, Ga, n_obs(Es, h1(Es)[3])))
    # 4 data quality
    h1h2('Excluding 2017', pmask=M, seasons=range(2018, 2026))
    yrs = [y for y in range(2016, 2026) if y != 2020]
    obs = t[[f'crop_{y}' for y in yrs]].notna().sum(1)
    cer = t[[f'cereal_{y}' for y in yrs]].fillna(False).astype(int).sum(1)
    h1h2('Cereal land defined without CROME 2020', pmask=M & (cer / obs.clip(lower=1) >= 0.5).values)
    # 5 shock thresholds
    for lab, sk in [('rain -15%', dict(rain=-15)), ('rain -25%', dict(rain=-25)), ('rain -30%', dict(rain=-30)),
                    ('soil -0.75 SD', dict(soil=-0.75)), ('soil -1.25 SD', dict(soil=-1.25)),
                    ('rain only', dict(rain_only=True)), ('soil moisture only', dict(soil_only=True)),
                    ('heat 3 days', dict(heat=3)), ('heat 8 days', dict(heat=8))]:
        h1h2(f'Shock threshold: {lab}', pmask=M, shock={**MAIN_SHOCK, **sk})
    # 6 spatial scale: 5 km hexagons
    hx, peak = hexagons(d, M)
    h1h2('5 km hexagon averages (cell x season strata)', E1x=d.est(**hx), E2x=d.est(**{**hx, 'Ymat': peak}))
    # 7 flood and peat
    h1h2('Excluding Flood Zone 3 and deep peat', pmask=M & ~t.fz3.values & ~t.deep_peat.values)
    # stated versions
    h1h2('2026 version: seasons 2017-2026, cell x season strata (no crop)', pmask=M, use_crop=False, seasons=range(2017, 2027))
    h1h2('Unmatched full sample', pmask=None)
    out['checks'] = chk

    # ---- exploratory (labelled as such)
    log('exploratory')
    exp = []
    def contrast(name, E, sel=None):
        TR = E.TR; post = (TR.e >= 0) if sel is None else (TR.e >= 0) & sel
        w = E.weights(post & TR.shock, post & ~TR.shock)
        if not (post & TR.shock).any() or not (post & ~TR.shock).any():
            return
        a, Va, Ga, _ = E.run([w]); log(name, round(a[0], 4)); exp.append(row(name, a, Va, 0, Ga, n_obs(E, E.weights(post))))
    TR = E1.TR
    for g in sorted(TR.g.unique()):
        contrast(f'Cohort first season {g}', E1, TR.g == g)
    reg_of_cell = t.groupby(d.cell).region.agg(lambda s: s.mode().iat[0])
    tr_reg = reg_of_cell.reindex(TR.cell.values).values
    for r in sorted(reg_of_cell.unique()):
        contrast(f'Region: {r}', E1, pd.Series(tr_reg == r, index=TR.index))
    fp = (t.fz3 | t.deep_peat).values
    contrast('Flood Zone 3 or deep peat', d.est('ndvi_july_z', pmask=M & fp))
    contrast('Not Flood Zone 3 or deep peat', d.est('ndvi_july_z', pmask=M & ~fp))
    Esoh = d.est('ndvi_july_z', pmask=M, fam=t.family_soh_a.values)
    a, Va, Ga, _ = Esoh.run(h3(Esoh)); exp.append(row('H3 with SOH actions counted as A', a, Va, 0, Ga, None))
    for y, lab in [('ndmi_july_z', 'July NDMI (canopy water)'), ('ndre_july_z', 'July NDRE (chlorophyll)'),
                   ('integral_z', 'Seasonal NDVI integral'), ('senesc_anom', 'Senescence timing (half-months)')]:
        contrast(f'Secondary outcome: {lab}', d.est(y, pmask=M))
    E2c = E2.TR
    comp_ = (E2c.e >= 0) & E2c.shock & E2c.prev
    calm = (E2c.e >= 0) & ~E2c.shock & ~E2c.prev
    a, Va, Ga, _ = E2.run([E2.weights(comp_, calm)])
    exp.append(row('Compound shock (shock after shock), peak NDVI vs calm-after-calm', a, Va, 0, Ga, n_obs(E2, E2.weights(comp_))))
    a, Va, Ga, _ = E1.run([E1.weights((TR.e >= 0) & TR.wet, (TR.e >= 0) & ~TR.wet)])
    exp.append(row('Wet winter (waterlogging) vs not, July NDVI (Sentinel-2 only)', a, Va, 0, Ga, None))
    out['exploratory'] = exp
    out['balance'] = bal.sort_values('smd_before', ascending=False).head(15).round(3).reset_index().rename(columns={'index': 'covariate'}).to_dict('records')
    json.dump(out, open(os.path.join(RES, 'wp3_estimates.json'), 'w'), indent=1, default=float)
    report(out)
    figure(out)
    log('done')


def hexagons(d, M, size=5000):
    """Hexagon x cohort x family units: mean outcome per season; cell = most common cell of the hexagon's parcels."""
    t = d.t
    q = (2 / 3 * t.x.values) / size
    r = (-1 / 3 * t.x.values + np.sqrt(3) / 3 * t.y.values) / size
    x, z = q, r; y = -x - z
    rx, ry, rz = np.round(x), np.round(y), np.round(z)
    dx, dy, dz = np.abs(rx - x), np.abs(ry - y), np.abs(rz - z)
    rx = np.where((dx > dy) & (dx > dz), -ry - rz, rx)
    rz = np.where(~((dx > dy) & (dx > dz)) & ~(dy > dz), -rx - ry, rz)
    hexid = (rx.astype(np.int64) * 100000 + rz.astype(np.int64))
    u = pd.DataFrame({'hex': hexid, 'G': d.G, 'fam': d.fam, 'cell': d.cell})[M]
    key = u.groupby(['hex', 'G', 'fam']).ngroup().values
    ug = u.assign(k=key).groupby('k').agg(G=('G', 'first'), fam=('fam', 'first'), hex=('hex', 'first'))
    hcell = u.groupby('hex').cell.agg(lambda s: s.mode().iat[0])
    Ym = d.Y['ndvi_july_z'][M]
    Ysum = np.zeros((len(ug), len(SEASONS))); Yn = np.zeros_like(Ysum)
    ok = ~np.isnan(Ym)
    np.add.at(Ysum, key, np.where(ok, Ym, 0)); np.add.at(Yn, key, ok)
    Yh = np.where(Yn > 0, Ysum / np.maximum(Yn, 1), np.nan)
    Yp = d.Y['ndvi_peak_z'][M]; okp = ~np.isnan(Yp)
    Ps = np.zeros_like(Ysum); Pn = np.zeros_like(Ysum)
    np.add.at(Ps, key, np.where(okp, Yp, 0)); np.add.at(Pn, key, okp)
    peak = np.where(Pn > 0, Ps / np.maximum(Pn, 1), np.nan)
    return dict(Ymat=Yh, G=ug.G.values, fam=ug.fam.values, cell=hcell.reindex(ug.hex).values,
                crop=np.zeros((len(ug), len(SEASONS)), int), use_crop=False), peak


def report(o):
    f = lambda r: f"| {r['name']} | {r['est']:+.3f} | {r['se']:.3f} | [{r['lo']:+.3f}, {r['hi']:+.3f}] | {r['p']:.3f} |"
    s = o['sample']
    L = ['# WP3 results: do agreements buffer cereal land against weather shocks?', '',
         'Run of the frozen pre-registration ([preregistration.md](preregistration.md), commit `b0f232b`). Outcomes are '
         'Sentinel-2 anomalies in standard deviations of the parcel\'s own 2017–2020 seasons; positive = agreement land '
         'did better. Standard errors clustered by ERA5 cell. All numbers are aggregates; no parcel is identified.', '',
         '## Sample', '',
         f"- Agreement parcels (entering 2021–2026): {s['treated_all']:,}; matched: {s['treated_matched']:,}",
         f"- Never-treated parcels: {s['control_all']:,}; used as matches: {s['control_matched']:,}",
         f"- Balance (standardised mean difference): largest {s['max_smd_before']:.2f} before matching, "
         f"{s['max_smd_after']:.2f} after; covariates above 0.1 after matching: {s['n_cov_smd_after_over_0.1']}", '',
         '## Confirmatory tests (Holm-adjusted over three)', '',
         '| Test | estimate | SE | 95% CI | p | p (Holm) | parcel-seasons |', '|---|---|---|---|---|---|---|'] + \
        [f"| {r['name']} | {r['est']:+.3f} | {r['se']:.3f} | [{r['lo']:+.3f}, {r['hi']:+.3f}] | {r['p']:.3f} | {r['p_holm']:.3f} | {r['n']:,} |"
         for r in o['confirmatory']] + \
        ['', 'Components:', '', '| | estimate | SE | 95% CI | p |', '|---|---|---|---|---|'] + [f(r) for r in o['components']] + \
        ['', 'H1 contrast by option family:', '', '| | estimate | SE | 95% CI | p |', '|---|---|---|---|---|'] + [f(r) for r in o['families']]
    b = o['block50']
    L += ['', f"50 km wild block bootstrap ({b['clusters']} blocks): SE H1 {b['H1_se']:.3f} (cell-clustered {b['H1_se_cell']:.3f}), "
          f"H2 {b['H2_se']:.3f} ({b['H2_se_cell']:.3f}), H3 {b['H3_se']:.3f} ({b['H3_se_cell']:.3f}).", '',
          '## Check 1: event study and pre-trends (July NDVI)', '',
          '| event time | effect | SE | shock minus non-shock | SE | parcel-seasons |', '|---|---|---|---|---|---|'] + \
         [f"| {r['e']:+d} | {r['att']:+.3f} | {r['se']:.3f} | {r['contrast']:+.3f} | {r['contrast_se']:.3f} | {r['n']:,} |" for r in o['event']]
    pa, pc = o['pretrend']['att'], o['pretrend']['contrast']
    L += ['', f"Joint test of event times −4 to −1: effect χ²({pa[1]}) = {pa[0]:.1f}, p = {pa[2]:.3f}; "
          f"shock contrast χ²({pc[1]}) = {pc[0]:.1f}, p = {pc[2]:.3f}.", '',
          '## Checks decided in advance (H1 contrast; H2 and H3 alongside)', '',
          '| Check | H1 | SE | p | H2 | SE | H3 | SE |', '|---|---|---|---|---|---|---|---|']
    for r in o['checks']:
        g = lambda k: f"{r[k]:+.3f}" if k in r else '–'
        gs = lambda k: f"{r[k]:.3f}" if k in r else '–'
        L.append(f"| {r['name']} | {r['est']:+.3f} | {r['se']:.3f} | {r['p']:.3f} | {g('H2')} | {gs('H2_se')} | {g('H3')} | {gs('H3_se')} |")
    L += ['', '## Exploratory (not confirmatory; no multiple-testing correction)', '',
          '| Analysis | estimate | SE | 95% CI | p |', '|---|---|---|---|---|'] + [f(r) for r in o['exploratory']]
    L += ['', 'Not yet run: the embedding (AlphaEarth) version of the matching, waiting for the national extraction; the '
          'Sentinel-1 waterlogging analysis, waiting for the national Sentinel-1 panel; the crop-controlled 2026 season, '
          'waiting for CROME 2026.']
    open(os.path.join(RES, 'wp3_results.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


def figure(o):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    ev = pd.DataFrame(o['event'])
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
    for a, (col, se, title) in zip(ax, [('att', 'se', 'Agreement effect on July NDVI, by season since entry'),
                                       ('contrast', 'contrast_se', 'Extra effect in shock seasons (H1), by season since entry')]):
        a.axhline(0, color='#888', lw=0.8); a.axvline(-0.5, color='#bbb', lw=0.8, ls='--')
        a.errorbar(ev.e, ev[col], yerr=1.96 * ev[se], fmt='o', color='#2E6B4F', ecolor='#7FA88F', capsize=3)
        a.set_title(title, loc='left', fontsize=11, fontweight='bold'); a.set_xlabel('season relative to first full season (0)')
        a.set_ylabel('SD of the parcel\'s own 2017–2020 normal'); a.spines[['top', 'right']].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(RES, 'wp3_event_study.png'), dpi=180)


if __name__ == '__main__':
    main()

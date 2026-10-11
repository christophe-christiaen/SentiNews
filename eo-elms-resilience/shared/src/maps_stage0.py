"""Maps from the Stage 0 data: cereal land and agreements, entry wave, weather shocks, Sentinel-2 drought response.
Output: results/maps/stage0_*.png (aggregated to hexagons / weather cells; no individual farms shown)."""
import os
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
OUT = os.path.join(ROOT, 'results', 'maps')
BG, INK, BODY, RULE = '#F6F4EE', '#1C2620', '#4A554E', '#D6D0C2'
GREEN, OCHRE = '#2F6B4F', '#9A5F14'
plt.rcParams.update({'font.family': 'Helvetica', 'font.size': 11, 'text.color': INK, 'axes.edgecolor': BG,
                     'figure.facecolor': BG, 'axes.facecolor': BG, 'savefig.facecolor': BG})
ENG = ['TLC', 'TLD', 'TLE', 'TLF', 'TLG', 'TLH', 'TLI', 'TLJ', 'TLK']
GRID = 5000          # hexagon size (m)


def england():
    g = gpd.read_file(os.path.join(ROOT, 'data', 'raw', 'boundaries', 'itl1_2021_buc.geojson')).to_crs(27700)
    return g[g.ITL121CD.isin(ENG)]


def frame(ax, eng, title, sub=None):
    eng.plot(ax=ax, facecolor='#ECE9E1', edgecolor='none', zorder=0)
    eng.boundary.plot(ax=ax, color='white', linewidth=0.8, zorder=3)
    ax.set_xlim(130_000, 660_000); ax.set_ylim(0, 670_000); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, loc='left', fontsize=15, fontweight='bold', color=INK, pad=6)
    if sub:
        ax.text(0, 1.0, sub, transform=ax.transAxes, fontsize=10.5, color=BODY, va='top')


def hexmap(ax, x, y, c=None, cmap='Greens', vmin=None, vmax=None, mincnt=1, norm=None, reduce=np.mean):
    return ax.hexbin(x, y, C=c, gridsize=int(530_000 / GRID), extent=(130_000, 660_000, 0, 670_000), cmap=cmap,
                     vmin=vmin, vmax=vmax, mincnt=mincnt, linewidths=0, reduce_C_function=reduce, norm=norm, zorder=2)


def cbar(fig, ax, h, label, ticks=None, fmt=None):
    cb = fig.colorbar(h, ax=ax, orientation='horizontal', fraction=0.035, pad=0.01, shrink=0.75, ticks=ticks, format=fmt)
    cb.outline.set_visible(False); cb.ax.tick_params(labelsize=9, colors=BODY, length=0)
    cb.set_label(label, fontsize=10, color=BODY)


def save(fig, name, note):
    fig.text(0.01, 0.01, note, fontsize=8.5, color=BODY)
    p = os.path.join(OUT, name); fig.savefig(p, dpi=200, bbox_inches='tight'); plt.close(fig); print('wrote', p)


def map_agreements(t, eng):
    c = t[t.cereal_land]
    fig, axs = plt.subplots(1, 2, figsize=(13, 7.6))
    h = hexmap(axs[0], c.x, c.y, cmap=LinearSegmentedColormap.from_list('d', ['#E3E8DF', '#8FAE8F', GREEN, '#163527']),
               reduce=len, mincnt=3)
    frame(axs[0], eng, 'Where England grows cereals', 'Cereal-land parcels per 5 km hexagon (cereal in ≥ half of 2016–2025)')
    cbar(fig, axs[0], h, 'parcels')
    ag = c.parcel_group.isin(['agreement', 'no agreement'])
    cc = c[ag]
    h2 = hexmap(axs[1], cc.x, cc.y, c=(cc.parcel_group == 'agreement').astype(float),
                cmap=LinearSegmentedColormap.from_list('a', ['#C9A36B', '#EFE7D6', '#9BC0A6', GREEN]), vmin=0, vmax=1, mincnt=5)
    frame(axs[1], eng, 'How much of it is under an agreement', 'Share of cereal parcels with an area-based CS or SFI option')
    cbar(fig, axs[1], h2, 'share under agreement', ticks=[0, .25, .5, .75, 1], fmt=lambda v, _: f'{v:.0%}')
    save(fig, 'stage0_cereal_land_agreements.png',
         f'{len(c):,} cereal-land parcels (RPA parcel points × CROME 2016–2025); {int((c.parcel_group == "agreement").sum()):,} under agreements, '
         f'{int((c.parcel_group == "no agreement").sum()):,} never entered. Hexagons with < 5 parcels hidden.')


def map_entry(t, eng):
    a = t[t.cereal_land & (t.parcel_group == 'agreement') & t.entry_year.notna()]
    cohorts = [('Before 2023', a.entry_year < 2023), ('2023', a.entry_year == 2023), ('2024', a.entry_year == 2024),
               ('2025–26', a.entry_year >= 2025)]
    fig, axs = plt.subplots(1, 4, figsize=(17, 5.6))
    cmap = LinearSegmentedColormap.from_list('e', ['#F0E4CF', '#D7A869', OCHRE, '#5E3A0C'])
    for ax, (lab, m) in zip(axs, cohorts):
        s = a[m]
        h = hexmap(ax, s.x, s.y, cmap=cmap, reduce=len, mincnt=1, vmin=1, vmax=150)
        frame(ax, eng, f'{lab}', f'{len(s):,} cereal parcels entered')
    cbar(fig, axs, h, 'cereal parcels entering a scheme per 5 km hexagon (capped at 150)')
    save(fig, 'stage0_entry_wave.png', 'Year of the earliest area-based CS or SFI option on cereal-land parcels. The 2024 SFI expansion is the main entry wave.')


def map_weather(eng):
    W = os.path.join(D, 'weather')
    m = pd.read_parquet(os.path.join(W, 'era5land_monthly.parquet'))
    h = pd.read_parquet(os.path.join(W, 'era5land_heatdays.parquet'))
    spring = m[m.month.between(3, 7)].groupby(['cell_id', 'year']).precip_mm.sum().unstack()
    normal = spring.loc[:, 1991:2020].mean(axis=1)
    anom = (spring.div(normal, axis=0) - 1) * 100
    from shapely.geometry import box
    ij = np.array([[int(v) for v in c.split('_')] for c in anom.index]) * 0.1
    cells = gpd.GeoDataFrame({'cell_id': anom.index}, geometry=[box(a - .05, b - .05, a + .05, b + .05) for a, b in ij],
                             crs=4326).to_crs(27700)
    hot = h.set_index(['cell_id', 'year']).hot_days_28.unstack().reindex(anom.index)
    fig, axs = plt.subplots(1, 3, figsize=(17, 6.6))
    norm = TwoSlopeNorm(vmin=-60, vcenter=0, vmax=40)
    rb = LinearSegmentedColormap.from_list('r', ['#7A3B0A', '#C98A3E', '#F2E6CF', '#A9C7D8', '#3E6E8E'])
    for ax, yr in zip(axs[:2], (2025, 2026)):
        frame(ax, eng, f'Spring {yr}: rainfall', 'March–July rainfall vs 1991–2020, cereal areas')
        cells.assign(v=anom[yr].values).plot(ax=ax, column='v', cmap=rb, norm=norm, linewidth=0, zorder=2)
        sc = matplotlib.cm.ScalarMappable(norm=norm, cmap=rb)
    cbar(fig, axs[:2], sc, '% vs normal', ticks=[-60, -40, -20, 0, 20, 40])
    hc = LinearSegmentedColormap.from_list('h', ['#F4EBDD', '#E0A05A', '#B5521B', '#6E1F0A'])
    frame(axs[2], eng, 'Summer 2026: heat', 'Days ≥ 28 °C, June–August')
    cells.assign(v=hot[2026].values).plot(ax=axs[2], column='v', cmap=hc, vmin=0, vmax=20, linewidth=0, zorder=2)
    sc2 = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(0, 20), cmap=hc)
    cbar(fig, axs[2], sc2, 'days')
    save(fig, 'stage0_weather_shocks_2025_2026.png', 'ERA5-Land (Copernicus/ECMWF) via Earth Engine, 0.1° cells containing cereal parcels. 2026 data to September.')


def map_s2(t, eng):
    f = os.path.join(D, 's2', 'parcels', '30UXD', '2022.parquet')
    if not os.path.exists(f):
        return
    d = pd.read_parquet(f)
    d['m'] = d.date.dt.month
    may = d[d.m == 5].groupby('parcref').ndvi.median(); jul = d[d.m == 7].groupby('parcref').ndvi.median()
    drop = (jul - may).dropna()
    p = t.set_index('parcref').loc[drop.index, ['x', 'y']]
    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    eng.plot(ax=ax, facecolor='#ECE9E1', edgecolor='white', linewidth=0.8, zorder=0)
    h = ax.hexbin(p.x, p.y, C=drop.values, gridsize=70, cmap=LinearSegmentedColormap.from_list('n', ['#6E1F0A', '#C98A3E', '#F2E6CF', '#9BC0A6', GREEN]),
                  vmin=-0.6, vmax=0.1, mincnt=3, linewidths=0, reduce_C_function=np.median, zorder=2)
    pad = 5000
    ax.set_xlim(p.x.min() - pad, p.x.max() + pad); ax.set_ylim(p.y.min() - pad, p.y.max() + pad); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('2022 drought seen by Sentinel-2', loc='left', fontsize=15, fontweight='bold')
    ax.text(0, 1.0, 'Change in greenness (NDVI) from May to July 2022, cereal parcels, ~1.5 km hexagons', transform=ax.transAxes, fontsize=10.5, color=BODY, va='top')
    cbar(fig, ax, h, 'NDVI change (more negative = earlier, harder senescence)')
    save(fig, 'stage0_s2_drought_2022_lincs.png', f'Sentinel-2 L2A tile 30UXD (Lincolnshire / Leicestershire), {len(drop):,} cereal parcels with clear May and July looks. Brown: early, hard senescence of winter cereals; green: mostly spring-sown crops still growing in July.')


def map_risk(eng):
    t = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y', 'cereal_land'])
    r = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_risk.parquet'))
    c = t[t.cereal_land].merge(r, on='parcref')
    fz3 = c.flood_zone.eq(3).fillna(False).astype(float)
    deep = c.peat_class.eq('Deep Peaty Soils')
    fig, axs = plt.subplots(1, 2, figsize=(13, 7.6))
    blues = LinearSegmentedColormap.from_list('f', ['#E8EEF1', '#A9C7D8', '#5B7F95', '#2B4A5E', '#14283A'])
    h = hexmap(axs[0], c.x, c.y, c=fz3.values, cmap=blues, vmin=0, vmax=0.6, mincnt=5)
    frame(axs[0], eng, 'Cereal land in Flood Zone 3', 'Share of cereal parcels at the highest river and sea flood risk')
    cbar(fig, axs[0], h, 'share in Flood Zone 3', ticks=[0, .2, .4, .6], fmt=lambda v, _: f'{v:.0%}')
    d = c[deep]; both = d.flood_zone.eq(3).fillna(False)
    frame(axs[1], eng, 'Cereal land on deep peat', 'Cereal parcels on deep peaty soils; dark = also in Flood Zone 3')
    axs[1].scatter(d.x[~both], d.y[~both], s=1.2, color='#C9A36B', linewidths=0, zorder=2, label=f'deep peat only ({int((~both).sum()):,})')
    axs[1].scatter(d.x[both], d.y[both], s=1.2, color='#5E3A0C', linewidths=0, zorder=3, label=f'deep peat and Flood Zone 3 ({int(both.sum()):,})')
    leg = axs[1].legend(loc='lower right', frameon=False, fontsize=10, markerscale=8)
    for tx in leg.get_texts(): tx.set_color(BODY)
    axs[1].annotate('The Fens', xy=(545_000, 290_000), xytext=(600_000, 380_000), fontsize=11, color=INK,
                    arrowprops=dict(arrowstyle='-', color=BODY, lw=0.8))
    save(fig, 'stage0_flood_peat.png',
         f'Environment Agency Flood Map for Planning (Flood Zones 2 and 3, rivers and sea); Natural England Peaty Soils Location (BGS, NSRI). '
         f'{int(fz3.sum()):,} of {len(c):,} cereal-land parcels in Flood Zone 3; {int(deep.sum()):,} on deep peat.')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    eng = england()
    t = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y', 'cereal_land', 'parcel_group', 'entry_year'])
    map_agreements(t, eng); map_entry(t, eng); map_weather(eng); map_s2(t, eng); map_risk(eng)

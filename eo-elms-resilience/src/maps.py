"""Maps of the pilot (results/maps/*.png). Boundaries: ONS ITL1 Jan 2021 BUC (OGL v3).
Projected to British National Grid (EPSG:27700)."""
import os, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm
from matplotlib.patches import Polygon as MPoly
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform as stransform
from sites import SITES
ROOT = os.path.join(os.path.dirname(__file__), '..'); OUT = f'{ROOT}/results/maps'; os.makedirs(OUT, exist_ok=True)
INK, MUTED, SURF, EDGE = '#1C2620', '#5B665F', '#F6F4EE', '#FFFFFF'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK, 'axes.labelcolor': INK})
tr = Transformer.from_crs(4326, 27700, always_xy=True)
itl = json.load(open(f'{ROOT}/data/raw/boundaries/itl1_2021_buc.geojson'))
NAME = {'North East (England)': 'North East', 'North West (England)': 'North West and Merseyside',
        'Yorkshire and The Humber': 'Yorkshire & The Humber', 'East Midlands (England)': 'East Midlands',
        'West Midlands (England)': 'West Midlands', 'East': 'Eastern', 'East (England)': 'Eastern', 'London': 'South East and London',
        'South East (England)': 'South East and London', 'South West (England)': 'South West',
        'Wales': 'Wales', 'Scotland': 'Scotland', 'Northern Ireland': None}
geoms = [(NAME.get(f['properties']['ITL121NM']), stransform(tr.transform, shape(f['geometry']))) for f in itl['features']]
SEQ = LinearSegmentedColormap.from_list('seq', ['#E6EFE8', '#9CC3A9', '#4F8A69', '#1E4D36'])
DIV = LinearSegmentedColormap.from_list('div', ['#6E3C0C', '#B5731E', '#E3C79A', '#E6E4DE', '#A9C9B4', '#4F8A69', '#1E4D36'])
def polys(g):
    return g.geoms if g.geom_type == 'MultiPolygon' else [g]
def draw(ax, values=None, cmap=None, norm=None):
    for reg, g in geoms:
        v = values.get(reg) if values is not None and reg else None
        fc = cmap(norm(v)) if v is not None and np.isfinite(v) else '#E4E1DA'
        for p in polys(g):
            ax.add_patch(MPoly(np.asarray(p.exterior.coords), closed=True, fc=fc, ec=EDGE, lw=1.0))
    ax.set_xlim(-10000, 670000); ax.set_ylim(0, 1000000); ax.set_aspect('equal'); ax.axis('off')
def site_xy():
    rows = []
    for reg, pts in SITES.items():
        for i, (lat, lon) in enumerate(pts):
            x, y = tr.transform(lon, lat); rows.append(dict(region=reg, site=i, x=x, y=y))
    return pd.DataFrame(rows)
def cbar(fig, ax, cmap, norm, label):
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); cb = fig.colorbar(sm, ax=ax, shrink=0.5, pad=0.01)
    cb.set_label(label, color=MUTED); cb.outline.set_visible(False); cb.ax.tick_params(colors=MUTED)
NOTE = 'Grey: no data (N. Ireland not sampled). Boundaries: ONS ITL1 2021. Pilot, 24 Sep 2026.'
xy = site_xy()

# 1 · sites and Countryside Stewardship coverage
cs = pd.read_csv(f'{ROOT}/data/processed/cs_share_by_site.csv').merge(xy, on=['region', 'site'], how='right')
fig, ax = plt.subplots(figsize=(7, 9.5), facecolor=SURF); draw(ax)
nn = cs[cs.cs_share_all.isna()]
ax.scatter(nn.x, nn.y, s=70, marker='s', fc='white', ec=MUTED, lw=1.2, label='Site, no CS data (Scotland, Wales)')
en = cs.dropna(subset=['cs_share_all']); norm = Normalize(0, 0.7)
ax.scatter(en.x, en.y, s=90, marker='s', c=en.cs_share_all, cmap=SEQ, norm=norm, ec=INK, lw=0.6)
cbar(fig, ax, SEQ, norm, 'Share of 6×6 km window in Countryside Stewardship')
ax.legend(loc='upper left', frameon=False, fontsize=9)
ax.set_title('50 pilot sites and agri-environment coverage', loc='left', fontsize=14, color=INK)
fig.text(0.02, 0.02, NOTE + ' CS: Natural England/RPA live agreements (land-management only).', fontsize=7, color=MUTED)
fig.savefig(f'{OUT}/map1_sites_cs_coverage.png', dpi=180, bbox_inches='tight'); plt.close(fig)

# 2 · strength of the yield signal by region
res = json.load(open(f'{ROOT}/results/pilot_results.json'))
rr = {k: v['r'] for k, v in res['H1_by_region'].items()}
fig, ax = plt.subplots(figsize=(7, 9.5), facecolor=SURF); norm = Normalize(0, 0.8); draw(ax, rr, SEQ, norm)
for reg, g in geoms:
    if reg in rr and reg != 'South East and London' or (reg == 'South East and London' and g.area > 5e9):
        c = g.representative_point(); ax.text(c.x, c.y, f'{rr[reg]:.2f}', ha='center', va='center', fontsize=11,
                                              color=INK, weight='bold',
                                              path_effects=[pe.withStroke(linewidth=4, foreground='white')])
ax.scatter(xy.x, xy.y, s=10, c=INK, marker='s', alpha=.45, label='Pilot site')
ax.legend(loc='upper left', frameon=False, fontsize=9)
cbar(fig, ax, SEQ, norm, 'Correlation: NDVI anomaly vs wheat-yield anomaly, 2001–2025')
ax.set_title('Where greenness tracks wheat yield', loc='left', fontsize=14)
fig.text(0.02, 0.02, NOTE + ' Yields: Defra cereal production survey.', fontsize=7, color=MUTED)
fig.savefig(f'{OUT}/map2_yield_signal_by_region.png', dpi=180, bbox_inches='tight'); plt.close(fig)

# 3 · drought fingerprints, cropland (region fill) + site dots, and 4 · recovery
nd = pd.read_csv(f'{ROOT}/data/processed/ndvi_site_year.csv')
nd['z'] = nd.groupby(['region', 'site', 'cover']).july.transform(lambda s: (s - s.mean()) / s.std())
sitez = nd.groupby(['region', 'site', 'year']).z.mean().reset_index().merge(xy, on=['region', 'site'])
sh = pd.read_csv(f'{ROOT}/results/shock_profiles.csv'); crop = sh[sh.cover == 'crop']
norm = TwoSlopeNorm(vmin=-3.2, vcenter=0, vmax=3.2)
fig, axs = plt.subplots(1, 3, figsize=(15, 8.2), facecolor=SURF)
for ax, y in zip(axs, [2018, 2022, 2025]):
    draw(ax, dict(zip(crop[crop.shock_year == y].region, crop[crop.shock_year == y].july_z)), DIV, norm)
    s = sitez[sitez.year == y]
    ax.scatter(s.x, s.y, s=55, c=s.z, cmap=DIV, norm=norm, ec=INK, lw=0.6)
    ax.set_title(f'{y}', fontsize=16, loc='left')
cbar(fig, axs, DIV, norm, 'July NDVI, standard deviations from normal (brown = drier / browner)')
fig.suptitle('Drought fingerprints: regions = cropland mean, dots = each site (crop + grass)', x=0.02, ha='left', fontsize=14)
fig.text(0.02, 0.02, NOTE + ' MODIS MOD13Q1 250 m. Wales cropland: 2 sites only.', fontsize=8, color=MUTED)
fig.savefig(f'{OUT}/map3_drought_fingerprints.png', dpi=180, bbox_inches='tight'); plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(10.5, 8.2), facecolor=SURF)
for ax, y in zip(axs, [2018, 2022]):
    draw(ax, dict(zip(crop[crop.shock_year == y].region, crop[crop.shock_year == y].next_z)), DIV, norm)
    s = sitez[sitez.year == y + 1]
    ax.scatter(s.x, s.y, s=55, c=s.z, cmap=DIV, norm=norm, ec=INK, lw=0.6)
    ax.set_title(f'Season after {y} ({y+1})', fontsize=15, loc='left')
cbar(fig, axs, DIV, norm, 'July NDVI the following season, SD from normal (green = rebound)')
fig.suptitle('Recovery: 2018 rebounded, 2022 did not', x=0.02, ha='left', fontsize=14)
fig.text(0.02, 0.02, NOTE, fontsize=8, color=MUTED)
fig.savefig(f'{OUT}/map4_recovery.png', dpi=180, bbox_inches='tight'); plt.close(fig)
print(sorted(os.listdir(OUT)))

"""Figures and maps for the cumulative-shock analysis (results/cumulative/, results/maps/)."""
import os, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, Normalize
from matplotlib.patches import Polygon as MPoly, Patch
from matplotlib.lines import Line2D
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform as stransform
from sites import SITES
ROOT = os.path.join(os.path.dirname(__file__), '..'); C = f'{ROOT}/results/cumulative'; M = f'{ROOT}/results/maps'
INK, MUTED, SURF, EDGE = '#1C2620', '#5B665F', '#F6F4EE', '#FFFFFF'
DIV = LinearSegmentedColormap.from_list('div', ['#6E3C0C', '#B5731E', '#E3C79A', '#E6E4DE', '#A9C9B4', '#4F8A69', '#1E4D36'])
DEBT = LinearSegmentedColormap.from_list('debt', ['#5A300A', '#9A5F14', '#D2A86A', '#EFE3CC', '#F3F0E8'])
TYPES = [('Bounced back', '#4F8A69'), ('Slow recovery', '#D9B77E'), ('Back-to-back hits', '#B5731E'), ('Persistent stress', '#5A300A')]
TCOL = dict(TYPES); TCOL['Little affected'] = '#8FA6B8'
tr = Transformer.from_crs(4326, 27700, always_xy=True)
NAME = {'North East (England)': 'North East', 'North West (England)': 'North West and Merseyside', 'Yorkshire and The Humber': 'Yorkshire & The Humber',
        'East Midlands (England)': 'East Midlands', 'West Midlands (England)': 'West Midlands', 'East': 'Eastern', 'London': 'South East and London',
        'South East (England)': 'South East and London', 'South West (England)': 'South West', 'Wales': 'Wales', 'Scotland': 'Scotland'}
itl = json.load(open(f'{ROOT}/data/raw/boundaries/itl1_2021_buc.geojson'))
geoms = [(NAME.get(f['properties']['ITL121NM']), stransform(tr.transform, shape(f['geometry']))) for f in itl['features']]
xy = pd.DataFrame([dict(region=r, site=i, x=tr.transform(lon, lat)[0], y=tr.transform(lon, lat)[1])
                   for r, pts in SITES.items() for i, (lat, lon) in enumerate(pts)])
NOTE = 'Stress index: mean of peak-season and July NDVI anomalies vs each site’s 2001–2015 normal. MODIS MOD13Q1; ONS ITL1 2021. N. Ireland not sampled.'
def draw(ax, fill=None):
    for reg, g in geoms:
        fc = fill(reg) if fill and reg else '#E4E1DA'
        for p in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
            ax.add_patch(MPoly(np.asarray(p.exterior.coords), closed=True, fc=fc, ec=EDGE, lw=1.0))
    ax.set_xlim(-10000, 670000); ax.set_ylim(0, 1000000); ax.set_aspect('equal'); ax.axis('off')
def cbar(fig, ax, cmap, norm, label):
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); cb = fig.colorbar(sm, ax=ax, shrink=0.5, pad=0.01)
    cb.set_label(label, color=MUTED); cb.outline.set_visible(False); cb.ax.tick_params(colors=MUTED)

def main():
    site = pd.read_csv(f'{C}/site_stress_index.csv').merge(xy, on=['region', 'site'])
    reg = pd.read_csv(f'{C}/region_stress_index.csv')
    rt = pd.read_csv(f'{C}/region_typology.csv'); stp = pd.read_csv(f'{C}/site_typology.csv').merge(xy, on=['region', 'site'])
    ev = pd.read_csv(f'{C}/region_shock_events.csv')

    # 1 · timeline heat strip
    order = rt.sort_values('debt_2026').region.tolist()
    short = {'North West and Merseyside': 'North West', 'Yorkshire & The Humber': 'Yorkshire', 'South East and London': 'South East'}
    years = list(range(2010, 2027))
    mat = reg.pivot(index='region', columns='year', values='S').loc[order, years]
    fig, ax = plt.subplots(figsize=(13, 5.6), facecolor=SURF); ax.set_facecolor(SURF)
    norm = TwoSlopeNorm(vmin=-4, vcenter=0, vmax=2.5)
    ax.imshow(mat.values, cmap=DIV, norm=norm, aspect='auto')
    for i, r in enumerate(order):
        for j, y in enumerate(years):
            v = mat.iloc[i, j]
            e = ev[(ev.region == r) & (ev.year == y)]
            if len(e):
                ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, ec=INK, lw=1.4))
                if bool(e.compound.iloc[0]): ax.plot(j + .32, i - .3, marker='o', ms=5, color='white', mec=INK, mew=1)
            ax.text(j, i, f'{v:.1f}', ha='center', va='center', fontsize=8, color='white' if v < -2 else INK)
    ax.set_xticks(range(len(years))); ax.set_xticklabels(years, fontsize=9, color=MUTED)
    ax.set_yticks(range(len(order))); ax.set_yticklabels([short.get(r, r) for r in order], fontsize=10, color=INK)
    ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
    cbar(fig, ax, DIV, norm, 'Stress index (SD from normal)')
    ax.legend(handles=[Patch(fc='none', ec=INK, lw=1.4, label='Shock (≤ −1 SD)'),
                       Line2D([], [], marker='o', ls='', color='white', mec=INK, label='Compound hit: shock before recovery')],
              loc='upper left', bbox_to_anchor=(0, -0.08), ncol=2, frameon=False, fontsize=9)
    ax.set_title('Shocks and recovery by region, 2010–2026 (ordered by stress debt in 2026)', loc='left', fontsize=13, color=INK)
    fig.tight_layout(); fig.savefig(f'{C}/fig_timeline_heat.png', dpi=180); fig.savefig(f'{M}/fig_timeline_heat.png', dpi=180); plt.close(fig)

    # 2 · stress debt after each shock
    dn = Normalize(-6, 0)
    fig, axs = plt.subplots(1, 3, figsize=(15, 8.2), facecolor=SURF)
    for ax, y in zip(axs, [2018, 2023, 2026]):
        d = reg[reg.year == y].set_index('region').D
        draw(ax, lambda r: DEBT(dn(d.get(r, np.nan))) if r in d else '#E4E1DA')
        s = site[site.year == y]; ax.scatter(s.x, s.y, s=50, c=s.D, cmap=DEBT, norm=dn, ec=INK, lw=0.6)
        ax.set_title({2018: '2018 · first drought', 2023: '2023 · after the 2022 drought', 2026: '2026 · after 2025 and 2026'}[y], fontsize=14, loc='left')
    cbar(fig, axs, DEBT, dn, 'Stress debt: deficits carried over, half-life one year (darker = deeper)')
    fig.suptitle('Stress builds up when droughts arrive before land has recovered', x=0.02, ha='left', fontsize=14)
    fig.text(0.02, 0.02, NOTE, fontsize=8, color=MUTED)
    fig.savefig(f'{M}/map5_stress_debt.png', dpi=180, bbox_inches='tight'); plt.close(fig)

    # 3 · typology
    rtd = rt.set_index('region').typology
    fig, ax = plt.subplots(figsize=(7.4, 9.5), facecolor=SURF)
    from matplotlib.colors import to_rgb
    lite = lambda c: tuple(0.55 * np.array(to_rgb(c)) + 0.45 * np.array(to_rgb(SURF)))
    draw(ax, lambda r: lite(TCOL[rtd[r]]) if r in rtd else '#E4E1DA')
    for k, (name, col) in enumerate(TYPES):
        s = stp[stp.typology == name]; ax.scatter(s.x, s.y, s=75, c=col, ec=INK, lw=1.1, zorder=3)
    ax.legend(handles=[Patch(fc=c, ec=INK, label=f'{n} ({(stp.typology == n).sum()} sites)') for n, c in TYPES],
              loc='upper left', frameon=False, fontsize=10, title='Dots: sites · pale fill: region', title_fontsize=9)
    ax.set_title('Resilience types, 2016–2026', loc='left', fontsize=14)
    fig.text(0.02, 0.02, 'Bounced back: every shock recovered the next year. Slow recovery: 2-year episode. Back-to-back: shocks in consecutive years.\nPersistent stress: 3+ years without returning to normal. ' + NOTE, fontsize=6.5, color=MUTED)
    fig.savefig(f'{M}/map6_resilience_types.png', dpi=180, bbox_inches='tight'); plt.close(fig)

    # 4 · recovery: the season after each drought
    norm = TwoSlopeNorm(vmin=-4, vcenter=0, vmax=3)
    fig, axs = plt.subplots(1, 3, figsize=(15, 8.2), facecolor=SURF)
    for ax, y in zip(axs, [2019, 2023, 2026]):
        d = reg[reg.year == y].set_index('region').S
        draw(ax, lambda r: DIV(norm(d[r])) if r in d else '#E4E1DA')
        s = site[site.year == y]; ax.scatter(s.x, s.y, s=50, c=s.S, cmap=DIV, norm=norm, ec=INK, lw=0.6)
        ax.set_title(f'Season after {y - 1} ({y})', fontsize=14, loc='left')
    cbar(fig, axs, DIV, norm, 'Stress index the following season (green = rebound, brown = still stressed)')
    fig.suptitle('Recovery: 2018 bounced back, 2022 only partly, 2025 not at all', x=0.02, ha='left', fontsize=14)
    fig.text(0.02, 0.02, NOTE, fontsize=8, color=MUTED)
    fig.savefig(f'{M}/map4_recovery.png', dpi=180, bbox_inches='tight'); plt.close(fig)
    print(sorted(os.listdir(M)))

if __name__ == '__main__':
    main()

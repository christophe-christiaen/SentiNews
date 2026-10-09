"""Crop vs grass versions of the shock and cumulative-stress maps (results/maps/*_by_cover.png).
Unit: site x land-cover stress series (as in cumulative_cover.py). A region is filled only when
at least two of its sites have that land cover; otherwise it is grey (n/a)."""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, Normalize, to_rgb
from matplotlib.patches import Patch
from cumulative import BASE, debt, profile
from cumulative_maps import draw, cbar, geoms, xy, DIV, DEBT, TYPES, TCOL, INK, MUTED, SURF
ROOT = os.path.join(os.path.dirname(__file__), '..'); M = f'{ROOT}/results/maps'; C = f'{ROOT}/results/cumulative'
NA = '#E4E1DA'
nd = pd.read_csv(f'{ROOT}/data/processed/ndvi_site_year.csv')
for col in ('peak', 'july'):
    nd[col + '_z'] = nd.groupby(['region', 'site', 'cover'], group_keys=False).apply(
        lambda g: (g[col] - g[g.year <= BASE][col].mean()) / g[g.year <= BASE][col].std())
nd['S'] = nd[['peak_z', 'july_z']].mean(axis=1)
sc = nd[['region', 'site', 'cover', 'year', 'S', 'july_z']].sort_values(['region', 'site', 'cover', 'year']).copy()
sc['D'] = sc.groupby(['region', 'site', 'cover']).S.transform(lambda s: debt(s.values))
sc = sc.merge(xy, on=['region', 'site'])
nsites = sc.groupby(['region', 'cover']).site.nunique()
ok = lambda r, c: nsites.get((r, c), 0) >= 2
reg = sc.groupby(['region', 'cover', 'year'])[['S', 'D', 'july_z']].mean().reset_index()
# typology per site-cover and region-cover
st = pd.DataFrame([dict(region=r, site=i, cover=c, typology=profile(g)[2]) for (r, i, c), g in sc.groupby(['region', 'site', 'cover'])]).merge(xy, on=['region', 'site'])
rt = {(r, c): profile(g)[2] for (r, c), g in reg.groupby(['region', 'cover']) if ok(r, c)}
st.to_csv(f'{C}/site_typology_by_cover.csv', index=False)
pd.Series(rt).rename_axis(['region', 'cover']).rename('typology').reset_index().to_csv(f'{C}/region_typology_by_cover.csv', index=False)
NOTE = ('Crop: MODIS IGBP classes 12/14; grass: class 10. Regions filled only where ≥ 2 sites have that land cover (grey = n/a). '
        'Stress index: mean of peak-season and July NDVI anomalies vs 2001–2015. MODIS MOD13Q1; ONS ITL1 2021.')

def grid(var, years, titles, cmap, norm, label, suptitle, fname, value='region'):
    fig, axs = plt.subplots(2, len(years), figsize=(5 * len(years), 13), facecolor=SURF)
    for row, cov in enumerate(('crop', 'grass')):
        for col, y in enumerate(years):
            ax = axs[row, col]
            d = reg[(reg.cover == cov) & (reg.year == y)].set_index('region')[var]
            draw(ax, lambda r: cmap(norm(d[r])) if r in d.index and ok(r, cov) else NA)
            s = sc[(sc.cover == cov) & (sc.year == y)]
            ax.scatter(s.x, s.y, s=42, c=s[var], cmap=cmap, norm=norm, ec=INK, lw=0.6, zorder=3)
            ax.set_title(f'{"Cropland" if cov == "crop" else "Grassland"} · {titles[col]}', fontsize=13, loc='left')
    cbar(fig, axs, cmap, norm, label)
    fig.suptitle(suptitle, x=0.02, ha='left', fontsize=15)
    fig.text(0.02, 0.01, NOTE, fontsize=8, color=MUTED)
    fig.savefig(f'{M}/{fname}', dpi=150, bbox_inches='tight'); plt.close(fig)

grid('july_z', [2018, 2022, 2025], ['2018', '2022', '2025'], DIV, TwoSlopeNorm(vmin=-3.5, vcenter=0, vmax=3.5),
     'July NDVI, SD from normal (brown = drier)', 'Drought footprints: cropland and grassland', 'map3_drought_by_cover.png')
grid('S', [2019, 2023, 2026], ['after 2018 (2019)', 'after 2022 (2023)', 'after 2025 (2026)'], DIV, TwoSlopeNorm(vmin=-4, vcenter=0, vmax=3),
     'Stress index the following season (green = rebound)', 'Recovery after each drought: cropland and grassland', 'map4_recovery_by_cover.png')
grid('D', [2018, 2023, 2026], ['2018', '2023', '2026'], DEBT, Normalize(-6, 0),
     'Stress debt (darker = deeper)', 'Accumulated stress debt: cropland and grassland', 'map5_stress_debt_by_cover.png')

# typology, crop and grass side by side
lite = lambda c: tuple(0.55 * np.array(to_rgb(c)) + 0.45 * np.array(to_rgb(SURF)))
fig, axs = plt.subplots(1, 2, figsize=(13, 9.5), facecolor=SURF)
for ax, cov in zip(axs, ('crop', 'grass')):
    draw(ax, lambda r: lite(TCOL[rt[(r, cov)]]) if (r, cov) in rt else NA)
    s = st[st.cover == cov]
    ax.scatter(s.x, s.y, s=62, c=[TCOL[t] for t in s.typology], ec=INK, lw=1.0, zorder=3)
    n = s.typology.value_counts()
    ax.set_title(f'{"Cropland" if cov == "crop" else "Grassland"} ({len(s)} site series)', fontsize=14, loc='left')
    ax.legend(handles=[Patch(fc=c, ec=INK, label=f'{k} ({n.get(k, 0)})') for k, c in TYPES + [('Little affected', TCOL['Little affected'])] if n.get(k, 0)],
              loc='upper left', frameon=False, fontsize=9)
fig.suptitle('Resilience types 2016–2026: cropland and grassland', x=0.02, ha='left', fontsize=15)
fig.text(0.02, 0.01, 'Dots: site series; pale fill: region. ' + NOTE, fontsize=7, color=MUTED)
fig.savefig(f'{M}/map6_resilience_types_by_cover.png', dpi=160, bbox_inches='tight'); plt.close(fig)
print(st.groupby('cover').typology.value_counts().to_dict()); print(rt)

# timeline heat strip, cropland above grassland
years = list(range(2010, 2027))
short = {'North West and Merseyside': 'North West', 'Yorkshire & The Humber': 'Yorkshire', 'South East and London': 'South East'}
d26 = reg[(reg.year == 2026)].set_index(['region', 'cover']).D
rows = {cov: sorted([r for r in reg.region.unique() if ok(r, cov)], key=lambda r: d26[(r, cov)]) for cov in ('crop', 'grass')}
events = {(r, c): profile(g)[0] for (r, c), g in reg.groupby(['region', 'cover']) if ok(r, c)}
norm = TwoSlopeNorm(vmin=-4, vcenter=0, vmax=2.5)
fig, axs = plt.subplots(2, 1, figsize=(13, 9.6), facecolor=SURF, gridspec_kw=dict(height_ratios=[len(rows['crop']), len(rows['grass'])], hspace=0.28))
for ax, cov in zip(axs, ('crop', 'grass')):
    ax.set_facecolor(SURF); order = rows[cov]
    mat = reg[reg.cover == cov].pivot(index='region', columns='year', values='S').loc[order, years]
    ax.imshow(mat.values, cmap=DIV, norm=norm, aspect='auto')
    for i, r in enumerate(order):
        ev = {e['year']: e for e in events[(r, cov)]}
        for j, y in enumerate(years):
            v = mat.iloc[i, j]
            if y in ev:
                ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, ec=INK, lw=1.4))
                if ev[y]['compound']: ax.plot(j + .32, i - .3, marker='o', ms=5, color='white', mec=INK, mew=1)
            ax.text(j, i, f'{v:.1f}', ha='center', va='center', fontsize=8, color='white' if v < -2 else INK)
    ax.set_xticks(range(len(years))); ax.set_xticklabels(years, fontsize=9, color=MUTED)
    ax.set_yticks(range(len(order))); ax.set_yticklabels([short.get(r, r) for r in order], fontsize=10, color=INK)
    ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
    ax.set_title(f'{"Cropland" if cov == "crop" else "Grassland"} ({len(order)} regions, ordered by stress debt in 2026)', loc='left', fontsize=12, color=INK)
cbar(fig, axs, DIV, norm, 'Stress index (SD from normal)')
axs[1].legend(handles=[Patch(fc='none', ec=INK, lw=1.4, label='Shock (≤ −1 SD)'),
                       plt.Line2D([], [], marker='o', ls='', color='white', mec=INK, label='Compound hit: shock before recovery')],
              loc='upper left', bbox_to_anchor=(0, -0.14), ncol=2, frameon=False, fontsize=9)
fig.suptitle('Shocks and recovery by region, 2010–2026: cropland and grassland', x=0.02, ha='left', fontsize=14)
fig.savefig(f'{M}/fig_timeline_heat_by_cover.png', dpi=170, bbox_inches='tight'); plt.close(fig)
ev_rows = [dict(region=r, cover=c, **e) for (r, c), evs in events.items() for e in evs]
pd.DataFrame(ev_rows).to_csv(f'{C}/region_shock_events_by_cover.csv', index=False)
print({c: rows[c] for c in rows})

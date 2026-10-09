"""Figures for the pilot (results/figures/*.png)."""
import os, json, pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT = os.path.join(os.path.dirname(__file__), '..'); F = f'{ROOT}/results/figures'
eng = pd.read_csv(f'{ROOT}/results/england_yield_vs_ndvi.csv')
fig, ax = plt.subplots(figsize=(9, 4)); ax2 = ax.twinx()
ax.plot(eng.year, eng.wheat_t_ha_a, 'o-', c='#8a5a14', label='Wheat yield anomaly (t/ha, Defra)')
ax2.plot(eng.year, eng.early_a, 's--', c='#2f6b4f', label='NDVI anomaly by 1 July (MODIS)')
ax.set_ylabel('t/ha'); ax2.set_ylabel('NDVI'); ax.axhline(0, c='grey', lw=.5)
fig.legend(loc='lower left', frameon=False); ax.set_title('England: early-season NDVI tracks wheat yield')
fig.tight_layout(); fig.savefig(f'{F}/fig1_england_timeseries.png', dpi=160)
d = pd.read_csv(f'{ROOT}/data/processed/panel_yield.csv')
fig, ax = plt.subplots(figsize=(6, 5))
for r, g in d.groupby('region'): ax.scatter(g.peak_a, g.wheat_t_ha_a, s=14, label=r)
ax.set_xlabel('Peak cropland NDVI anomaly'); ax.set_ylabel('Wheat yield anomaly (t/ha)')
ax.legend(fontsize=6, frameon=False); fig.tight_layout(); fig.savefig(f'{F}/fig2_region_year_scatter.png', dpi=160)
s = pd.read_csv(f'{ROOT}/results/shock_profiles.csv')
p = s[s.cover == 'crop'].pivot(index='region', columns='shock_year', values='july_z')
fig, ax = plt.subplots(figsize=(7, 4.5)); p.plot.barh(ax=ax); ax.axvline(0, c='k', lw=.5)
ax.set_xlabel('July cropland NDVI z-score'); ax.set_title('Drought-shock resistance by region')
fig.tight_layout(); fig.savefig(f'{F}/fig3_shock_resistance.png', dpi=160)
print('ok')

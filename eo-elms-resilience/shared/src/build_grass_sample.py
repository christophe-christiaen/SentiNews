"""U1 sample (wp2_resilience/results/u1_grassland_protocol.md): 100,000 random parcels of England's permanent
grassland. Grassland land = CROME PG01 in >= 80% of observed years, >= 8 of the 10 years observed, never cereal.

Output  shared/data/parcels/grass_sample.parquet (parcref, x, y); counts printed (aggregates only)
"""
import os
import numpy as np, pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = os.path.join(ROOT, 'shared', 'data', 'parcels')
YEARS = range(2016, 2026)
N, SEED = 100_000, 20261018


def main():
    p = pd.read_parquet(os.path.join(P, 'parcel_panel.parquet'),
                        columns=['parcref', 'x', 'y', 'years_observed', 'cereal_years'] + [f'crop_{y}' for y in YEARS])
    pg = (p[[f'crop_{y}' for y in YEARS]] == 'PG01').sum(axis=1)
    ok = (p.years_observed >= 8) & (pg >= 0.8 * p.years_observed) & (p.cereal_years == 0) & p.x.notna()
    pool = p[ok]
    s = pool.sample(N, random_state=np.random.RandomState(SEED))[['parcref', 'x', 'y']]
    s.to_parquet(os.path.join(P, 'grass_sample.parquet'), index=False)
    print(f'grassland land: {len(pool):,} parcels; sample {len(s):,}')
    sq = (s.x // 50_000).astype(int).astype(str) + '_' + (s.y // 50_000).astype(int).astype(str)
    print(f'50 km squares: {sq.nunique()}')


if __name__ == '__main__':
    main()

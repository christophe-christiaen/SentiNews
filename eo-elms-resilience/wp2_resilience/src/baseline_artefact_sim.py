"""Simulation for Paper 2: how much false 'legacy' does a short baseline create when there is none?

Fields with no season-to-season dynamics: y_it = a_i + c_{cell,t} + e_it (e iid). Each field's anomaly is the
z-score against its own first n seasons, as in WP2 (n = 4: 2017-2020). The legacy test regresses S_t on S_t-1 within
cell x season. (For pairs after the baseline the shared error of the baseline mean alone would give about
1/(n + 1); pairs inside the baseline pull the other way, so the pooled figure is lower: see the output.) Also run:
n = 4 with real dynamics rho = 0.2, and the split-normal version, which turns out to be biased towards zero.

Output  wp2_resilience/results/baseline_artefact_sim.json; figure results/maps/wp2_baseline_artefact.png
"""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
RNG = np.random.default_rng(7)


def simulate(n_base, rho=0.0, fields=40000, seasons=10, cells=400, split=False):
    a = RNG.normal(0, 1.0, fields)[:, None]
    cell = RNG.integers(0, cells, fields)
    c = RNG.normal(0, 0.8, (cells, seasons))[cell]
    e = np.zeros((fields, seasons)); prev = RNG.normal(0, 1, fields)
    for t in range(seasons):
        prev = rho * prev + np.sqrt(1 - rho ** 2) * RNG.normal(0, 1, fields); e[:, t] = prev
    y = a + c + e
    if not split:
        mu, sd = y[:, :n_base].mean(1, keepdims=True), y[:, :n_base].std(1, ddof=1, keepdims=True)
        S = (y - mu) / sd
        X, Y = S[:, :-1], S[:, 1:]
    else:                                         # disjoint halves of the other seasons for S_t and S_t-1
        X = np.empty((fields, seasons - 1)); Y = np.empty_like(X)
        for t in range(1, seasons):
            others = np.array([k for k in range(seasons) if k not in (t, t - 1)])
            perm = np.argsort(RNG.random((fields, len(others))), 1)
            A, B = others[perm[:, :len(others) // 2]], others[perm[:, len(others) // 2:]]
            z = lambda k, sel: (y[:, k] - np.take_along_axis(y, sel, 1).mean(1)) / np.take_along_axis(y, sel, 1).std(1, ddof=1)
            Y[:, t - 1], X[:, t - 1] = z(t, A), z(t - 1, B)
    df = pd.DataFrame({'Y': Y.ravel(), 'X': X.ravel(), 'cy': (cell[:, None] * 100 + np.arange(1, seasons)[None, :]).ravel()})
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    w = df[['Y', 'X']] - df.groupby('cy')[['Y', 'X']].transform('mean')
    return float((w.X * w.Y).sum() / (w.X ** 2).sum())


def main():
    out = {'no dynamics, baseline n': {}, 'analytic 1/(n+1)': {}}
    for n in (2, 3, 4, 6, 8, 10, 15):
        seasons = max(10, n + 6)
        out['no dynamics, baseline n'][n] = simulate(n, seasons=seasons)
        out['analytic 1/(n+1)'][n] = 1 / (n + 1)
        print(n, round(out['no dynamics, baseline n'][n], 3), round(1 / (n + 1), 3), flush=True)
    out['n=4, true rho=0.2'] = simulate(4, rho=0.2)
    out['split normal, no dynamics'] = simulate(4, split=True)
    out['split normal, true rho=0.2'] = simulate(4, rho=0.2, split=True)
    print({k: v for k, v in out.items() if not isinstance(v, dict)})
    json.dump(out, open(os.path.join(ROOT, 'wp2_resilience', 'results', 'baseline_artefact_sim.json'), 'w'), indent=1)

    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    DARK, BODY, GREEN, OCHRE, RULE, BG = '#1C2620', '#4A554E', '#2F6B4F', '#9A5F14', '#D6D0C2', '#F6F4EE'
    wf = json.load(open(os.path.join(ROOT, 'wp2_resilience', 'results', 'within_field_check.json')))
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.2))
    fig.patch.set_facecolor(BG)
    for x in ax:
        x.set_facecolor(BG); x.spines[['top', 'right']].set_visible(False); x.spines[['left', 'bottom']].set_color(RULE)
        x.tick_params(colors=BODY, labelsize=11)
    ns = sorted(out['no dynamics, baseline n'])
    nn = np.linspace(2, 15, 100)
    ax[0].plot(ns, [out['no dynamics, baseline n'][n] for n in ns], 'o', color=OCHRE, ms=9, label='simulated, no real carry-over')
    ax[0].plot(4, wf['T1 | original']['coef'], 's', color=GREEN, ms=11, label='WP2 Sentinel-2, as reported (n = 4)')
    ax[0].plot(15, 0.12, 'D', color=DARK, ms=9, label='MODIS pilot, as reported (n = 15)')
    ax[0].set_xlabel('seasons in the baseline (n)', color=BODY, fontsize=12); ax[0].set_ylabel('apparent "legacy" coefficient', color=BODY, fontsize=12)
    ax[0].set_title('A short baseline creates carry-over that is not there', loc='left', fontsize=13, fontweight='bold', color=DARK)
    ax[0].axhline(0, color=BODY, lw=0.8); ax[0].legend(frameon=False, fontsize=10)
    labs = ['as reported', 'within each field\n(Anderson–Hsiao)', 'field fixed effects', 'seasons shuffled']
    keys = ['original', 'Anderson-Hsiao, z = S(t-2)', 'field FE (lower bound)', 'shuffled seasons (placebo)']
    for k, (t, col, off) in enumerate([('T1', GREEN, -0.18), ('T2', OCHRE, 0.18)]):
        v = [wf[f'{t} | {kk}']['coef'] for kk in keys]
        ax[1].bar(np.arange(4) + off, v, width=0.34, color=col, label={'T1': 'stress carries over (T1)', 'T2': 'unrecovered land hit harder (T2)'}[t])
    ax[1].axhline(0, color=BODY, lw=0.8)
    ax[1].set_xticks(range(4), labs, fontsize=10.5, color=DARK)
    ax[1].set_ylabel('coefficient (SD per SD)', color=BODY, fontsize=12)
    ax[1].set_title('381,400 fields: most of the effect goes within each field', loc='left', fontsize=13, fontweight='bold', color=DARK)
    ax[1].legend(frameon=False, fontsize=10)
    fig.tight_layout(w_pad=3)
    fig.savefig(os.path.join(ROOT, 'results', 'maps', 'wp2_baseline_artefact.png'), dpi=170, facecolor=BG)


if __name__ == '__main__':
    main()

"""Deck figure for WP3: H1-H3 under the three designs (frozen plan, trend-adjusted, within cohort) and the event study
of the shock contrast. Reads the JSON outputs of wp3_did.py, wp3_trend_adjusted.py and wp3_within_cohort.py.

Output  results/maps/wp3_effects.png
"""
import json, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
RES = os.path.join(ROOT, 'wp3_elms_effect', 'results')
OUT = os.path.join(ROOT, 'results', 'maps', 'wp3_effects.png')
DARK, BODY, GREEN, OCHRE, BLUE, RULE = '#1C2620', '#4A554E', '#2F6B4F', '#9A5F14', '#5B7F95', '#D6D0C2'


def main():
    a = json.load(open(os.path.join(RES, 'wp3_estimates.json')))
    b = json.load(open(os.path.join(RES, 'wp3_trend_adjusted.json')))['main']
    c = json.load(open(os.path.join(RES, 'wp3_within_cohort.json')))['main']
    conf = {r['name'][:2]: r for r in a['confirmatory']}
    designs = [('Frozen plan', GREEN, lambda h: conf[h]), ('Trend-adjusted', OCHRE, lambda h: b[h]['adjusted']),
               ('Within cohort', BLUE, lambda h: c[h]['after entry'])]
    labels = {'H1': 'H1  smaller drop\nin shock seasons', 'H2': 'H2  better recovery\nafter a shock',
              'H3': 'H3  land-use change\nbeats management'}
    fig, ax = plt.subplots(1, 2, figsize=(15, 6.2), gridspec_kw={'width_ratios': [1.05, 1]})
    fig.patch.set_facecolor('#F6F4EE')
    for x in ax:
        x.set_facecolor('#F6F4EE'); x.spines[['top', 'right']].set_visible(False)
        x.spines[['left', 'bottom']].set_color(RULE); x.tick_params(colors=BODY, labelsize=12)
    for i, h in enumerate(['H1', 'H2', 'H3']):
        for k, (name, col, get) in enumerate(designs):
            r = get(h); y = -(i * 4 + k)
            ax[0].plot([r['lo'], r['hi']], [y, y], color=col, lw=2.5, solid_capstyle='round')
            ax[0].plot(r['est'], y, 'o', color=col, ms=9)
            ax[0].text(0.36, y, f"{r['est']:+.3f}", va='center', ha='right', fontsize=11.5, color=col)
    ax[0].axvline(0, color=BODY, lw=1)
    ax[0].set_xlim(-0.23, 0.37); ax[0].spines['left'].set_visible(False)
    ax[0].set_yticks([-1, -5, -9], [labels[h] for h in ('H1', 'H2', 'H3')], fontsize=12.5, color=DARK, fontweight='bold')
    ax[0].tick_params(axis='y', length=0)
    ax[0].set_xlabel('effect, SD of the parcel\'s own 2017–2020 normal (95% CI)', color=BODY, fontsize=12)
    ax[0].set_title('Three tests, three designs', loc='left', fontsize=15, fontweight='bold', color=DARK, pad=34)
    for name, col, _ in designs:
        ax[0].plot([], [], 'o-', color=col, label=name)
    ax[0].legend(loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=11.5)
    ax[0].set_ylim(-11, 1.4)
    ev = pd.DataFrame(a['event'])
    pre = ev.e < 0
    for m, col in [(pre, OCHRE), (~pre, GREEN)]:
        ax[1].errorbar(ev.e[m], ev.contrast[m], yerr=1.96 * ev.contrast_se[m], fmt='o', color=col, ecolor=col, capsize=4, ms=9, lw=2)
    ax[1].axhline(0, color=BODY, lw=1); ax[1].axvline(-0.5, color=RULE, lw=1.2, ls='--')
    ax[1].text(-2.5, 0.19, 'before entry: should be zero', ha='center', color=OCHRE, fontsize=12)
    ax[1].text(1.5, 0.19, 'after entry', ha='center', color=GREEN, fontsize=12)
    ax[1].set_ylim(-0.07, 0.21)
    ax[1].set_xlabel('season relative to the first full season under agreement', color=BODY, fontsize=12)
    ax[1].set_title('Extra July NDVI in shock seasons (H1), by season', loc='left', fontsize=15, fontweight='bold', color=DARK, pad=34)
    fig.tight_layout(w_pad=3)
    fig.savefig(OUT, dpi=170, facecolor=fig.get_facecolor())
    print('wrote', OUT)


if __name__ == '__main__':
    main()

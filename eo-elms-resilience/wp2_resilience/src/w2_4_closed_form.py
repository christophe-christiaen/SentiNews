"""W2-4 (wp2_resilience/results/w2_4_closed_form_protocol.md, written before running): closed form for the
short-baseline artefact, checked by Monte Carlo of the WP2 design.

beta(n, T) = [(T-n-1) K - (n-1)] / [n(n-1) + (T-n-1)(n+1) K],  K = E[1/s^2] = (n-1)/(n-3)  (K = 1 if not scaled)

Output  wp2_resilience/results/w2_4_closed_form.md, .json; results/maps/wp2_closed_form.png
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
RNG = np.random.default_rng(20261018)
NS = (2, 3, 4, 5, 6, 8, 10, 15)
REPS, FIELDS, CELLS = 200, 40000, 400


def K(n, scaled=True):
    if not scaled:
        return 1.0
    return (n - 1) / (n - 3) if n > 3 else np.inf


def beta(n, T, scaled=True):
    k, m = K(n, scaled), T - n - 1
    if np.isinf(k):
        return 1 / (n + 1)                      # ratio-of-expectations limit; no stable value (see protocol)
    return (m * k - (n - 1)) / (n * (n - 1) + m * (n + 1) * k)


def one(n, T, shocks=True, scaled=True):
    a = RNG.normal(0, 1, (FIELDS, 1)); cell = RNG.integers(0, CELLS, FIELDS)
    c = RNG.normal(0, 0.8, (CELLS, T))[cell] if shocks else 0.0
    y = a + c + RNG.normal(0, 1, (FIELDS, T))
    mu = y[:, :n].mean(1, keepdims=True)
    S = (y - mu) / (y[:, :n].std(1, ddof=1, keepdims=True) if scaled else 1.0)
    X, Y = S[:, :-1], S[:, 1:]
    g = (cell[:, None] * T + np.arange(T - 1)[None, :]).ravel()          # cell x season groups
    x, yv = X.ravel(), Y.ravel()
    ok = np.isfinite(x) & np.isfinite(yv); g, x, yv = g[ok], x[ok], yv[ok]
    cnt = np.bincount(g, minlength=CELLS * T)
    xm = np.bincount(g, x, CELLS * T) / np.maximum(cnt, 1); ym = np.bincount(g, yv, CELLS * T) / np.maximum(cnt, 1)
    xd, yd = x - xm[g], yv - ym[g]
    return float((xd * yd).sum() / (xd ** 2).sum())


def main():
    versions = {'estimated SD, cell shocks (WP2 design)': dict(shocks=True, scaled=True),
                'estimated SD, no cell shocks': dict(shocks=False, scaled=True),
                'mean removed, not scaled (= known SD), no cell shocks': dict(shocks=False, scaled=False)}
    out = {}
    for vlab, kw in versions.items():
        for tlab in ('T = 10', 'T = max(10, n + 6)'):
            for n in NS:
                T = 10 if tlab == 'T = 10' else max(10, n + 6)
                if T - n - 1 < 1:
                    continue
                r = np.array([one(n, T, **kw) for _ in range(REPS)])
                f = beta(n, T, kw['scaled'])
                out[f'{vlab} | {tlab} | {n}'] = dict(n=n, T=T, formula=f, mean=float(r.mean()), median=float(np.median(r)),
                                                     se=float(r.std(ddof=1) / np.sqrt(REPS)), p10=float(np.quantile(r, 0.1)), p90=float(np.quantile(r, 0.9)))
            print(vlab, tlab, 'done', flush=True)
    # acceptance (protocol)
    acc = {}
    for k, v in out.items():
        vlab = k.split(' | ')[0]; n = v['n']
        if vlab.startswith('mean removed'):
            acc[k] = abs(v['formula'] - v['mean']) <= 2 * v['se']
        elif n >= 6:
            tol = 2 * v['se'] if 'no cell shocks' in vlab else 0.02
            acc[k] = abs(v['formula'] - v['mean']) <= tol
    verdict = dict(checks=len(acc), passed=int(sum(acc.values())), failed=[k for k, v in acc.items() if not v])
    json.dump({'results': out, 'acceptance': {k: bool(v) for k, v in acc.items()}, 'verdict': verdict},
              open(os.path.join(ROOT, 'wp2_resilience', 'results', 'w2_4_closed_form.json'), 'w'), indent=1)
    report(out, acc, verdict); figure(out)


def report(out, acc, verdict):
    L = ['# W2-4: a closed form for the short-baseline artefact', '',
         'Protocol: [w2_4_closed_form_protocol.md](w2_4_closed_form_protocol.md), written before this run. Fields with no '
         'carry-over, z-scored against their first n seasons over T seasons; legacy test pooled within cell × season. '
         f'{REPS} Monte Carlo replications per row ({FIELDS:,} fields, {CELLS} cells).', '',
         'β(n, T) = [(T − n − 1)K − (n − 1)] / [n(n − 1) + (T − n − 1)(n + 1)K], K = (n − 1)/(n − 3) with the SD '
         'estimated, K = 1 without scaling; infinite K for n ≤ 3 (no stable value).', '',
         '| Version | T | n | formula | MC mean (SE) | MC median | 10–90% of runs | accepted |', '|---|---|---|---|---|---|---|---|']
    for k, v in out.items():
        vlab, tlab, _ = k.split(' | ')
        a = acc.get(k); a = '–' if a is None else ('yes' if a else '**no**')
        L.append(f"| {vlab} | {v['T']} | {v['n']} | {v['formula']:+.3f} | {v['mean']:+.3f} ({v['se']:.3f}) | {v['median']:+.3f} | "
                 f"{v['p10']:+.3f} to {v['p90']:+.3f} | {a} |")
    L += ['', f"**Acceptance (rules fixed in advance):** {verdict['passed']} of {verdict['checks']} checks passed."
          + (f" Failed: {', '.join(verdict['failed'])}." if verdict['failed'] else ''), '',
          'Rows marked "–" are reported, not tested: n = 4, 5 have infinite variance (E[1/s⁴] diverges), n ≤ 3 has no '
          'stable value.']
    open(os.path.join(ROOT, 'wp2_resilience', 'results', 'w2_4_closed_form.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


def figure(out):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    DARK, BODY, GREEN, OCHRE, GREY, RULE = '#1C2620', '#4A554E', '#2F6B4F', '#9A5F14', '#9AA39D', '#D6D0C2'
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    nn = np.arange(4, 16)
    ax.plot(nn, [beta(n, 10) for n in nn if 10 - n - 1 >= 1] + [np.nan] * sum(10 - n - 1 < 1 for n in nn), color=OCHRE, lw=2,
            label='closed form, SD estimated (T = 10)')
    ax.plot(nn, [beta(n, 10, False) if 10 - n - 1 >= 1 else np.nan for n in nn], color=GREY, lw=2, ls='--', label='closed form, not scaled (T = 10)')
    ax.plot(nn, 1 / (nn + 1), color=BODY, lw=1, ls=':', label='earlier approximation 1/(n + 1)')
    for k, v in out.items():
        if v['T'] != 10:
            continue
        c = OCHRE if k.startswith('estimated SD, cell') else (GREY if k.startswith('mean removed') else None)
        if c is None:
            continue
        ax.plot([v['n']] * 2, [v['p10'], v['p90']], color=c, lw=1, alpha=0.6)
        ax.plot(v['n'], v['median'], 'o', color=c, ms=4)
    ax.axhline(0, color=BODY, lw=0.7); ax.set_ylim(-0.15, 0.7)
    ax.set_xlabel('seasons in the baseline (n), panel of T = 10 seasons', fontsize=9); ax.set_ylabel('apparent carry-over with none present', fontsize=9)
    ax.spines[['top', 'right']].set_visible(False); ax.legend(frameon=False, fontsize=8)
    ax.set_title('Points: Monte Carlo medians with 10–90% of runs (WP2 design, cell shocks)', loc='left', fontsize=9, color=DARK)
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'results', 'maps', 'wp2_closed_form.png'), dpi=200)


if __name__ == '__main__':
    main()

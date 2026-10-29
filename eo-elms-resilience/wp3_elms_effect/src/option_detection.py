"""Paper 3: detecting agri-environment options from satellite records (results/detection_protocol.md, written before
any model was fitted). Families, comparisons, features, placebo, leave-one-region-out evaluation and the reading rule
are fixed there.

Output  wp3_elms_effect/results/option_detection.md, option_detection.json; results/maps/p3_detection.png
"""
import glob, json, os, re
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
RES = os.path.join(ROOT, 'wp3_elms_effect', 'results')
RNG = np.random.default_rng(20261017)
BANDS = [f'A{i:02d}' for i in range(64)]
S2 = [f'{i}_p{k:02d}' for k in range(1, 13) for i in ('ndvi', 'ndre', 'ndmi')]
CAP = 15000
FAMILIES = {
    'Herbal leys': ['SAM3', 'CSAM3'],
    'Cover crops': ['SAM2', 'CSAM2', 'SOH2', 'SOH3'],
    'No-till': ['SOH1'],
    'In-field flower and bird-food plots': ['AHL1', 'AHL2', 'CAHL1', 'CAHL2'],
    'Margins and corners': ['AHL3', 'AHL4', 'CAHL3', 'CAHL4', 'AB8'],
    'Grassland options': ['LIG1', 'CLIG3', 'IGL2', 'CIGL2', 'GS1', 'GS2'],
    'Buffer strips (control)': ['SW1', 'SW3', 'SW4'] + [f'AHW{k}' for k in range(6, 12)],
    'Management only (control)': ['SAM1', 'IPM2', 'IPM3', 'IPM4', 'CIPM2', 'CIPM3', 'CIPM4', 'NUM2', 'NUM3', 'CNUM2', 'CNUM3',
                                  'PRF1', 'PRF2', 'PRF3', 'PRF4']}
MGMT = set(FAMILIES['Management only (control)'])
REGION = {'London': 'South East'}


def codes(row):
    out = set()
    for col in ('CS_land_codes', 'SFI_land_codes'):
        if isinstance(row[col], str):
            out |= {re.sub(r'_\d+$', '', c.strip()) for c in row[col].split(';') if c.strip()}
    return out


def load():
    pan = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'),
                          columns=['parcref', 'cereal_land', 'parcel_group', 'entry_year', 'css_legacy', 'CS_land_codes', 'SFI_land_codes'])
    pan = pan[pan.cereal_land & ~pan.css_legacy]
    reg = pd.read_parquet(os.path.join(ROOT, 'wp2_resilience', 'results', 'parcel_resilience.parquet'), columns=['parcref', 'region'])
    reg['region'] = reg.region.replace(REGION)
    pan = pan.merge(reg, on='parcref').dropna(subset=['region'])
    pan['codes'] = pan.apply(codes, axis=1)
    agr = pan[(pan.parcel_group == 'agreement') & pan.entry_year.between(2021, 2024)].copy()
    never = pan[pan.parcel_group == 'no agreement'].copy()
    mgmt_only = agr[agr.codes.map(lambda c: len(c) > 0 and c <= MGMT)].copy()
    return agr, never, mgmt_only


def emb_year(years, keep):
    acc, n = None, None
    for y in years:
        d = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(os.path.join(D, 'embeddings', 'parcels', f'aef_*_{y}.parquet')))],
                      ignore_index=True).drop_duplicates('parcref').set_index('parcref')[BANDS]
        d = d[d.index.isin(keep)]
        acc = d if acc is None else acc.add(d, fill_value=0)
    return acc / len(years)


def s2_2025(keep):
    s = pd.read_parquet(os.path.join(D, 's2', 's2_parcel_year.parquet'), columns=['parcref', 'year'] + S2)
    return s[(s.year == 2025) & s.parcref.isin(keep)].drop_duplicates('parcref').set_index('parcref')[S2]


def sample(pos, comp):
    pos = pos.sample(min(len(pos), CAP), random_state=1)
    parts = []
    for r, g in pos.groupby('region'):
        c = comp[comp.region == r]
        if len(c):
            parts.append(c.sample(min(len(g), len(c)), random_state=2))
    neg = pd.concat(parts)
    return pd.concat([pos.assign(y=1), neg.assign(y=0)])[['parcref', 'region', 'y']]


def evaluate(df, X):
    pred = pd.Series(np.nan, index=df.index); by_region = {}
    for r in sorted(df.region.unique()):
        te = df.region == r
        if df.y[te].nunique() < 2 or df.y[~te].nunique() < 2:
            continue
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0).fit(X[~te.values], df.y[~te])
        pred[te] = m.predict_proba(X[te.values])[:, 1]
        by_region[r] = float(roc_auc_score(df.y[te], pred[te]))
    ok = pred.notna()
    return dict(auc=float(roc_auc_score(df.y[ok], pred[ok])), auc_min=min(by_region.values()), auc_max=max(by_region.values()), n=int(ok.sum()))


def main():
    agr, never, mgmt = load()
    keep = set(agr.parcref) | set(never.parcref)
    print('loading embeddings and Sentinel-2', flush=True)
    e25, epre, s2 = emb_year([2025], keep), emb_year([2017, 2018, 2019], keep), s2_2025(keep)
    out = {'counts': {}, 'results': {}}
    for fam, cs in FAMILIES.items():
        cs = set(cs)
        pos = agr[agr.codes.map(lambda c: len(c & cs) > 0)]
        out['counts'][fam] = int(len(pos))
        comps = {'A: vs never-treated land': never}
        if fam != 'Management only (control)':
            comps['B: vs management-only scheme land'] = mgmt[~mgmt.parcref.isin(pos.parcref)]
        for clab, comp in comps.items():
            df = sample(pos, comp).reset_index(drop=True)
            feats = {'Embedding 2025': e25.reindex(df.parcref).values,
                     'Sentinel-2 2025': s2.reindex(df.parcref).values,
                     'Both': np.hstack([e25.reindex(df.parcref).values, s2.reindex(df.parcref).values]),
                     'Placebo: embedding 2017–2019': epre.reindex(df.parcref).values}
            res = {k: evaluate(df, X) for k, X in feats.items()}
            res['detection gain'] = res['Embedding 2025']['auc'] - res['Placebo: embedding 2017–2019']['auc']
            out['results'][f'{fam} | {clab}'] = res
            print(fam, '|', clab, {k: round(v['auc'], 3) if isinstance(v, dict) else round(v, 3) for k, v in res.items()}, flush=True)
    for fam in FAMILIES:
        b = out['results'].get(f'{fam} | B: vs management-only scheme land')
        out['results'].setdefault('_verdict', {})[fam] = (bool(b['Embedding 2025']['auc'] >= 0.70 and b['detection gain'] >= 0.10) if b else None)
    json.dump(out, open(os.path.join(RES, 'option_detection.json'), 'w'), indent=1, default=float)
    report(out); figure(out)


def report(o):
    L = ['# Paper 3: detecting agri-environment options from satellite records', '',
         'Run of [detection_protocol.md](detection_protocol.md) (written before any model). Leave-one-region-out AUC '
         '(0.5 = chance); placebo = the 2017–2019 embedding, before any option existed; detection gain = 2025 embedding '
         'minus placebo. "Detected" = AUC ≥ 0.70 against comparison B and gain ≥ 0.10.', '',
         '| Family | parcels | comparison | embedding 2025 | Sentinel-2 2025 | both | placebo 2017–19 | detection gain |',
         '|---|---|---|---|---|---|---|---|']
    for k, r in o['results'].items():
        if k.startswith('_'):
            continue
        fam, comp = k.split(' | ')
        L.append(f"| {fam} | {o['counts'][fam]:,} | {comp} | {r['Embedding 2025']['auc']:.2f} ({r['Embedding 2025']['auc_min']:.2f}–{r['Embedding 2025']['auc_max']:.2f}) | "
                 f"{r['Sentinel-2 2025']['auc']:.2f} | {r['Both']['auc']:.2f} | {r['Placebo: embedding 2017–2019']['auc']:.2f} | {r['detection gain']:+.2f} |")
    L += ['', '## Verdict (rule fixed in advance)', '', '| Family | detected |', '|---|---|'] + \
         [f"| {f} | {'yes' if v else ('no' if v is not None else '–')} |" for f, v in o['results']['_verdict'].items()]
    open(os.path.join(RES, 'option_detection.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


def figure(o):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    DARK, BODY, GREEN, OCHRE, PURPLE = '#1C2620', '#4A554E', '#2F6B4F', '#9A5F14', '#6B4E8C'
    fams = list(FAMILIES)
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2), sharey=True)
    for ax, comp, title in [(axes[0], 'A: vs never-treated land', 'A. Option land vs land never in a scheme'),
                            (axes[1], 'B: vs management-only scheme land', 'B. Option land vs scheme land with management only')]:
        yy = np.arange(len(fams))[::-1]
        for k, (lab, col, mk, name) in enumerate([('Embedding 2025', PURPLE, 'o', 'AlphaEarth embedding 2025 (AI)'),
                                                  ('Sentinel-2 2025', GREEN, 's', 'Sentinel-2 indices 2025 (no AI, baseline)'),
                                                  ('Placebo: embedding 2017–2019', '#8C8C8C', 'D', 'Placebo: embedding 2017–2019')]):
            xs = [o['results'][f'{f} | {comp}'][lab]['auc'] if f'{f} | {comp}' in o['results'] else np.nan for f in fams]
            ax.scatter(xs, yy + (1 - k) * 0.22, color=col, marker=mk, s=55, label=name, zorder=3)
        ax.axvline(0.5, color=BODY, lw=0.8); ax.axvline(0.7, color=OCHRE, lw=1, ls='--')
        ax.set_yticks(yy, fams, fontsize=11, color=DARK); ax.set_xlim(0.45, 0.95)
        ax.set_title(title, loc='left', fontsize=12.5, fontweight='bold', color=DARK)
        ax.set_xlabel('AUC on held-out regions (0.5 = chance)', color=BODY, fontsize=11)
        ax.spines[['top', 'right']].set_visible(False)
    axes[1].text(0.47, 0, 'management only: the comparison group in this panel', fontsize=10, color=BODY, va='center', style='italic', bbox=dict(facecolor='white', edgecolor='none', pad=2))
    axes[1].legend(frameon=False, fontsize=10, loc='lower right', bbox_to_anchor=(1.0, 0.1))
    fig.tight_layout(w_pad=2); fig.savefig(os.path.join(ROOT, 'results', 'maps', 'p3_detection.png'), dpi=200)
    for a in axes:                                          # deck version on the deck background
        a.set_facecolor('#F6F4EE')
    fig.savefig(os.path.join(ROOT, 'results', 'maps', 'p3_detection_deck.png'), dpi=200, facecolor='#F6F4EE')


if __name__ == '__main__':
    main()

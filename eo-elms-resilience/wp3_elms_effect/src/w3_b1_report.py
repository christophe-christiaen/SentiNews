"""W3-B1: write the report from w3_b1_inference.json, w3_b1_multiple.json and w3_b1_honest.json (protocol: w3_b1_inference_protocol.md)."""
import json, os
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
J = lambda f: json.load(open(os.path.join(RES, f)))
g = lambda x: g(x[0]) if isinstance(x, list) else x
d, m, h = J('w3_b1_inference.json'), J('w3_b1_multiple.json')['rows'], J('w3_b1_honest.json')
c = lambda x: f"{x['est']:+.3f} ({x['lo']:+.3f}, {x['hi']:+.3f})"
iv = lambda x: f"{x['se']:.3f} ({x['lo']:+.3f}, {x['hi']:+.3f})" if x.get('se') else 'not defined'
info = d['merged_clusters']
L = ['# W3-B1: few shocks, trends, multiple tests and crop conditioning', '', 'Protocol: [w3_b1_inference_protocol.md](w3_b1_inference_protocol.md). Labels beside registered results; no registered reading changes. Exploratory.', '',
     '## 1. Inference when shocks are few', '', 'SE (95% interval). Season and two-way use scores from each row\'s deviation from its side\'s mean, because the estimator\'s influence functions sum to about zero within a season (see the protocol record). **Season clustering understates uncertainty when one season dominates, as it does here, so the permutation test carries more weight.**', '',
     '| Result | Estimate | Cell | 50 km | Region (no conditioning) | Season | Permutation p | Label | Share of hazard side by season |', '|---|---:|---|---:|---|---|---:|---|---|']
for r in d['targets']:
    i = r['inference']; sh = ', '.join(f'{k}: {v:.0%}' for k, v in r['hazard_season_shares'].items())
    L.append(f"| {r['name']} | {r['est']:+.3f} | {iv(i['cell'])} | {i['block50']['se']:.3f} | {iv(i['region_no_conditioning'])} | {iv(i['season'])}, G = {i['season']['G']} | {r['permutation']['p']:.3f} | {'robust to few shocks' if r['robust_to_few_shocks'] else 'not robust'} | {sh} |")
L += ['', '### Leave one season out', '', '| Result | ' + ' | '.join(str(y) for y in range(2021, 2027)) + ' |', '|---|' + '---:|' * 6]
for r in d['targets']:
    L.append(f"| {r['name']} | " + ' | '.join(f"{r['leave_one_out'][str(y)]['est']:+.3f}" if str(y) in r['leave_one_out'] else '' for y in range(2021, 2027)) + ' |')
L += ['', f"**Cells merged by agreement: not informative.** {info['agreements']:,} agreements, {info['agreements_in_more_than_one_cell']:,} in more than one cell, so {info['largest_share_of_cells']:.0%} of cells fall into one cluster, and with so few effective clusters the SE collapses. Farm-level clustering remains unaddressed, apart from 50 km blocks, which are coarser than most farms.", '',
      '## 2. How large a trend violation overturns the result', '', 'Rambachan and Roth (2023), relative magnitudes, cell-clustered covariance. Breakdown M̄ is the smallest grid value (step 0.25) whose 95% set includes zero. The package warned in 36 of its fits that a set is open at an endpoint, so set lengths may not be exact.', '',
      '| Result | Parameter | Estimate | M̄ = 0 | M̄ = 0.25 | M̄ = 0.5 | Breakdown M̄ |', '|---|---|---:|---|---|---|---:|']
st = lambda q: f"({g(q['lb']):+.3f}, {g(q['ub']):+.3f})"
for r in h:
    s = r['sets']; L.append(f"| {r['target']} | {'average of 0–3' if r['parameter'] == 'average' else 'first season'} | {g(r['estimate']):+.3f} | {st(s[0])} | {st(s[1])} | {st(s[2])} | {g(r['breakdown_Mbar'])} |")
L += ['', '## 3. Multiple testing', '', f"Romano–Wolf over {len(m)} contrasts, cell-level uncertainty. {sum(r['p_raw'] < .05 for r in m)} have raw p below 0.05; **{sum(r['survives'] for r in m)} survive.** Cushions and costs both count. Placebo failures stand.", '',
      '| Outcome | Contrast | Family | Estimate (95% interval) | Raw p | Adjusted, all 64 | Adjusted, within outcome |', '|---|---|---|---|---:|---:|---:|']
for r in sorted(m, key=lambda r: r['p_rw_all'])[:12]:
    L.append(f"| {r['outcome']} | {r['contrast']} | {r['family']} | {c(r)} | {r['p_raw']:.4f} | {r['p_rw_all']:.4f} | {r['p_rw_outcome']:.4f} |")
L += ['', '## 4. Crop conditioning', '', '| Version | H1 | Placebo |', '|---|---|---|']
L += [f"| {k} | {c(v['H1'])} | {c(v['placebo'])} |" for k, v in d['crop_conditioning'].items()]
L += ['', 'Crop conditioning matters (H1 moves by more than 0.05 SD): no.', '', '### Does entry change rotations?', '', 'Share of seasons in cereals, after entry, E3 matched sample, in share units.', '', '| Family | Effect | Placebo | Entry shifts rotations |', '|---|---|---|---|']
L += [f"| {r['family']} | {c(r['effect'])} | {c(r['placebo'])} | {'yes' if r['shifts'] else 'no'} |" for r in d['rotations']]
open(os.path.join(RES, 'w3_b1_inference.md'), 'w').write('\n'.join(L) + '\n')

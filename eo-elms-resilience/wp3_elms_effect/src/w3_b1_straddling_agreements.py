"""W3-B1 #9, descriptive add-on (record of w3_b1_block_bootstrap_protocol.md, 19 November 2026): how many agreements
in Paper B's samples have fields in more than one held-out region, i.e. can sit on both sides of the train/test split.

Agreement per field: CS CONTRACT_ID by parcel reference; SFI app_id by snapping each action point to the nearest parcel
point within 50 m (the rule of shared/src/build_parcel_schemes.py). Holding identifiers are not published for CS or SFI,
so the agreement stands in for the holding. Never-treated fields have no agreement and cannot be counted.

Output  wp3_elms_effect/results/w3_b1_straddling_agreements.md, .json (counts only)
"""
import json, os
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
import option_detection as od
import w3_4_model_comparison as mc

NAT = os.path.join(od.D, 'schemes', 'national')
SNAP_M = 50


def links(parcels):
    cs = pd.read_csv(os.path.join(NAT, 'cs_options.csv'), usecols=['CONTRACT_ID', 'PARCREF'], dtype=str).dropna()
    cs = pd.DataFrame({'parcref': cs.PARCREF.str.replace(' ', ''), 'agreement': 'CS:' + cs.CONTRACT_ID})
    s = pd.read_csv(os.path.join(NAT, 'sfi_actions.csv'), usecols=['app_id', 'x_bng', 'y_bng'], dtype=str)
    s['x'], s['y'] = pd.to_numeric(s.x_bng, errors='coerce'), pd.to_numeric(s.y_bng, errors='coerce')
    s = s[s.x.notna() & s.y.notna()]
    dist, idx = cKDTree(parcels[['x', 'y']].values).query(s[['x', 'y']].values, k=1)
    sfi = pd.DataFrame({'parcref': parcels.parcref.values[idx], 'agreement': 'SFI:' + s.app_id.values})[dist <= SNAP_M]
    return pd.concat([cs, sfi]).drop_duplicates()


def count(df, L):
    """df: sample fields (parcref, region) on agreement land; L: field-agreement links."""
    m = df.merge(L, on='parcref')
    reg = m.groupby('agreement').region.nunique(); n = m.groupby('agreement').parcref.nunique()
    multi = n[n >= 2].index; strad = reg[reg >= 2].index
    f_strad = m[m.agreement.isin(strad)].parcref.nunique()
    return {'fields': int(df.parcref.nunique()), 'fields_linked': int(m.parcref.nunique()), 'agreements': int(len(n)),
            'agreements_2plus_fields': int(len(multi)), 'agreements_straddling': int(len(strad)),
            'share_of_multi_agreements_straddling': float(len(strad) / max(len(multi), 1)),
            'fields_in_straddling_agreements': int(f_strad), 'share_of_linked_fields': float(f_strad / max(m.parcref.nunique(), 1))}


def main():
    pts = pd.read_parquet(os.path.join(od.D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y']).drop_duplicates('parcref')
    L = links(pts)
    agr, never, mgmt = od.load()
    out, union = {}, []
    for fam, cs in od.FAMILIES.items():
        cs = set(cs)
        pos = agr[agr.codes.map(lambda c: len(c & cs) > 0)]
        comp = never if fam in mc.CONTROLS else mgmt[~mgmt.parcref.isin(pos.parcref)]
        df = od.sample(pos, comp).reset_index(drop=True)
        side = df if fam not in mc.CONTROLS else df[df.y == 1]          # comparison A (never treated) has no agreement
        out[fam] = count(side, L); union.append(side)
        out[fam]['never_treated_fields_not_countable'] = int((df.y == 0).sum()) if fam in mc.CONTROLS else 0
        print(fam, out[fam], flush=True)
    out['All samples together'] = count(pd.concat(union).drop_duplicates('parcref'), L)
    json.dump(out, open(os.path.join(mc.RES, 'w3_b1_straddling_agreements.json'), 'w'), indent=1)
    p = lambda v: f'{100 * v:.1f}%'
    T = ['# W3-B1 #9: agreements that straddle a held-out region boundary', '',
         'Descriptive count for the Paper B text (record of [w3_b1_block_bootstrap_protocol.md](w3_b1_block_bootstrap_protocol.md), '
         '19 November 2026). Agreement per field: Countryside Stewardship contract by parcel reference; SFI agreement by snapping '
         'each action point to the nearest parcel point within 50 m. CS and SFI publish no holding identifier, so the agreement '
         'stands in for the holding; a holding with several agreements in different regions is not detected. Never-treated '
         'fields (comparison A, used only for the two controls) have no agreement and are not counted.', '',
         '| Sample | fields on agreement land | linked to an agreement | agreements | with ≥ 2 sample fields | straddling ≥ 2 regions | fields in straddling agreements |',
         '|---|---|---|---|---|---|---|']
    for k, r in out.items():
        T.append(f"| {k} | {r['fields']:,} | {r['fields_linked']:,} | {r['agreements']:,} | {r['agreements_2plus_fields']:,} | "
                 f"{r['agreements_straddling']:,} ({p(r['share_of_multi_agreements_straddling'])}) | "
                 f"{r['fields_in_straddling_agreements']:,} ({p(r['share_of_linked_fields'])} of linked) |")
    open(os.path.join(mc.RES, 'w3_b1_straddling_agreements.md'), 'w').write('\n'.join(T) + '\n')


if __name__ == '__main__':
    main()

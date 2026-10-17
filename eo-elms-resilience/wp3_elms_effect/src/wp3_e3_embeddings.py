"""WP3 exploratory E3 (decisions record, 17 October 2026, detailed before any embedding was used): the section 7
matching repeated with AlphaEarth pre-entry embeddings.

Pre-entry embedding = each field's mean AlphaEarth embedding 2017-2020; its first 10 principal components are added
to the propensity covariates; matching otherwise unchanged. H1-H3 re-estimated with the frozen-plan estimator and
the within-cohort design, next to the original matched sample.

Output  wp3_elms_effect/results/wp3_e3_embeddings.md, .json; wp3_elms_effect/data/matched_sample_e3.parquet
"""
import glob, json, os
import numpy as np, pandas as pd
from sklearn.decomposition import PCA
import wp3_did as w
import wp3_within_cohort as wc

EMB = os.path.join(w.D, 'embeddings', 'parcels')
BANDS = [f'A{i:02d}' for i in range(64)]


def pre_entry_embedding(parcrefs):
    keep = set(parcrefs); acc = None; cnt = None
    for y in range(2017, 2021):
        parts = [pd.read_parquet(f) for f in sorted(glob.glob(os.path.join(EMB, f'aef_*_{y}.parquet')))]
        d = pd.concat(parts, ignore_index=True)
        d = d[d.parcref.isin(keep)].drop_duplicates('parcref').set_index('parcref')[BANDS].reindex(parcrefs)
        v = d.values.astype('float64'); ok = ~np.isnan(v).any(axis=1)
        acc = np.where(ok[:, None], v, 0) if acc is None else acc + np.where(ok[:, None], v, 0)
        cnt = ok.astype(int) if cnt is None else cnt + ok
    mean = acc / np.maximum(cnt, 1)[:, None]
    mean[cnt == 0] = np.nan
    return mean, cnt


def main():
    d = w.Data()
    t = d.t
    emb, cnt = pre_entry_embedding(t.parcref.values)
    miss = cnt == 0
    fill = np.nanmean(emb, axis=0)
    emb = np.where(np.isnan(emb), fill, emb)
    pcs = PCA(n_components=10, random_state=0).fit(emb)
    Z = pcs.transform(emb)
    for k in range(10):
        t[f'emb_pc{k + 1}'] = Z[:, k]
    w.log('embeddings: fields without any 2017-2020 embedding', int(miss.sum()), 'variance explained by 10 PCs', round(float(pcs.explained_variance_ratio_.sum()), 3))

    base_cov = w.covariates
    def covariates_e3(tt):
        X = base_cov(tt)
        for k in range(10):
            X[f'emb_pc{k + 1}'] = tt[f'emb_pc{k + 1}'].values
        return X
    orig = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet')).in_matched_sample.values
    w.covariates = covariates_e3
    M, bal, ps = w.match(t)
    w.covariates = base_cov
    pd.DataFrame({'parcref': t.parcref, 'in_matched_sample': M}).to_parquet(os.path.join(w.W3, 'data', 'matched_sample_e3.parquet'), index=False)
    emb_bal = bal.loc[[f'emb_pc{k + 1}' for k in range(10)]]
    out = {'sample': {'treated_matched': int(((d.G > 0) & M).sum()), 'control_matched': int(((d.G == 0) & M).sum()),
                      'max_smd_after_all': float(bal.smd_after.max()), 'n_cov_over_0.1': int((bal.smd_after > 0.1).sum()),
                      'max_smd_embedding_pcs_before': float(emb_bal.smd_before.max()), 'max_smd_embedding_pcs_after': float(emb_bal.smd_after.max()),
                      'fields_without_embedding': int(miss.sum())}}
    # embedding balance of the ORIGINAL matched sample, for comparison
    Xe = covariates_e3(t)[[f'emb_pc{k + 1}' for k in range(10)]]
    out['sample']['max_smd_embedding_pcs_original_sample'] = float(w.smd(Xe[orig], (d.G > 0)[orig]).max())
    w.log(out['sample'])

    res = {}
    for lab, mask in (('original matching', orig), ('matching + embeddings (E3)', M)):
        E1 = d.est('ndvi_july_z', pmask=mask)
        W = w.h1(E1)[:1] + w.h3(E1)
        th, V, G, _ = E1.run(W)
        E2 = d.est('ndvi_peak_z', pmask=mask)
        th2, V2, G2, _ = E2.run(w.h2(E2)[:1])
        r = {'H1': w.row('H1', th, V, 0, G), 'H2': w.row('H2', th2, V2, 0, G2), 'H3': w.row('H3', th, V, 1, G)}
        wcr = wc.run(d, mask, ['g'], 'within cohort ' + lab)
        for h in ('H1', 'H2', 'H3'):
            r[h + ' within cohort'] = wcr[h]['after entry']
            r[h + ' within cohort, before entry'] = wcr[h]['before entry']
        res[lab] = r
        w.log(lab, {k: round(v['est'], 3) for k, v in r.items()})
    out['estimates'] = res
    json.dump(out, open(os.path.join(w.RES, 'wp3_e3_embeddings.json'), 'w'), indent=1, default=float)
    s = out['sample']
    L = ['# WP3 E3: matching with AlphaEarth pre-entry embeddings (exploratory)', '',
         'Specified in the decisions record before any embedding was used. Pre-entry embedding = mean 2017–2020; first 10 '
         'principal components added to the matching covariates.', '',
         f"- Matched: {s['treated_matched']:,} agreement fields, {s['control_matched']:,} never-treated fields; "
         f"largest standardised difference after matching {s['max_smd_after_all']:.2f} ({s['n_cov_over_0.1']} covariates above 0.1).",
         f"- Embedding components: largest difference {s['max_smd_embedding_pcs_before']:.2f} before matching; "
         f"{s['max_smd_embedding_pcs_original_sample']:.2f} in the original matched sample; {s['max_smd_embedding_pcs_after']:.2f} with embedding matching.",
         f"- Fields without any 2017–2020 embedding (given the mean): {s['fields_without_embedding']:,}.", '',
         '| Estimate | original matching | matching + embeddings |', '|---|---|---|']
    a, b = res['original matching'], res['matching + embeddings (E3)']
    for k in a:
        L.append(f"| {k} | {a[k]['est']:+.3f} ({a[k]['se']:.3f}) | {b[k]['est']:+.3f} ({b[k]['se']:.3f}) |")
    L += ['', 'H1 = shock minus non-shock effect on July NDVI; H2 = recovery; H3 = land-use change minus management options. '
          'Frozen-plan estimator unless marked "within cohort". Estimate (SE), SE clustered by ERA5 cell.']
    open(os.path.join(w.RES, 'wp3_e3_embeddings.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

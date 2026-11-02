"""Addendum 7: W3-S families to water-mechanism groups (protocol: w3_g_water_mechanisms_protocol.md, Mechanism groups).

Built from the committed W3-S crosswalk (family names, codes and descriptions) only; no outcome or EO feature is read.
Groups: S source (soil cover and structure), P pathway (strips and barriers catching overland flow), K storage (water
held on the land), V conversion (permanent cover replacing arable or crop), N no water mechanism (negative control).
A family fitting two groups goes to the one its description names first; such families carry a note. Not-testable
codes stay out.

Output: wp3_elms_effect/results/w3_g_groups.csv (families and counts only; public).
"""
import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RES = os.path.join(ROOT, 'wp3_elms_effect', 'results')

GROUP = {
    'cover_crops': ('S', ''), 'no_till': ('S', 'includes reduced-depth cultivation on archaeology (small ES/CS codes)'),
    'herbal_leys': ('S', ''),
    'infield_plots': ('S', 'not in the addendum table; sown plots give cover in winter (bird food) or most of the year '
                      '(nectar), so soil cover is the mechanism named first'),
    'area_strips': ('P', 'includes in-field grass strips, watercourse and pond buffers; also overwinter stubble and '
                    'low-input cereal (AHW6-8, AHW10) as registered, which act as source, not pathway'),
    'hedge_management': ('P', ''), 'new_hedges': ('P', ''), 'walls_banks': ('P', ''), 'beetle_banks': ('P', ''),
    'pond_creation': ('K', ''), 'pond_restoration': ('K', ''), 'sfi_ponds_ditches': ('K', 'ditches convey as well as store'),
    'wet_grassland': ('K', ''), 'fen_reedbed': ('K', ''),
    'other_water': ('K', 'swales, leaky and check dams, flood mitigation, raised water levels, sluices, designed water bodies'),
    'arable_reversion': ('V', ''),
    'grassland_options': ('V', 'low-input grassland and field corners (the addendum table); also winter bird food on grassland (IGL2)'),
    'species_rich_grassland': ('V', ''),
    'in_field_trees': ('V', 'in-field trees, agroforestry and orchards (the addendum table); largest codes protect existing trees'),
    'woodland_creation': ('V', ''),
    'wood_pasture': ('V', 'mixes management, restoration and creation (WD6 creation is the largest CS code)'),
    'scrub_successional': ('V', 'mixes management and creation of scrub'),
    'management_only': ('N', ''), 'grazing_regime': ('N', ''), 'seasonal_livestock_removal': ('N', ''),
    'organic': ('N', 'organic management names no water mechanism; leys within organic rotations are not identifiable'),
    'rush_pastures': ('N', 'management of existing rush pasture'), 'moorland_rough_grazing': ('N', 'grazing levels on existing moorland'),
    'historic_grassland': ('N', 'keeps existing grassland over archaeology'),
    'lowland_heathland': ('N', 'mostly management of existing heath (LH1); creation codes are small'),
    'woodland_management': ('N', 'management of existing woodland: no change in cover (the addendum table lists woodland under V, '
                            'meant for creation, which is woodland_creation)'),
    'other_land': ('N', 'coastal habitats and scrub, bracken and rhododendron control'),
}
NAME = {'S': 'source', 'P': 'pathway', 'K': 'storage', 'V': 'conversion', 'N': 'no water mechanism'}


def main():
    X = pd.read_csv(os.path.join(RES, 'w3_s_crosswalk.csv'), keep_default_na=False)
    X = X[X.group != 'X']
    f = X.groupby(['family', 'group', 'expectation']).agg(codes=('code', 'size'), parcel_code_pairs=('parcels', 'sum')).reset_index()
    assert set(f.family) == set(GROUP), set(f.family) ^ set(GROUP)
    f['mechanism_group'] = f.family.map(lambda k: GROUP[k][0])
    f['mechanism'] = f.mechanism_group.map(NAME)
    f['note'] = f.family.map(lambda k: GROUP[k][1])
    f = f.rename(columns={'group': 'w3s_group'}).sort_values(['mechanism_group', 'family'])
    f[['family', 'mechanism_group', 'mechanism', 'w3s_group', 'expectation', 'codes', 'parcel_code_pairs', 'note']].to_csv(
        os.path.join(RES, 'w3_g_groups.csv'), index=False)
    print(f.groupby('mechanism_group').agg(families=('family', 'size'), codes=('codes', 'sum'), pairs=('parcel_code_pairs', 'sum')))


if __name__ == '__main__':
    main()

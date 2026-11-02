"""W3-S Part A, step 2: the crosswalk (protocol: w3_s_option_stacks_protocol.md, Part A).

Every code in the inventory (w3_s_inventory.csv) gets a group, a family and an expectation, from its code, description
and unit only. No outcome or EO feature is read. Rules, applied in this order:
1. Codes in a family registered earlier (W3-4, W3-1, wet grassland, ponds) keep that family.
2. Not testable: capital items, buildings and works unrelated to land cover, payment supplements, base or threshold
   payments, assessments, access, deer and squirrel control.
3. A code that does the same thing as a registered family's codes (another scheme or version of the same action) joins
   that family.
   Codes that mean different things in two schemes are keyed as SCHEME:CODE.
4. Codes with at least 1,000 parcels that fit no family form new families, one per management purpose; codes with fewer
   join the nearest family of the same group (or 'other land' / 'other water' if none fits).
Every assignment that is not obvious carries a note. Groups: L land management, I linear features, W ponds and water,
X not testable.

Output: wp3_elms_effect/results/w3_s_crosswalk.csv and w3_s_crosswalk_summary.md (codes and counts only; public).
"""
import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RES = os.path.join(ROOT, 'wp3_elms_effect', 'results')

# family: (group, expectation, source, codes). Expectation: visible (10 m), not_visible (negative control).
FAMILIES = {
    # registered earlier (rule 1), extended by rule 3
    'herbal_leys': ('L', 'visible', 'W3-4', 'SAM3 CSAM3'),
    'cover_crops': ('L', 'visible', 'W3-4', 'SAM2 CSAM2 SOH2 SOH3 SOH4'),
    'no_till': ('L', 'visible', 'W3-4', 'SOH1 HD6 HS3 HS9 ED3 HD3 OD3 OHD3'),
    'infield_plots': ('L', 'visible', 'W3-4', 'AHL1 AHL2 CAHL1 CAHL2 AHW1 AHW4 AHW5 EF2NR EF4NR HF2NR HF4NR HF12NR HF13NR '
                      'HF15NR HF20NR HG2NR HG3 OF2NR OF4NR OHF2NR OHF4NR OHF13NR'),
    'grassland_options': ('L', 'visible', 'W3-4', 'LIG1 CLIG3 IGL2 CIGL2 GS1 GS2 LIG2 GS5 IGL1 CIGL1 EK1 EK2 EK3 EL1 EL2 EL3 '
                          'HK1 HK2 HK3 HL1 HL2 HL3 OK1 OK2 OK3 OL2 OL3 OHK1 OHK2 OHK3 OHL3 SW8 WBD5 WBD8 SW13 HJ6'),
    'management_only': ('L', 'not_visible', 'W3-4 control', 'SAM1 CSAM1 IPM2 IPM3 IPM4 CIPM2 CIPM3 CIPM4 NUM2 NUM3 CNUM2 '
                        'CNUM3 PRF1 PRF2 PRF4'),
    'area_strips': ('I', 'visible', 'W3-1 (W3-4 buffer strips and margins)', 'SW1 SW3 AHW6 AHW7 AHW8 AHW9 AHW10 AHW11 '
                    'AHL3 AHL4 CAHL3 CAHL4 AB8 SW2 SW4 SW11 IGL3 CIGL3 WBD3 BFS1 BFS2 BFS3 BFS6 WT1 WT2 EE1 EE2 EE3 EE4 '
                    'EE5 EE6 EE7 EE8 EE9 EE10 EJ5 EJ9 ES:HE1 HE2 ES:HE3 HE4 HE5 HE6 HE7 HE8 HE10 HE11 HJ5 HJ9 OE1 OE2 OE3 OE4 OE5 '
                    'OE6 OE7 OE8 OE9 OE10 OHE1 OHE2 OHE3 OHE4 OHE5 OHE6 OHE7 OHE8 OHJ5 OHJ9 OJ5 OJ9 EF1 HF1 OF1 OHF1 EF11 '
                    'HF11 OHF11 HF9NR HF10NR HF14NR HG6NR HG7NR OFA1 EC24 EC25 HC24 HC25 OC24 OC25 OHC24'),
    'new_hedges': ('I', 'visible', 'W3-1', 'BN11 BN7 TE4D'),
    'hedge_management': ('I', 'not_visible', 'W3-1', 'BE3 BN5 BN6 HRW1 HRW2 HRW3 CHRW1 CHRW2 CHRW3 HB11 HB12 TE1'),
    'walls_banks': ('I', 'not_visible', 'W3-1', 'BN12 BN13 BN14 BN1 BN2 BN3 BN4 BND1 BND2'),
    'wet_grassland': ('W', 'visible', 'addendum 4', 'GS9 GS10 GS11 GS12 HK9 HK10 HK11 HK12 HK13 HK14 HS7 HD10 HD11'),
    'fen_reedbed': ('W', 'visible', 'addendum 4', 'WT6 WT8 WT9 WT7 HQ3 HQ4 HQ5 HQ6 HQ7 HQ8 WT10 HQ9 HQ10'),
    'pond_creation': ('W', 'visible', 'W3-W', 'WN5A WN6A WN2 RP7'),
    'pond_restoration': ('W', 'not_visible', 'W3-W', 'WN5B WN6B WT4 WT5 HQ1 HQ2 WN7'),
    'sfi_ponds_ditches': ('W', 'not_visible', 'W3-W', 'WBD1 WBD2 WT3 HB14 WN3 WN4'),
    # new families (rule 4)
    'beetle_banks': ('I', 'not_visible', 'new', 'AB3 AHW3 EF7 HF7 OF7 OHF7'),
    'species_rich_grassland': ('L', 'visible', 'new', 'GS6 GS7 GS8 GS13 GS14 HK6 HK7 HK8 HK15 HK16 HK17 GRH6 UL20 UHL20 '
                               'UOL20 UOHL20 UL21 UHL21 UOL21'),
    'organic': ('L', 'visible', 'new', 'OT1 OT2 OT5 OT6 OR1 OR2 OR5 OU1 ILC TFC OFC1 OFC2 OFC3 OFC4 OFC5 OFM1 OFM2 OFM4 '
                'OFM5 OFM6'),
    'rush_pastures': ('L', 'not_visible', 'new', 'EL4 EK4 HK4 HL4 OK4 OL4 OHK4'),
    'moorland_rough_grazing': ('L', 'not_visible', 'new', 'UP1 UP2 UP3 EL5 EL6 HL5 HL6 HL7 HL8 HL9 HL10 HL11 HL12 OL5 OHL5 '
                               'UL22 UL23 UHL23 UOL22 UOL23 GRH1 UPL1 UPL2 UPL3 UPL7 UPL8 UPL9 UPL10'),
    'grazing_regime': ('L', 'not_visible', 'new', 'EK5 HK5 OK5 OHK5 UL18 UHL18 UOL18 UL17 UHL17'),
    'seasonal_livestock_removal': ('L', 'not_visible', 'new', 'SW9 SW10 WBD6 WBD7 HJ7 UJ12 UHJ12 UOJ12'),
    'lowland_heathland': ('L', 'not_visible', 'new', 'LH1 LH2 LH3 HO1 HO2 HO3 HO4 HO5'),
    'in_field_trees': ('L', 'not_visible', 'new', 'EC1 EC2 BE1 BE2 BFS4 BFS5 HC1 HC2 HC5 HC6 OC1 OC2 OHC1 OHC2 AGF1 AGF2 AF1 '
                       'AF2 TE2 TE3 BE4 BE5 HC18 HC19 HC20 HC21'),
    'woodland_creation': ('L', 'visible', 'new', 'WD1 HC9 HC10 TE4A TE4B TE4C'),
    'woodland_management': ('L', 'not_visible', 'new', 'WD2 HC7 HC8 WD3 EC4 HC4 OC4 OHC4 AHW12 WS2 UC22 UHC22'),
    'wood_pasture': ('L', 'not_visible', 'new', 'WD4 WD5 WD6 WD10 WD11 WD12 HC12 HC13 HC14'),
    'scrub_successional': ('L', 'visible', 'new', 'WD7 WD8 HC15 HC16 HC17 SCR1 SCR2 HS4 ED4 HD4 OD4 OHD4 HEF5'),
    'historic_grassland': ('L', 'not_visible', 'new', 'ED5 HS5 HD5 OD5 OHD5 HEF6 UD13 UHD13 UOD13'),
    'arable_reversion': ('L', 'visible', 'new', 'SW7 WBD4 HJ3 HJ4 HD7 SW15 HS2 ED2 HD2 OD2 OHD2'),
    'other_land': ('L', 'not_visible', 'pooled', 'CT1 CT3 CT5 CT7 HP1 HP2 HP4 HP5 HP6 HP7 HP8 HP9 HP10 HP11 HIOS1 HIOS2 '
                   'HIOS3 HIOS4 SB1A SB1B SB1C SB1D SB1E SB1F SB4 SB5 SB6A SB6B SB6C'),
    'other_water': ('W', 'not_visible', 'pooled', 'SW12 SW16 SW18 WN1 WN8 WN9 WN10 RP8 RP9 RP10 RP11 RP12 RP32 RP33 HS6 HD8 HD9 '
                    'HEF8'),
}

NOT_TESTABLE = {
    'capital item or works unrelated to land cover': 'AC1 AQ1 AQ2 BC4 FG1 FG2 FG3 FG4 FG5 FG7 FG8 FG9 FG10 FG11 FG12 FG13 '
        'FG14 FG15 FG16 FG17 FY1 LV1 LV3 LV4 LV5 LV6 LV7 LV8 RP1 RP2 RP3 RP4 RP5 RP6 RP13 RP14 RP15 RP16 RP17 RP18 RP19 '
        'RP20 RP21 RP22 RP23 RP24 RP25 RP26 RP27 RP28 RP29 RP30 TE5 TE6 TE7 TE8 TE9 TE10 TE11 TE12 TE13 TE14 BE6 SB3 '
        'CS:HE1 CS:HE3 FM1 PA1 HJ11',
    'building': 'HS1 HS8 HEF1 HEF2',
    'payment supplement': 'SP1 SP2 SP3 SP4 SP5 SP6 SP7 SP8 HR1 HR2 HR4 HR5 HR6 HR7 HR8 GS15 GS16 GRH7 GRH8 GRH10 GRH11 '
        'SPM2 SPM3 SPM5 UPL6 EE12 HE12 OHE12 OE12 WT11 WT12 HQ11 HQ12 HQ13 HK18 HK19 UP4 UP5 UP6 HL13 HL15 HL16 CT6 SW14 '
        'WBD9 HJ8 BN8 BN9 BN10 BN15 BE7 HC11 WD9 SB2',
    'base, threshold or non-payment option': 'A13 OPTELSTHR OPTOELSTHR UX1 UX2 UX3 UOX2 UOX3',
    'assessment or record': 'MOR1 CMOR1',
    'access': 'HN2 HN3 HN4 HN5 HN6 HN7 WS4',
    'deer or squirrel control': 'WS1 WS3',
}

NOTES = {
    'AHW6': 'overwinter stubble, not a strip; kept where W3-4 and W3-1 registered it',
    'AHW7': 'overwinter stubble, not a strip; kept where W3-4 and W3-1 registered it',
    'AHW8': 'whole-crop spring cereal and stubble, not a strip; kept as registered',
    'AHW10': 'low-input cereal crop, not a strip; kept as registered',
    'OFA1': 'overwinter stubble (organic); joins area_strips because AHW6/7 are there',
    'HG6NR': 'fodder crop for arable mosaic; joins area_strips with AHW10 (low-input cereal)',
    'HG7NR': 'low-input spring cereal; joins area_strips with AHW10',
    'IPM2': 'flower-rich margins: W3-4 registered as management-only control; kept there',
    'CIPM2': 'flower-rich margins: W3-4 registered as management-only control; kept there',
    'IPM3': 'companion crop: W3-4 registered as management-only control; kept there',
    'CIPM3': 'companion crop: W3-4 registered as management-only control; kept there',
    'SOH4': 'winter cover after maize: same purpose as cover crops',
    'HD6': 'direct drilling (ES): same action as no-till',
    'HS3': 'reduced-depth non-inversion cultivation on archaeology: nearest is no_till (small code)',
    'HS9': 'restricted-depth establishment on archaeology: nearest is no_till (small code)',
    'ED3': 'non-inversion cultivation on archaeology: nearest is no_till',
    'HD3': 'non-inversion cultivation on archaeology: nearest is no_till',
    'OD3': 'non-inversion cultivation on archaeology: nearest is no_till',
    'OHD3': 'non-inversion cultivation on archaeology: nearest is no_till',
    'LIG2': 'very low inputs in SDAs: same action as LIG1, joins grassland_options',
    'GS5': 'very low inputs in SDAs: same action as GS2, joins grassland_options (W3-S candidate "low-input grassland" not formed)',
    'IGL1': 'grassland field corners out of management: same action as GS1 (grassland_options)',
    'CIGL1': 'grassland field corners out of management: same action as GS1 (grassland_options)',
    'EK2': 'ES low-input permanent grassland: same action as GS2', 'EK3': 'ES very low-input grassland: same action as GS2',
    'EL2': 'ES low-input in-bye grassland (SDA): same action as GS5', 'EL3': 'ES very low-input in-bye (SDA): same action as GS5',
    'OK2': 'organic ES version of EK2', 'OK3': 'organic ES version of EK3',
    'SW8': 'intensive grassland next to a watercourse, managed with low inputs: nearest is grassland_options',
    'WBD5': 'intensive grassland next to a watercourse: same as SW8',
    'WBD8': 'grassland to reduce nutrients in groundwater: nearest is grassland_options',
    'SW13': 'very low nitrogen to groundwaters: nearest is grassland_options',
    'HJ6': 'preventing erosion or run-off from intensive grassland: nearest is grassland_options',
    'SW2': 'buffer strip on intensive grassland (negative control in addendum 4 Part B); same type as SW1',
    'SW4': 'watercourse buffer: in W3-4 buffer-strip control; joins area_strips',
    'SW11': 'riparian strip, 998 parcels (< 1,000): W3-S candidate family not formed; joins area_strips',
    'WT1': 'buffers around ponds and ditches: a strip; joins area_strips (water-related)',
    'WT2': 'buffers around ponds and ditches: a strip; joins area_strips (water-related)',
    'BFS2': 'pond buffer: a strip; joins area_strips', 'BFS3': 'pond buffer: a strip; joins area_strips',
    'HE10': 'floristically enhanced margin: same as AB8', 'EF1': 'arable field corners (ES): same as AHL3',
    'HF1': 'arable field corners (ES): same as AHL3',
    'EC24': 'hedgerow-tree buffer strip: a strip; joins area_strips', 'TE1': 'hedgerow tree planting: as HRW3',
    'TE4D': 'tree planting for hedges and clumps: nearest is new_hedges',
    'AB3': 'beetle bank (W3-S candidate); about 2 m wide, so not expected visible at 10 m',
    'WN2': 'scrapes: shallow open water, nearest is pond_creation', 'RP7': 'sediment ponds: nearest is pond_creation',
    'WN7': 'restoration of large water bodies', 'WT3': 'ditches of high environmental value: nearest is SFI ponds and ditches',
    'HB14': 'ditches of very high environmental value: nearest is SFI ponds and ditches',
    'WN3': 'ditch restoration: nearest is SFI ponds and ditches', 'WN4': 'ditch creation: nearest is SFI ponds and ditches',
    'GS12': 'creation of wet grassland for wintering birds; not in addendum 4 list (GS9-11), joins by rule 3',
    'HS7': 'historic water meadows: nearest is wet_grassland', 'HD10': 'water meadows: nearest is wet_grassland',
    'HD11': 'water meadows: nearest is wet_grassland',
    'WT10': 'lowland raised bog: nearest is fen_reedbed', 'HQ9': 'lowland raised bog: nearest is fen_reedbed',
    'HQ10': 'lowland raised bog: nearest is fen_reedbed',
    'UL20': 'upland meadow haymaking (option, not supplement): nearest is species_rich_grassland',
    'UL21': 'no-cutting strip in meadows: nearest is species_rich_grassland',
    'OU1': 'whole-farm organic management (ES)', 'ILC': 'organic conversion payment for improved land',
    'EL4': 'rush pastures: new family (>= 1,000 parcels); not wet grassland for waders',
    'UL17': 'no supplementary feeding on moorland: nearest is grazing_regime',
    'SW9': 'not visible (W3-S candidate)', 'LH1': 'management of existing heath: not expected visible',
    'BE4': 'traditional orchards, 808 parcels (< 1,000): W3-S candidate not formed; joins in_field_trees',
    'BE5': 'orchard creation (< 1,000): joins in_field_trees', 'AGF1': 'agroforestry (< 1,000): joins in_field_trees',
    'AGF2': 'agroforestry (< 1,000): joins in_field_trees', 'TE2': 'parkland tree planting (capital, land cover): in_field_trees',
    'TE3': 'fruit-tree planting (capital, land cover): in_field_trees',
    'WD1': 'woodland creation (maintenance payment): expected visible as trees grow',
    'WD3': 'woodland edges on arable land: nearest is woodland_management', 'EC4': 'woodland edges: as WD3',
    'AHW12': 'woodland edges on arable land: as WD3', 'UC22': 'woodland livestock exclusion: woodland_management',
    'HS4': 'scrub on archaeology: nearest is scrub_successional', 'HEF5': 'scrub on archaeology: nearest is scrub_successional',
    'HS2': 'archaeology taken out of cultivation: nearest is arable_reversion',
    'ED2': 'archaeology taken out of cultivation: nearest is arable_reversion',
    'SW15': 'flood mitigation on arable reversion: arable_reversion (mechanism also water storage)',
    'SW12': 'making space for water: other_water', 'SW16': 'flood mitigation on permanent grassland: other_water',
    'SW18': 'raised water levels on peat grassland: other_water',
    'RP11': 'swales (capital, water): other_water', 'RP12': 'check and woody debris dams: other_water',
    'RP32': 'small leaky woody dam: other_water', 'RP33': 'large leaky woody dam: other_water',
    'CT1': 'coastal habitat: no coastal family (all codes < 1,000); other_land',
    'SB4': 'bracken control: other_land', 'SB1A': 'scrub control and felling diseased trees: other_land',
    'SP2': 'raised water level supplement: payment supplement (water-relevant)',
    'HK19': 'raised water levels supplement: payment supplement (water-relevant)',
    'HQ13': 'inundation grassland supplement: payment supplement (water-relevant)',
    'UP5': 'moorland re-wetting supplement: payment supplement (water-relevant)',
    'HL13': 'moorland re-wetting supplement: payment supplement (water-relevant)',
    'BN13': 'stone wall supplement: kept in walls_banks as W3-1 registered',
    'BN14': 'stone wall supplement: kept in walls_banks as W3-1 registered',
    'HRW1': 'hedgerow assessment: kept in hedge_management as W3-1 registered',
    'CHRW1': 'hedgerow assessment: kept in hedge_management as W3-1 registered',
    'SAM1': 'soil assessment: kept in management_only as W3-4 registered',
    'A13': 'non-payment permanent-grassland option', 'UX2': 'Uplands ELS base payment by land type',
    'MOR1': 'moorland assessment and record', 'FG2': 'no description in the SFI list; metres; FG = fencing in CS',
    'RP5': 'cross drains on tracks', 'RP6': 'piped culverts and ditches (yard and track drainage)',
}
NO_DESC = 'HF15NR HP4 OC25 OE12 OE7 OF2NR OHC1 OHC2 OHC24 OHE1 OHE2 OHE4 OHE7 OHE8 OHF13NR OHF2NR OHJ5 OHJ9 OJ9 OK1 UOL22'


def main():
    inv = pd.read_csv(os.path.join(RES, 'w3_s_inventory.csv'), keep_default_na=False)
    rows = {}
    for fam, (g, e, src, codes) in FAMILIES.items():
        for c in codes.split():
            assert c not in rows, c
            rows[c] = dict(group=g, family=fam, expectation=e, family_source=src, reason='')
    for why, codes in NOT_TESTABLE.items():
        for c in codes.split():
            assert c not in rows, c
            rows[c] = dict(group='X', family='not_testable', expectation='not_testable', family_source='', reason=why)
    nd = set(NO_DESC.split())
    out = []
    for r in inv.itertuples():
        a = rows.get(f'{r.scheme}:{r.code}', rows.get(r.code))
        assert a is not None, f'unassigned {r.scheme} {r.code}'
        note = NOTES.get(r.code, '')
        if r.code in nd:
            note = (note + '; ' if note else '') + 'no description in the layer; assigned from the code pattern of its sibling codes'
        out.append(dict(scheme=r.scheme, code=r.code, description=r.description, unit=r.unit, parcels=r.parcels, **a, note=note))
    X = pd.DataFrame(out)
    extra = set(rows) - set(inv.code) - set(inv.scheme + ':' + inv.code)
    assert not extra, f'codes listed but not in the inventory: {sorted(extra)}'
    X.to_csv(os.path.join(RES, 'w3_s_crosswalk.csv'), index=False)

    fam = X.groupby(['group', 'family', 'expectation', 'family_source']).agg(codes=('code', 'size'), parcel_code_pairs=('parcels', 'sum')).reset_index()
    nt = X[X.group == 'X'].groupby('reason').agg(codes=('code', 'size'), parcel_code_pairs=('parcels', 'sum')).reset_index()
    L = ['# W3-S crosswalk: summary', '',
         'Built from code, description and unit only ([`src/w3_s_crosswalk.py`](../src/w3_s_crosswalk.py)); no outcome or EO '
         'feature read. Full table: [w3_s_crosswalk.csv](w3_s_crosswalk.csv). Parcel counts are parcels carrying the code '
         '(CS and SFI starting 2021–2024; ES live in 2021–2024; SFI snapped within 50 m), summed over codes.', '',
         f'- Codes: {len(X)} (CS {sum(X.scheme == "CS")}, SFI {sum(X.scheme == "SFI")}, ES {sum(X.scheme == "ES")}); '
         f'testable {sum(X.group != "X")}, not testable {sum(X.group == "X")}; with a note {sum(X.note != "")}.', '',
         '| Group | Family | Expectation | Source | Codes | Parcel-code pairs |', '|---|---|---|---|---|---|']
    L += [f'| {r.group} | {r.family} | {r.expectation} | {r.family_source} | {r.codes} | {r.parcel_code_pairs:,} |' for r in fam.itertuples()]
    pc = pd.read_parquet(os.path.join(ROOT, 'wp3_elms_effect', 'data', 'w3_s_parcel_codes.parquet'))
    pc = pc.merge(X[['scheme', 'code', 'group']], on=['scheme', 'code'], how='left')
    only = pc.groupby('parcref').group.agg(lambda g: set(g) == {'X'})
    L += ['', f'Parcels with any code: {len(only):,}; parcels whose only codes are not testable: {int(only.sum()):,} ({only.mean():.1%}).']
    L += ['', '**Not testable, by reason:**', '', '| Reason | Codes | Parcel-code pairs |', '|---|---|---|']
    L += [f'| {r.reason} | {r.codes} | {r.parcel_code_pairs:,} |' for r in nt.itertuples()]
    open(os.path.join(RES, 'w3_s_crosswalk_summary.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()

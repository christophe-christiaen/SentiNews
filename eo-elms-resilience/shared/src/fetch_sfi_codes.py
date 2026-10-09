"""SFI / CS action-code lookup.
Sources: (1) Defra 'SFI action uptake data' workbook (SFI23 and SFI24 action codes and names, OGL v3);
(2) GOV.UK 'Find funding for land or farms' finder via the search API (current versions, incl. SFI26 and CS).
Writes shared/config/action_codes.csv (code, title, source, url). The uptake workbook wins where both exist.
SFI26 records in the RPA layer carry a "_26" suffix (e.g. CHRW2_26): strip it before looking up."""
import csv, os, re, requests
import pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
rows, start = {}, 0
while True:
    d = requests.get('https://www.gov.uk/api/search.json', params={'filter_format': 'farming_grant', 'count': 100, 'start': start,
                                                                  'fields': 'title,link'}, timeout=60).json()
    res = d.get('results', [])
    for r in res:
        m = re.match(r'^([A-Z]{2,6}\d{1,2})[:\s]+(.*)', r['title'])
        if m:
            rows[m.group(1)] = (m.group(2).strip(), 'https://www.gov.uk' + r['link'])
    if len(res) < 100:
        break
    start += 100
out = {k: (t, 'GOV.UK finder', u) for k, (t, u) in rows.items()}
UPTAKE = ('https://assets.publishing.service.gov.uk/media/690b6e489456634d9795fe2f/SFI_option_data2025-11-04.ods')
ref = os.path.join(ROOT, 'shared', 'data', 'reference', 'SFI_option_data2025-11-04.ods')
if not os.path.exists(ref):
    os.makedirs(os.path.dirname(ref), exist_ok=True); open(ref, 'wb').write(requests.get(UPTAKE, timeout=120).content)
for sheet, scheme in (('Number_of_agreements_SFI23', 'SFI23'), ('Number_of_agreements_SFI24', 'SFI24')):
    t = pd.read_excel(ref, sheet_name=sheet, engine='odf', header=None)
    for code, title in zip(t[0], t[1]):
        if isinstance(code, str) and re.fullmatch(r'[A-Z]{2,6}\d{1,2}', code.strip()):
            out[code.strip()] = (str(title).strip(), f'Defra SFI uptake data ({scheme})', UPTAKE)
fn = os.path.join(ROOT, 'shared', 'config', 'action_codes.csv')
with open(fn, 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['code', 'title', 'source', 'url'])
    for k in sorted(out):
        w.writerow([k, *out[k]])
rows = out
print(len(rows), 'codes ->', os.path.relpath(fn, ROOT))

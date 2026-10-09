"""Cross-sensor check: MODIS/Aqua MYD13Q1 NDVI for the same sites, 2016-2026.
Terra's orbit has drifted to earlier overpasses since ~2020 and Aqua's to later ones,
so agreement between the two argues against drift artefacts in recent anomalies."""
import json, os, time, requests
from concurrent.futures import ThreadPoolExecutor
from sites import SITES, KM
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'modis_aqua'); os.makedirs(OUT, exist_ok=True)
API = 'https://modis.ornl.gov/rst/api/v1/MYD13Q1/subset'
S = requests.Session()
def job(a):
    reg, i, lat, lon, y = a
    fn = f"{OUT}/MYD13Q1_NDVI_{reg.replace(' ', '_').replace('&', 'and')}_{i}_{y}.json"
    if os.path.exists(fn): return
    for k in range(6):
        try:
            r = S.get(API, params=dict(latitude=lat, longitude=lon, band='250m_16_days_NDVI', startDate=f'A{y}081',
                                       endDate=f'A{y}225', kmAboveBelow=KM, kmLeftRight=KM), timeout=120)
            if r.status_code == 200: json.dump(r.json(), open(fn, 'w')); return
        except Exception: pass
        time.sleep(2 * (k + 1))
jobs = [(reg, i, lat, lon, y) for reg, pts in SITES.items() for i, (lat, lon) in enumerate(pts) for y in range(2016, 2027)]
with ThreadPoolExecutor(12) as ex: list(ex.map(job, jobs))
print('done', len(os.listdir(OUT)))

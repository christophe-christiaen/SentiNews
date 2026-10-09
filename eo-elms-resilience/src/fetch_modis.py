import requests, json, os, sys, time, itertools
from concurrent.futures import ThreadPoolExecutor
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'modis')
API = 'https://modis.ornl.gov/rst/api/v1'
KM = 3
SITES = {
 'North East': [(55.35,-1.70),(55.05,-1.80),(54.60,-1.45),(55.68,-2.10),(54.85,-1.60)],
 'North West and Merseyside': [(53.83,-2.90),(53.60,-2.85),(53.10,-2.75),(54.70,-2.75),(53.33,-3.05)],
 'Yorkshire & The Humber': [(54.05,-0.55),(53.80,-0.10),(54.00,-1.30),(53.70,-0.95),(54.20,-0.80)],
 'East Midlands': [(53.20,-0.40),(52.85,-0.10),(53.40,-0.20),(52.40,-0.85),(53.20,-0.95)],
 'West Midlands': [(52.75,-2.60),(52.10,-2.75),(52.25,-1.50),(52.85,-2.05),(52.15,-2.05)],
 'Eastern': [(52.35,0.05),(52.70,0.90),(52.25,1.00),(51.85,0.50),(52.05,-0.25)],
 'South East and London': [(51.15,-1.25),(51.65,-1.30),(51.25,1.10),(50.90,-0.70),(51.50,-1.10)],
 'South West': [(51.25,-1.85),(50.80,-2.25),(51.05,-2.65),(51.75,-1.85),(50.85,-3.30)],
 'Scotland': [(56.25,-3.05),(56.65,-2.75),(57.40,-2.30),(55.95,-2.65),(55.70,-2.30)],
 'Wales': [(51.45,-3.40),(51.75,-4.95),(51.75,-2.85),(53.25,-4.35),(53.20,-3.10)],
}
S = requests.Session()
def get(url, params):
    for a in range(6):
        try:
            r = S.get(url, params=params, timeout=120)
            if r.status_code == 200: return r.json()
        except Exception as e: pass
        time.sleep(2*(a+1))
    raise RuntimeError(url+str(params))
def job(args):
    reg, i, lat, lon, prod, band, y, d0, d1 = args
    fn = f"{OUT}/{prod}_{band}_{reg.replace(' ','_').replace('&','and')}_{i}_{y}_{d0}.json"
    if os.path.exists(fn): return
    j = get(f"{API}/{prod}/subset", dict(latitude=lat, longitude=lon, band=band,
        startDate=f"A{y}{d0:03d}", endDate=f"A{y}{d1:03d}", kmAboveBelow=KM, kmLeftRight=KM))
    json.dump(j, open(fn,'w'))
jobs=[]
for reg, pts in SITES.items():
    for i,(lat,lon) in enumerate(pts):
        jobs.append((reg,i,lat,lon,'MCD12Q1','LC_Type1',2019,1,1))
        for y in range(2001, 2027):  # 2026 season complete by mid-Aug
            jobs.append((reg,i,lat,lon,'MOD13Q1','250m_16_days_NDVI',y,81,225))
print(len(jobs), flush=True)
t=time.time(); n=0
with ThreadPoolExecutor(12) as ex:
    for _ in ex.map(job, jobs):
        n+=1
        if n%250==0: print(n, round(time.time()-t), flush=True)
print('done', time.time()-t)

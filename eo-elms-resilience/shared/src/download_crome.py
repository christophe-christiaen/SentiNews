"""Resumable download of CROME geodatabases via Defra's signed direct links (Azure file share, supports Range).

The portal's /api/file/download stream drops mid-file and cannot resume; the 'download-url' endpoint returns a
signed link (valid ~24 h) that can. Each file is fetched with curl -C - until it reaches the size Defra lists, getting
a fresh link on every attempt. Several years download in parallel.

Output  shared/data/reference/crome/zips/Crop_Map_of_England_CROME_<year>*.gdb.zip
Usage   python download_crome.py --years 2016 2017 2018 --workers 3
"""
import argparse, os, subprocess, time
from concurrent.futures import ThreadPoolExecutor
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'shared', 'data', 'reference', 'crome', 'zips')
LIST = 'https://environment.data.gov.uk/backend/catalog/api/file-management/data-sets/{}?isSystemManaged=true'
SIGN = 'https://environment.data.gov.uk/file-management-open/data-sets/{}/files/{}/download-url'
FILESETS = {2016: 'c92cb911-b4f4-4582-bf57-f7f98c8d36e9', 2017: '63826b94-669a-4094-a206-470d399df3c8',
            2018: 'c369347b-53d4-4f92-821e-273089d773de', 2019: '1aaba8cc-9d93-480e-a29a-7a92324cc5b8',
            2020: '41adeeb3-89f1-4a86-8982-c2d27b5f3e6f', 2021: 'f447e4c3-4783-4e83-b9e4-61694f439d82',
            2022: '9eff03a0-55ce-44fd-b29b-9735f8d71e8d', 2023: '4f8fbd8e-ccec-4fbb-b346-575b58afb38a',
            2024: '2c6afc6a-ece4-4656-ac30-0ebaeb0459a3', 2025: 'dc01d521-c1dc-410b-a575-09b58f9404b7'}


def fetch(year, max_tries=200):
    fs = FILESETS[year]
    f = next(x for x in requests.get(LIST.format(fs), timeout=60).json()['files'] if x['name'].endswith('.gdb.zip'))
    path = os.path.join(OUT, f['name'])
    for k in range(max_tries):
        have = os.path.getsize(path) if os.path.exists(path) else 0
        if have >= f['size']:
            print(f'{year}: complete {have / 1e9:.2f} GB', flush=True)
            return path
        try:
            url = requests.get(SIGN.format(fs, f['name']), timeout=60).json()['url']
            real = int(requests.head(url, timeout=60).headers.get('Content-Length', f['size']))
        except Exception:
            time.sleep(60); continue
        if real != f['size']:            # the catalogue size can differ from the stored file (e.g. 2025)
            f['size'] = real
            if have >= real:
                print(f'{year}: complete {have / 1e9:.2f} GB', flush=True)
                return path
        subprocess.run(['curl', '-sS', '-C', '-', '--speed-time', '300', '--speed-limit', '500', '-o', path, url])
        now = os.path.getsize(path) if os.path.exists(path) else 0
        print(f'{year}: {now / 1e9:.2f} of {f["size"] / 1e9:.2f} GB (attempt {k + 1})', flush=True)
        if now == have:
            time.sleep(60)
    raise RuntimeError(f'{year}: gave up')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--years', nargs='*', type=int, default=sorted(FILESETS))
    ap.add_argument('--workers', type=int, default=3)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(a.workers) as ex:
        for r in ex.map(fetch, a.years):
            pass

#!/usr/bin/env python3
import datetime
import hashlib
import os
import random
import sys
import time
from urllib.parse import parse_qs

import requests
from bs4 import BeautifulSoup

from gigacluster import CACHE

PREFIX = '/news/rtc?'
REGION = 'au'

def make_all_coverage_url(cluster_id, region=REGION):
    return 'https://news.google.com/news/story?cf=all&ned={}&hl=en&topic=h&ncl={}'.format(region, cluster_id)

if len(sys.argv) == 1:
    r = requests.get('http://news.google.com')
    now = datetime.datetime.now()
    day = now.strftime('%y%m%d')
    indices = os.path.join(CACHE, '_indices', day)
    if not os.path.isdir(indices):
        os.makedirs(indices)
    filename = os.path.join(indices, '{}.html'.format(now.strftime('%H%M%S')))
    with open(filename, 'w') as f:
        f.write(r.text)
    files = [filename]
else:
    files = sys.argv[1:]

fetch_queue = []
for filename in files:
    with open(filename) as f:
        s = BeautifulSoup(f.read())
        for l in s.find_all('a'):
            if 'href' in l.attrs and l.attrs['href'].startswith(PREFIX):
                href = l.attrs['href']
                params = parse_qs(href[len(PREFIX):])
                cluster_id = params['ncl'][0]
                fetch_queue.append((cluster_id, make_all_coverage_url(cluster_id)))

print('[clusters]\t{} to fetch'.format(len(fetch_queue)))
fetched = not_fetched = 0
while fetch_queue:
    cluster_id, url = fetch_queue.pop(0)
    dirname = os.path.join(CACHE, cluster_id)
    fetch = True
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
        fetch = True

    filename = 'cluster.html'
    path = os.path.join(CACHE, cluster_id, filename)

    if not os.path.exists(path):
        #print('Fetching {} to {}'.format(url, path))
        time.sleep(random.randint(0, 4))
        with open(path, 'w') as f:
            f.write(requests.get(url).text)
        fetched += 1
    else:
        #print('Got {} as {}'.format(url, path))
        not_fetched += 1
    random.shuffle(fetch_queue)
print('[clusters]\tFetched {}, not fetched {}'.format(fetched, not_fetched))

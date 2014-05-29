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

exported = 0
for cluster_id in os.listdir(CACHE):
    listing = os.path.join(CACHE, cluster_id, 'cluster.html')
    if not os.path.exists(listing):
        continue
    with open(listing) as f:
        s = BeautifulSoup(f)
        for a in s.find_all('a'):
            if 'class' in a.attrs and 'article' in a.attrs['class'] and 'href' in a.attrs:
                url = a.attrs['href']
                path = os.path.join(CACHE, cluster_id, hashlib.md5(url.encode('utf8')).hexdigest())
                url_path = path + '.url'
                if not os.path.exists(url_path):
                    with open(url_path, 'w') as g:
                        g.write(url + '\n')
                        exported += 1
                '''
                if not os.path.exists(path):
                    print('Fetching {} to {}'.format(url, path))
                    with open(path, 'w') as g:
                        try:
                            g.write(requests.get(url).text)
                        except Exception:
                            pass # Create empty file...
                else:
                    print('Found {} as {}'.format(url, path))
                '''
print('[export]\texported {}'.format(exported))

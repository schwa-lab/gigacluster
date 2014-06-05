#!/usr/bin/env python3

import argparse
import os
import requests
import multiprocessing
import sys

from gigacluster import CACHE

def build_readability_url(url, token):
    return 'http://www.readability.com/api/content/v1/parser?url={}&token={}'.format(url, token)

def fetch(job):
    url, path = job
    #print('Fetching {} for {}'.format(url, path))
    with open(path, 'w') as g:
        g.write(requests.get(url).text)

p = argparse.ArgumentParser()
p.add_argument('-p', '--processes', default=2, type=int)
args = p.parse_args()

TOKEN = os.environ.get('READABILITY_API_TOKEN')
if TOKEN is None:
    p.error('Please set $READABILITY_API_TOKEN')

queue = []
for root, dirs, files in os.walk(CACHE):
    dirs.sort()
    files = set(files)
    for filename in sorted(f for f in files if f.endswith('.url')):
        readable = filename.replace('.url', '.readability')
        if not readable in files:
            url = build_readability_url(open(os.path.join(root, filename)).read().strip(), token=TOKEN)
            #print('Queueing {}'.format(url))
            path = os.path.join(root, readable)
            queue.append((url, path))
        else:
            #print('Found {}'.format(readable))
            pass

print('[readability]\tFetching {} urls using {} processes'.format(len(queue), args.processes))
if args.processes == 1:
    for i in queue:
        fetch(i)
else:
    pool = multiprocessing.Pool(args.processes)
    pool.map(fetch, queue)
    pool.close()
    pool.join()

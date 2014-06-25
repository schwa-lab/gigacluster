#!/usr/bin/env python3

import argparse
from collections import Counter
import glob
import json
import os

from gigacluster import CACHE

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--detail')
args = parser.parse_args()

clusters = []
readable_clusters = []
incomplete = 0
for cluster_id in os.listdir(CACHE):
    path = os.path.join(CACHE, cluster_id)
    if not os.path.isdir(path):
        continue
    tokens = Counter()
    n_sources = 0
    n_readable = 0
    for filename in os.listdir(path):
        if filename.endswith('.url'):
            n_sources += 1
        elif filename.endswith('.readability'):
            with open(os.path.join(CACHE, cluster_id, filename)) as f:
                try:
                    data = json.load(f)
                except Exception:
                    continue
                if not 'title' in data:
                    continue
                tokens.update(data['title'].lower().split())
                n_readable += 1
    if not n_sources:
        incomplete += 1
    clusters.append(n_sources)
    readable_clusters.append(n_readable)
    if args.detail:
        print('{}\t{}\t{}\t{}'.format(cluster_id, n_sources, n_readable, tokens.most_common(10)))

mean = sum(readable_clusters) / len(readable_clusters)
readable_clusters.sort()
median = clusters[len(readable_clusters) // 2]
for non_zero_min in readable_clusters:
    if non_zero_min != 0:
        break
print('{} clusters, {} docs, {} readable docs, mean {:.1f}, median {:.1f}, min {}, max {}, incomplete {}'.format(
        len(clusters), sum(clusters), sum(readable_clusters), mean, median, non_zero_min, clusters[-1], incomplete))

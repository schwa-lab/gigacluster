#!/usr/bin/env python3

import argparse
import itertools
import os
import sys

from gigacluster import DATA, Doc, dr, SentenceBOWOverlap, SentenceBOWCosine, DocSentenceComparator

METRICS = {
    'SentenceBOWOverlap': SentenceBOWOverlap,
    'SentenceBOWCosine': SentenceBOWCosine,
    'DocSentenceComparator': DocSentenceComparator,
}

parser = argparse.ArgumentParser()
parser.add_argument('cluster', help='Cluster docrep file')
parser.add_argument('-m', '--metric', default='DocSentenceComparator', help='Metric, available={}'.format(METRICS.keys()))
parser.add_argument('-t', '--threshold', type=float, default=0.4)
parser.add_argument('-T', '--sentence-threshold', type=float, default=0.4)
parser.add_argument('-l', '--length', type=int, default=1)
parser.add_argument('-i', '--idf-path', default=os.path.join(DATA, 'idf.txt'))
args = parser.parse_args()

m = METRICS.get(args.metric)
if m is None:
    parser.error('Require valid metric {}'.format(METRICS.keys()))
comparator = m(args.threshold, args.sentence_threshold, idf_path=args.idf_path)

print(comparator, file=sys.stderr)

prefix = os.path.dirname(args.cluster)
with open(args.cluster, 'rb') as f:
    docs = list(dr.Reader(f, Doc))
    for i, j in itertools.combinations(docs, 2):
        for match in comparator([i], [j]):
            print('{}\t{}'.format(prefix, match))
print('Distribution: score={}\tsentence_score{}'.format(*comparator.deciles), file=sys.stderr)
sys.stdout.flush()
sys.stderr.flush()

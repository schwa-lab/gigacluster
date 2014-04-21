#!/usr/bin/env python3

import argparse
import datetime
import sys

from stream import Stream
from window import Window
from comparators import *

METRICS = {
    'SentenceBOWOverlap': SentenceBOWOverlap,
    'SentenceBOWCosine': SentenceBOWCosine,
}

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--primary')
parser.add_argument('-s', '--streams', default=[], action='append')
parser.add_argument('-m', '--metric', default='SentenceBOWOverlap', help='Metric, available={}'.format(METRICS.keys()))
parser.add_argument('-t', '--threshold', type=float, default=0.25)
parser.add_argument('-l', '--length', type=int, default=1)
parser.add_argument('-i', '--idf-path')
parser.add_argument('-e', '--end-date')
args = parser.parse_args()

if args.end_date:
    end_date = datetime.datetime.strptime(args.end_date, '%Y%m%d').date()
else:
    end_date = None

primary = Window(Stream(args.primary))
secondaries = [Window(Stream(i), before=1, after=1) for i in args.streams]

m = METRICS.get(args.metric)
if m is None:
    parser.error('Require valid metric {}'.format(METRICS.keys()))
comparator = m(args.threshold, length=args.length, idf_path=args.idf_path)

print(comparator, file=sys.stderr)

more = primary.seek()
while more:
    for date, docs in primary.dates.items():
        print(primary, '@', date, file=sys.stderr)
        for w in secondaries:
            w.seek(date)
            print(' ', w, file=sys.stderr)
            for match in comparator(docs, w.iter_docs()):
                print('{}\t{}'.format(date, match))
            sys.stdout.flush()
    more = primary.seek()
    if end_date and date == end_date:
        break

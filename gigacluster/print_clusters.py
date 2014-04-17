#!/usr/bin/env python3

import argparse
import sys

from stream import Stream
from window import Window
from comparators import *

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--primary')
parser.add_argument('-s', '--streams', default=[], action='append')
args = parser.parse_args()

primary = Window(Stream(args.primary))
secondaries = [Window(Stream(i), before=1, after=1) for i in args.streams]

comparator = NEOverlap(threshold=0.1)

more = primary.seek()
while more:
    for date, docs in primary.dates.items():
        print(primary, '@', date, file=sys.stderr)
        for w in secondaries:
            w.seek(date)
            for a, b, c in comparator(docs, w.iter_docs()):
                print('{}\t{}\t{}\t{:.3f}\t{}'.format(date, a.id, b.id, c, a.features.intersection(b.features)))
    more = primary.seek()

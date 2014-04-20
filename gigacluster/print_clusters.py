#!/usr/bin/env python3

import argparse
import datetime
import sys

from stream import Stream
from window import Window
from comparators import *

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--primary')
parser.add_argument('-s', '--streams', default=[], action='append')
parser.add_argument('-e', '--end-date')
args = parser.parse_args()

if args.end_date:
    end_date = datetime.datetime.strptime(args.end_date, '%Y%m%d').date()
else:
    end_date = None

primary = Window(Stream(args.primary))
secondaries = [Window(Stream(i), before=1, after=1) for i in args.streams]

#comparator = BOWOverlap(threshold=0.1)
comparator = SentenceBOWOverlap(threshold=0.3, length=6)

more = primary.seek()
while more:
    for date, docs in primary.dates.items():
        print(primary, '@', date, file=sys.stderr)
        for w in secondaries:
            w.seek(date)
            print(' ', w, file=sys.stderr)
            for match in comparator(docs, w.iter_docs()):
                print('{}\t{}'.format(date, match))
    more = primary.seek()
    if end_date and date == end_date:
        break

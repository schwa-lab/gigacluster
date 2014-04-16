#!/usr/bin/env python3

import argparse

from stream import Stream, StreamCollection

parser = argparse.ArgumentParser()
parser.add_argument('primary')
parser.add_argument('streams')
args = parser.parse_args()

print(args)

primary = Stream(args.primary)

for day, docs in primary:
    print(day, len(docs))

#collection = StreamCollection(Stream(args.primary), [Stream(args.streams)])

#for i in collection.iter_window(1):
#    print i

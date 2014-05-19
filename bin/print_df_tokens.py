#!/usr/bin/env python3

from collections import Counter
import sys
from model import dr, Doc

df = Counter()
with open(sys.argv[1], 'rb') as f:
    for doc in dr.Reader(f, Doc):
        df.update({t.raw.replace('\t', ' ').replace('\n', ' ').strip() for t in doc.tokens})
for t, c in df.items():
    print('{}\t{}'.format(t, c))

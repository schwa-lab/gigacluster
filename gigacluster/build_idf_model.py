#!/usr/bin/env python

from collections import Counter
import argparse
import math
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-n', type=int)
args = parser.parse_args()

SMOOTH = 1
def get_idf(n, df=SMOOTH):
    """ Calculates idf, returning a string. """
    return '{:.6f}'.format(math.log(n / df))

# Aggregate separate token dfs.
token_dfs = Counter()
for line in sys.stdin:
    try:
        token, df = line.rstrip().split('\t')
    except ValueError:
        print('Error reading "{}"'.format(line.rstrip('\n')), file=sys.stderr)
        continue
    token_dfs[token] += int(df)

# Calculate idf and bucket.
idfs = {}
seen_smooth_value = False
for token, df in token_dfs.items():
    if df == SMOOTH:
        seen_smooth_value = True
    idfs.setdefault(get_idf(args.n, df), []).append(token)

# Add the smooth value if required, otherwise, this will be the highest idf value.
if not seen_smooth_value:
    idfs[get_idf(args.n, SMOOTH)] = ['']

# Output idfs and their tokens.
for idf, tokens in sorted(idfs.items()):
    print('{}\t{}'.format(idf, '\t'.join(tokens)))

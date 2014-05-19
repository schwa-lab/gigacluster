#!/usr/bin/env python3

from __future__ import division, print_function
from difflib import SequenceMatcher
import sys
import unicode

from gigacluster import SentenceMatch, read_info, is_punctuation, STOPWORDS
import nltk
stem = nltk.stem.PorterStemmer().stem

LENGTH_RATIO = 1.5
INV_LR = 1/LENGTH_RATIO

RED    = '\033[0;31m'
GREEN  = '\033[0;32m'
NORMAL = '\033[0m'

red = lambda i: '{}{}{}'.format(RED, i, NORMAL)
green = lambda i: '{}{}{}'.format(GREEN, i, NORMAL)


def first_norm(s):
    return [tok.lower() for tok in s if not is_punctuation(tok)]

def second_norm(s):
    return [stem(tok)
            for tok in s
            if tok not in STOPWORDS]


matcher = SequenceMatcher(None)
for f in sys.argv[1:]:
    with open(f) as f:
        for line in f:
            window, line = line.decode('utf-8').split('\t', 1)
            m = SentenceMatch.from_string(line)
            if m.sentence_score < 0.4:
                continue
            s, t = read_info(m.info)
            if s == t:
                continue

            s_nopunct = first_norm(s)
            t_nopunct = first_norm(t)

            s_normed = second_norm(s_nopunct)
            t_normed = second_norm(t_nopunct)
            stoks = set(s_normed)
            ttoks = set(t_normed)

            if len(stoks & ttoks) in (len(stoks), len(ttoks)):
                # one is subset of the other
                if ' '.join(s_nopunct) in ' '.join(t_nopunct) or ' '.join(t_nopunct) in ' '.join(s_nopunct):
                    #substring not interesting
                    continue

                # check substantial unnormalised distances
                ratio = len(s) / len(t)
                if ratio > LENGTH_RATIO or ratio < INV_LR:
                    if ratio < 1:
                        ratio = 1/ratio
                    print(ratio, unicode(m).encode('utf-8'), sep='\t')

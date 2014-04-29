#!/usr/bin/env python

from difflib import SequenceMatcher
import sys

from gigacluster import SentenceMatch, read_info, lemma_sequence, iter_blocks, is_punctuation, overlap, NON_MATCH

'''
<metadata>
M\t(overlap=1)\t(matching bit - original text)
N\t(overlap)\t(sentence a, red)\t(sentence b, green)
...

'''

RED    = '\033[0;31m'
GREEN  = '\033[0;32m'
NORMAL = '\033[0m'

red = lambda i: '{}{}{}'.format(RED, i, NORMAL)
green = lambda i: '{}{}{}'.format(GREEN, i, NORMAL)

def get_block_lines(s, t):
    lines = []
    s_tokens = [i for i in s if not is_punctuation(i)]
    t_tokens = [i for i in t if not is_punctuation(i)]
    if len(s_tokens) < 5 and len(t_tokens) < 5:
        return lines
    # Try matching.
    s_lemmas = lemma_sequence(s_tokens)
    t_lemmas = lemma_sequence(t_tokens)
    matcher.set_seqs(s_lemmas, t_lemmas)
    for block_type, s_start, s_stop, t_start, t_stop in iter_blocks(s_lemmas, t_lemmas, matcher.get_matching_blocks()):
        s_slice = s_tokens[s_start:s_stop]
        t_slice = t_tokens[t_start:t_stop]
        _, _, _, _, score = overlap(set(s_lemmas[s_start:s_stop]), set(t_lemmas[t_start:t_stop]))
        s_text = ' '.join(s_slice)
        t_text = ' '.join(t_slice)
        if block_type == NON_MATCH:
            s_text = green(s_text)
            t_text = red(t_text)
            text = '{}\t{}'.format(s_text, t_text)
        else:
            text = s_text
        lines.append('{}\t{:.3f}\t{}'.format(block_type, score, text))
    return lines

matcher = SequenceMatcher(None)
for line in sys.stdin:
    window, line = line.split('\t', 1)
    m = SentenceMatch.from_string(line)
    if m.sentence_score < 0.6:
        continue
    s, t = read_info(m.info)
    if s == t:
        continue
    blocks = get_block_lines(s, t)
    if blocks:
        print(m)
        print('\n'.join(blocks))
        print()

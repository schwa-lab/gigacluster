#!/usr/bin/env python

from difflib import SequenceMatcher
import sys

from gigacluster import SentenceMatch, read_info, lemma_sequence, iter_blocks, is_punctuation, NON_MATCH

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
    s_tokens = [(index, i) for index, i in enumerate(s) if not is_punctuation(i)]
    t_tokens = [(index, i) for index, i in enumerate(t) if not is_punctuation(i)]
    if len(s_tokens) < 5 and len(t_tokens) < 5:
        return lines
    # Try matching.
    s_lemmas = lemma_sequence(i[1] for i in s_tokens)
    t_lemmas = lemma_sequence(i[1] for i in t_tokens)
    matcher.set_seqs(s_lemmas, t_lemmas)
    s_tokens_start = s_tokens_stop = t_tokens_start = t_tokens_stop = 0
    for block_type, s_start, s_stop, t_start, t_stop in iter_blocks(s_lemmas, t_lemmas, matcher.get_matching_blocks()):
        s_slice = s_tokens[s_start:s_stop]
        t_slice = t_tokens[t_start:t_stop]
        s_text = ' '.join(i[1] for i in s_slice)
        t_text = ' '.join(i[1] for i in t_slice)
        if block_type == NON_MATCH:
            s_text = green(s_text)
            t_text = red(t_text)
            text = '{}\t{}'.format(s_text, t_text)
        else:
            text = s_text
        # Calculate real offsets, including punctuation.
        if s_slice:
            s_tokens_start = s_slice[0][0]
            s_tokens_stop = s_slice[-1][0] + 1
        if t_slice:
            t_tokens_start = t_slice[0][0]
            t_tokens_stop = t_slice[-1][0] + 1
        lines.append('{}\t{}\t{}\t{}\t{}\t{}'.format(block_type, s_tokens_start, s_tokens_stop,
                                                     t_tokens_start, t_tokens_stop, text))
        s_tokens_start = s_tokens_stop
        t_tokens_start = t_tokens_stop
    return lines

matcher = SequenceMatcher(None)
for f in sys.argv[1:]:
    with open(f) as f:
        for line in f:
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

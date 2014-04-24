from gigacluster.comparators import *
from gigacluster.model import Doc, Token

def test_overlap():
    assert 1 == overlap(set('abc'), set('bca'))[-1]
    assert 0 == overlap(set('abc'), set('def'))[-1]
    assert 1/3 == overlap(set('ab'), set('bc'))[-1]

def test_unigram_tf():
    d = Doc()
    for i in 'The cat in the mat .'.split():
        d.tokens.append(Token(raw=i))
    tf = unigram_tf(d, slice(0, len(d.tokens) + 1))
    assert {'cat': 1, 'mat': 1} == dict(tf)

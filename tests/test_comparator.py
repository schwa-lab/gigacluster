from difflib import SequenceMatcher
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

def test_iter_blocks():
    expected = [
        (NON_MATCH, 'a', ''),
        (MATCH, 'bc', 'bc'),
        (NON_MATCH, 'd', ''),
    ]
    assert expected == list(_match_blocks('abcd', 'bc'))
    expected = [
        (MATCH, 'a', 'a'),
        (NON_MATCH, '', 'bc'),
        (MATCH, 'a', 'a'),
    ]
    assert expected == list(_match_blocks('aa', 'abca'))
    expected = [
        (NON_MATCH, 'a', ''),
    ]
    assert expected == list(_match_blocks('a', ''))
    expected = [
        (NON_MATCH, 'a', ''),
        (MATCH, 'b', 'b'),
    ]
    assert expected == list(_match_blocks('ab', 'b'))
    expected = [
        (MATCH, 'b', 'b'),
    ]
    assert expected == list(_match_blocks('b', 'b'))

def _match_blocks(a, b):
    print('\nMatching', (a, b))
    for match_type, a_start, a_stop, b_start, b_stop in iter_blocks(a, b, SequenceMatcher(None, a, b).get_matching_blocks()):
        a_str = a[a_start:a_stop]
        b_str = b[b_start:b_stop]
        print((match_type, a_start, a_stop, b_start, b_stop, a_str, b_str))
        yield match_type, a_str, b_str

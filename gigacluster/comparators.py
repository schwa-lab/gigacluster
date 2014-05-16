#!/usr/bin/env python3

from __future__ import print_function, division
from collections import Counter
import itertools
import math
import re
import sys
import six
if six.PY3:
    viewkeys = dict.keys
else:
    viewkeys = dict.viewkeys


from .idf import IDF
from .model import dr, prev_next_sentences
from .stopwords import STOPWORDS

from nltk.stem.porter import PorterStemmer as Stemmer

class Match(object):
    def __init__(self, a, b, score, info):
        self.a = a
        self.b = b
        self.score = score
        self.info = info

    def __str__(self):
        return '{}\t{}\t{:.3f}\t{}'.format(self.a, self.b, self.score, self.info)

class SentenceMatch(Match):
    def __init__(self, a, b, score, sentence_score, intersection, union, card_a, card_b, dot, idf_dot, norm, info=''):
        super(SentenceMatch, self).__init__(a, b, score, info)
        self.sentence_score = sentence_score
        self.intersection = intersection
        self.union = union
        self.card_a = card_a
        self.card_b = card_b
        self.dot = dot
        self.idf_dot = idf_dot
        self.norm = norm

    def __str__(self):
        return u'{}\t{}\t{:.3f}\t{:.3f}\t{}\t{}\t{}\t{}\t{:.3f}\t{:.3f}\t{:.3f}\t{}'.format(
            self.a, self.b, self.score, self.sentence_score,
            self.intersection, self.union, self.card_a, self.card_b,
            self.dot, self.idf_dot, self.norm, self.info)

    @classmethod
    def from_string(self, s):
        a, b, score, sentence_score, intersection, union, card_a, card_b, dot, idf_dot, norm, info = s.rstrip('\n').split('\t', 11)
        return self(a, b, float(score), float(sentence_score), int(intersection), int(union), int(card_a), int(card_b), float(dot), float(idf_dot), float(norm), info)

def read_info(info):
    return tuple(s.split() for s in info.split('\t'))

STEMMER = Stemmer()
def lemma_sequence(token_norms):
    return [STEMMER.stem(i.lower()) for i in token_norms]

NON_MATCH = 'N'
MATCH = 'M'
def iter_blocks(s, t, blocks):
    i = j = 0
    for block in blocks:
        if block.size == 0:
            continue
        if block.a > i or block.b > j:
            yield NON_MATCH, i, block.a, j, block.b
        yield MATCH, block.a, block.a + block.size, block.b, block.b + block.size
        i = block.a + block.size
        j = block.b + block.size
    if i != len(s) or j != len(t):
        yield NON_MATCH, i, len(s), j, len(t)

def overlap(a, b):
    i = len(a.intersection(b))
    u = len(a.union(b))
    if u:
        return i, u, len(a), len(b), i / u
    else:
        return i, u, len(a), len(b), 0

def cosine_similarity(a, b):
    """
    Compute the cosine similarity of two vectors, represented as dicts.
    Equation described here: http://www.miislita.com/information-retrieval-tutorial/cosine-similarity-tutorial.html#Cosim
    """
    if not a or not b:
        return 0.0
    return sum(a[t] * b[t] for t in set(a).intersection(b)) / (norm(a) * norm(b))

def norm(a):
    """ The Euclidean norm. """
    return math.sqrt(float(sum(v * v for v in a.values())))

EXP = re.compile('(_|[^\w\s])+', re.UNICODE)
def is_punctuation(t):
    return EXP.match(t)

@dr.requires_decoration(prev_next_sentences)
def sentence_id(doc, sentence):
    return '{}/{}'.format(doc.id, sentence.index)

def sentence_text(doc, sentence):
    return ' '.join(t.text for t in doc.tokens[sentence.span]).replace('\t', ' ')

def iter_long(sentences, length):
    for s in sentences:
        if s.span.stop - s.span.start > length:
            yield s

def unigram_tf(doc, span):
    return Counter(t.text for t in doc.tokens[span] 
            if not is_punctuation(t.text) and not t.text.lower() in STOPWORDS)

def sq_tfidf_unigrams(doc, idf):
    return {t: math.sqrt(tf) * idf.get(t) for t, tf in unigram_tf(doc, slice(0, len(doc.tokens) + 1)).items()}

def prime_sentence_features(doc):
    if not hasattr(doc, 'sentence_features'):
        doc.sentence_features = {s: unigram_tf(doc, s.span) for s in doc.sentences}

# Comparators
class Comparator(object):
    def __init__(self, threshold):
        self.threshold = threshold
        self.stats = Counter()

    def __call__(self, docs_a, docs_b):
        comparisons = 0
        for i in docs_a:
            self.prime_features(i)
        for i in docs_b:
            self.prime_features(i)
        req_comparisons = len(docs_a) * len(docs_b)
        step = req_comparisons // 10
        print('{} comparisons'.format(req_comparisons), file=sys.stderr, end='')
        for a, b in itertools.product(docs_a, docs_b):
            if comparisons % step == 0:
                print(' ...{}'.format(comparisons), file=sys.stderr, end='')
            comparisons += 1
            for m in self._handle(a, b):
                yield m
        print('', file=sys.stderr)

    def _handle(self, a, b):
        raise NotImplementedError

def score_sentence_pair(a_id, b_id, doc_score, a_features, b_features, idf, threshold=0.):
    card_intersection, card_union, card_a, card_b, sentence_score = overlap(set(a_features.keys()), set(b_features.keys()))
    if not sentence_score or sentence_score < threshold:
        return
    dot_dict = {k: a_features[k] * b_features[k]
                for k in viewkeys(a_features) & viewkeys(b_features)}
    return SentenceMatch(a_id, b_id, score=doc_score,
                         sentence_score=sentence_score,
                         intersection=card_intersection, union=card_union,
                         card_a=card_a, card_b=card_b,
                         dot=sum(dot_dict.values()),
                         idf_dot=sum(v * idf.get(k) for k, v in dot_dict.items()),
                         norm=norm(a_features) * norm(b_features),
                         )

class DocSentenceComparator(Comparator):
    def __init__(self, threshold, sentence_threshold, idf_path):
        super(DocSentenceComparator, self).__init__(threshold)
        self.idf = IDF(idf_path)
        self.sentence_threshold = sentence_threshold
        self.sentence_stats = Counter()
    
    def __str__(self):
        return '<{} t={} st={} idf={}>'.format(self.__class__.__name__, self.threshold, self.sentence_threshold, self.idf)

    def _handle(self, a, b):
        matches = []
        # Check for document similarity.
        score = cosine_similarity(a.features, b.features)
        self.stats['{:.3f}'.format(score)] += 1
        if score > self.threshold:
            #features = [(a.features[k] + b.features[k] / 2, k) for k in set(a.features.keys()).intersection(set(b.features.keys()))]
            #features.sort(reverse=True)

            # Check for sentence similarity.
            for i, j in itertools.product(a.sentences, b.sentences):
                if not (i in a.sentence_features and j in b.sentence_features):
                    continue
                a_f = a.sentence_features[i]
                b_f = b.sentence_features[j]
                match = score_sentence_pair(sentence_id(a, i), sentence_id(b, j), score,
                                            a_f, b_f,
                                            self.idf, self.sentence_threshold)
                if match is not None:
                    match.info = '{}\t{}'.format(sentence_text(a, i),
                                                 sentence_text(b, j))
                    self.sentence_stats['{:.3f}'.format(match.sentence_score)] += 1
                    matches.append(match)
        return matches

    def prime_features(self, doc):
        if not hasattr(doc, 'features'):
            doc.features = sq_tfidf_unigrams(doc, self.idf)
            prime_sentence_features(doc)

    @property
    def deciles(self):
        return self._get_decile(self.stats), self._get_decile(self.sentence_stats)

    def _get_decile(self, stats):
        samples = list(self._iter_samples(stats))
        dec = len(samples) // 10
        return samples[-dec:-dec + 1]
        
    def _iter_samples(self, stats):
        for i, count in sorted(stats.items()):
            for j in range(count):
                yield i

class SentenceBOWOverlap(Comparator):
    def __init__(self, threshold, length, idf_path=None):
        super(SentenceBOWOverlap, self).__init__(threshold)
        self.length = length
        if idf_path:
            self.idf = IDF(idf_path)
        else:
            self.idf = None

    def __str__(self):
        return '<{} t={} l={} idf={}>'.format(self.__class__.__name__, self.threshold, self.length, self.idf)

    def _handle(self, a, b):

        
        matches = []
        for s, t in itertools.product(iter_long(a.sentences, self.length), iter_long(b.sentences, self.length)):
            if s in a.sentence_features and t in b.sentence_features:
                score = self._score(a.sentence_features[s], b.sentence_features[t])
                if score > self.threshold:
                    matches.append(Match(sentence_id(a, s), sentence_id(b, t), score, 
                                    '{}\t{}'.format(sentence_text(a, s), sentence_text(b, t))))
        return matches

    def prime_features(self, doc):
        prime_sentence_features(doc) 

    def _score(self, a_f, b_f):
        card_intersection, card_union, card_a, card_b, sentence_score = overlap(a_f, b_f)
        if self.idf:
            sentence_score *= sum(self.idf.get(t) for t in a_f.intersection(b_f))
        return sentence_score

class SentenceBOWCosine(SentenceBOWOverlap):
    def _score(self, a_features, b_features):
        return cosine_similarity(a_features, b_features)

    def _get_features(self, doc, sentence):
        return {i: self.idf.get(i) for i in {t.raw for t in doc.tokens[sentence.span]} 
                                    if not is_punctuation(i) and not i.lower() in STOPWORDS}

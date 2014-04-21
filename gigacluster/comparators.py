#!/usr/bin/env python3

import math
import re
import string
from stopwords import STOPWORDS

from idf import IDF
from model import dr, prev_next_sentences

class Match(object):
    def __init__(self, a, b, score, info):
        self.a = a
        self.b = b
        self.score = score
        self.info = info

    def __str__(self):
        return '{}\t{}\t{:.3f}\t{}'.format(self.a, self.b, self.score, self.info)

def overlap(a, b):
    u = len(a.union(b))
    if u:
        return len(a.intersection(b)) / u
    else:
        return 0

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

class Comparator(object):
    def __init__(self, threshold):
        self.threshold = threshold

    def __call__(self, docs_a, docs_b):
        for i, a in enumerate(docs_a):
            self.prime_features(a)
            for j, b in enumerate(docs_b):
                if i == j:
                    break # Do not compare a,b; b,a.
                self.prime_features(b)
                matches = self._handle(a, b)
                for m in matches:
                    yield m

    def _handle(self, a, b):
        raise NotImplementedError

class OverlapComparator(Comparator):
    def _handle(self, a, b):
        score = overlap(a.features, b.features)
        if score > self.threshold:
            return [Match(a.id, b.id, score, a.features.intersection(b.features))]
        else:
            return []

EXP = re.compile('[{}]+'.format(string.punctuation))
def is_punctuation(t):
    return EXP.match(t)

@dr.requires_decoration(prev_next_sentences)
def sentence_id(doc, sentence):
    return '{}/{}'.format(doc.id, sentence.index)

def sentence_text(doc, sentence):
    return ' '.join(t.raw for t in doc.tokens[sentence.span]).replace('\t', ' ')

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
        for i, s in enumerate(a.sentences):
            if s.span.stop - s.span.start < self.length:
                continue
            for j, t in enumerate(b.sentences):
                if i < j:
                    continue
                if t.span.stop - t.span.start < self.length:
                    continue
                if s in a.features and t in b.features:
                    score = self._score(a.features[s], b.features[t])
                    if score > self.threshold:
                        matches.append(Match(sentence_id(a, s), sentence_id(b, t), score, 
                                        '{}\t{}'.format(sentence_text(a, s), sentence_text(b, t))))
        return matches

    def prime_features(self, doc):
        if not hasattr(doc, 'features'):
            doc.features = {}
            for s in doc.sentences:
                if s.span.stop - s.span.start < self.length:
                    continue
                doc.features[s] = self._get_features(doc, s)
        
    def _get_features(self, doc, sentence):
        return {i for i in {t.raw for t in doc.tokens[sentence.span]} if not is_punctuation(i) and not i.lower() in STOPWORDS}

    def _score(self, a_features, b_features):
        s = overlap(a_features, b_features)
        if self.idf:
            s *= sum(self.idf.get(t) for t in a_features.intersection(b_features))
        return s

class SentenceBOWCosine(SentenceBOWOverlap):
    def _score(self, a_features, b_features):
        return cosine_similarity(a_features, b_features)

    def _get_features(self, doc, sentence):
        return {i: self.idf.get(i) for i in {t.raw for t in doc.tokens[sentence.span]} 
                                    if not is_punctuation(i) and not i.lower() in STOPWORDS}

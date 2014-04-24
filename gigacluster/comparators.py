#!/usr/bin/env python3

from collections import Counter
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
        return '{}\t{}\t{:.3f}\t{:.3f}\t{}\t{}\t{}\t{}\t{:.3f}\t{:.3f}\t{:.3f}\t{}'.format(
            self.a, self.b, self.score, self.sentence_score, 
            self.intersection, self.union, self.card_a, self.card_b,
            self.dot, self.idf_dot, self.norm, self.info)

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

EXP = re.compile('[{}]+'.format(string.punctuation))
def is_punctuation(t):
    return EXP.match(t)

@dr.requires_decoration(prev_next_sentences)
def sentence_id(doc, sentence):
    return '{}/{}'.format(doc.id, sentence.index)

def sentence_text(doc, sentence):
    return ' '.join(t.raw for t in doc.tokens[sentence.span]).replace('\t', ' ')

def iter_pairs(a_items, b_items, hook):
    for i, a in enumerate(a_items):
        hook(a)
        for j, b in enumerate(b_items):
            if i == j:
                break # Do not compare a,b; b,a.
            hook(b)
            yield a, b
        
def iter_long(sentences, length):
    for s in sentences:
        if s.span.stop - s.span.start > length:
            yield s

def unigram_tf(doc, span):
    return Counter(t.raw for t in doc.tokens[span] 
            if not is_punctuation(t.raw) and not t.raw.lower() in STOPWORDS)

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
        for a, b in iter_pairs(docs_a, docs_b, self.prime_features):
            for m in self._handle(a, b):
                yield m

    def _handle(self, a, b):
        raise NotImplementedError

class DocSentenceComparator(Comparator):
    def __init__(self, threshold, sentence_threshold, idf_path):
        super(DocSentenceComparator, self).__init__(threshold)
        self.idf = IDF(idf_path)
    
    def __str__(self):
        return '<{} t={} idf={}>'.format(self.__class__.__name__, self.threshold, self.idf)

    def _handle(self, a, b):
        matches = []
        # Check for document similarity.
        score = cosine_similarity(a.features, b.features)
        self.stats['{:.3f}'.format(score)] += 1
        if score > self.threshold:
            #features = [(a.features[k] + b.features[k] / 2, k) for k in set(a.features.keys()).intersection(set(b.features.keys()))]
            #features.sort(reverse=True)

            # Check for sentence similarity.
            # Perhaps some extra calls, but we don't know until this point whether we'll need to prime.
            prime_sentence_features(a)
            prime_sentence_features(b)
            for i, j in iter_pairs(a.sentences, b.sentences, lambda i: i):
                if not (i in a.sentence_features and j in b.sentence_features):
                    continue
                a_f = a.sentence_features[i]
                b_f = b.sentence_features[j]
                card_intersection, card_union, card_a, card_b, sentence_score = overlap(set(a_f.keys()), set(b_f.keys()))
                dot_dict = {k: a_f[k] * b_f[k] for k in set(a_f.keys()).intersection(set(b_f.keys()))}
                matches.append(SentenceMatch(sentence_id(a, i), sentence_id(b, j), 
                                score=score, 
                                sentence_score=sentence_score,
                                intersection=card_intersection,
                                union=card_union,
                                card_a=card_a,
                                card_b=card_b,
                                dot=sum(dot_dict.values()),
                                idf_dot=sum(v * self.idf.get(k) for k, v in dot_dict.items()),
                                norm=norm(a_f) * norm(b_f),
                                info='{}\t{}'.format(sentence_text(a, i), 
                                                    sentence_text(b, j))))
        matches.sort(key=lambda m: m.sentence_score, reverse=True)
        return matches[:5]

    def prime_features(self, doc):
        if not hasattr(doc, 'features'):
            doc.features = sq_tfidf_unigrams(doc, self.idf)

    @property
    def decile_quartile(self):
        samples = list(self.iter_samples(self.stats))
        dec = len(samples) // 10
        quart = len(samples) // 4
        return samples[-dec:-dec + 1], samples[-quart:-quart + 1]
        
    def iter_samples(self, stats):
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
        for s, t in iter_pairs(iter_long(a.sentences, self.length), iter_long(b.sentences, self.length), lambda i: i):
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
            sentence_score *= sum(self.idf.get(t) for t in a_features.intersection(b_features))
        return sentence_score

class SentenceBOWCosine(SentenceBOWOverlap):
    def _score(self, a_features, b_features):
        return cosine_similarity(a_features, b_features)

    def _get_features(self, doc, sentence):
        return {i: self.idf.get(i) for i in {t.raw for t in doc.tokens[sentence.span]} 
                                    if not is_punctuation(i) and not i.lower() in STOPWORDS}

#!/usr/bin/env python3

import re
import string
from stopwords import STOPWORDS

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

class BOWOverlap(OverlapComparator):
    def prime_features(self, doc):
        if not hasattr(doc, 'features'):
            setattr(doc, 'features', set(i for i in set(t.raw.lower() for t in doc.tokens) if not i in STOPWORDS))

class NEOverlap(OverlapComparator):
    def prime_features(self, doc):
        if not hasattr(doc, 'features'):
            doc.features = set()
            # Get uppers from other parts of the sentence.
            self.uppers = set()
            for s in doc.sentences:
                for t in doc.tokens[s.span][1:]:
                    if t.raw[0].isupper():
                        self.uppers.add(t.raw)
            for sentence in doc.sentences:
                mentions = list(self.iter_sentence_mentions(doc, sentence))
                if mentions:
                    self.add_features(doc, sentence, mentions)

    def iter_sentence_mentions(self, doc, sentence):
        m = []
        for i, t in enumerate(doc.tokens[sentence.span]):
            is_mention = self.is_mention(t.raw)
            if i == 0 and is_mention and t.raw in self.uppers:
                m.append(t.raw)
            elif i > 0 and is_mention:
                m.append(t.raw)
            elif t.raw == "'s" and m:
                m.append(t.raw)
            elif m:
                yield ' '.join(m)
                m = []
        if m:
            yield ' '.join(m)

    def is_mention(self, text):
        # FIXME No acronyms.
        if text[0].isupper() and text[1:].islower() and not text.lower() in STOPWORDS:
            return True
        else:
            return False

    def add_features(self, doc, sentence, mentions):
        doc.features.update(set(mentions))

EXP = re.compile('[{}]+'.format(string.punctuation))
def is_punctuation(t):
    return EXP.match(t)

@dr.requires_decoration(prev_next_sentences)
def sentence_id(doc, sentence):
    return '{}/{}'.format(doc.id, sentence.index)

def sentence_text(doc, sentence):
    return ' '.join(t.raw for t in doc.tokens[sentence.span]).replace('\t', ' ')

class SentenceBOWOverlap(Comparator):
    def __init__(self, threshold, length):
        super(SentenceBOWOverlap, self).__init__(threshold)
        self.length = length

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
                score = overlap(a.features[s], b.features[t])
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
                doc.features[s] = {i for i in {t.raw.lower() for t in doc.tokens[s.span]} 
                                    if not is_punctuation(i)}

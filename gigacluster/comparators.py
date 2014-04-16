#!/usr/bin/env python3

from stopwords import STOPWORDS

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
                c = self._handle(a, b)
                '''
                print(c, [t.raw for t in a.tokens[:20]],
                         [t.raw for t in b.tokens[:20]])
                '''
                if c > self.threshold:
                    yield a, b, c

    def _handle(self, a, b):
        raise NotImplementedError

class OverlapComparator(Comparator):
    def _handle(self, a, b):
        u = len(a.features.union(b.features))
        if u:
            return len(a.features.intersection(b.features)) / u
        else:
            return 0

class ExhaustiveOverlap(OverlapComparator):
    def prime_features(self, doc):
        if not hasattr(doc, 'features'):
            setattr(doc, 'features', set(i for i in set(str(t).lower() for t in doc.tokens) if not i in STOPWORDS))

class NEOverlap(OverlapComparator):
    def prime_features(self, doc):
        if not hasattr(doc, 'features'):
            doc.features = set()
            for s in doc.sentences:
                m = []
                for t in doc.tokens[s.span]:
                    if self.is_mention(t.raw):
                        m.append(t.raw)
                    elif m:
                        doc.features.add(' '.join(m))
                        m = []
                if m:
                    doc.features.add(' '.join(m))

    def is_mention(self, text):
        # FIXME No acronyms.
        if text[0].isupper() and text[1:].islower() and not text.lower() in STOPWORDS:
            return True
        else:
            return False

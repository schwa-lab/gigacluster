#!/usr/bin/env python

class IDF(object):
    def __init__(self, path):
        self.path = path
        self.values = {}
        largest = 0
        with open(path) as f:
            for l in f:
                l = l.rstrip('\n').split('\t')
                idf = float(l[0])
                largest = max(largest, idf)
                for i in l[1:]:
                    self.values[i] = idf
        self.largest = largest
    
    def get(self, token):
        return self.values.get(token, self.largest)

#!/usr/bin/env python

import itertools
import os
from model import dr, Doc

class Stream(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        """ Yields tuples of (day, docs).
        Checks that day increases monotonically.
        """
        for fname in sorted(os.listdir(self.dirname)):
            with open(os.path.join(self.dirname, fname), 'rb') as f:
                print(f)
                for date, docs in itertools.groupby(dr.Reader(f, Doc), lambda d: d.date_str):
                    yield date, list(docs)
                    # TODO: date check.

class StreamCollection(object):
    def __init__(self, primary, streams):
        assert not primary in streams
        self.primary = primary
        self.streams = streams

    def iter_window(self, window):
        """ Iterates through the primary stream, yielding documents from it and other streams within the window. """
        raise NotImplementedError

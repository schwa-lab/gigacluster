#!/usr/bin/env python3

import datetime
import itertools
import os
from model import dr, Doc

class StreamError(Exception): pass

class Stream(object):
    """ A directory containing docrep files. Documents should be yieldable in temporal order.
    * Filenames should be sortable for temporal order.
    * Document order within files should be temporal.
    """
    def __init__(self, dirname, filename_exp=None):
        self.dirname = dirname
        self.filename_exp = filename_exp

    def __str__(self):
        return self.dirname

    def __iter__(self):
        """ Yields tuples of (day, docs).
        Checks that day increases monotonically.
        """
        last_date = None
        for fname in sorted(os.listdir(self.dirname)):
            if not fname.endswith('.dr'):
                continue
            if self.filename_exp and not self.filename_exp.match(fname):
                continue
            with open(os.path.join(self.dirname, fname), 'rb') as f:
                for date, docs in itertools.groupby(dr.Reader(f, Doc), lambda d: d.date_str):
                    if last_date and date < last_date:
                        raise StreamError('Dates should increase in streams: current date {}, seen {}'.format(date, last_date))
                    yield self.parse_date(date), list(docs)
                    last_date = date

    def parse_date(self, date):
        return datetime.datetime.strptime(date, '%Y%m%d').date()

#!/usr/bin/env python3

import datetime

DAY = datetime.timedelta(days=1)

class Window(object):
    """ A sliding window forwards in temporal order over a stream of documents.
    * Documents from a date are cached.
    """
    def __init__(self, stream, before=0, after=0):
        assert all(isinstance(i, int) and i >= 0 for i in (before, after)), \
                'Invalid before/after pair: {}/{} ({}/{})'.format(before, after, type(before), type(after))
        self.stream = stream
        self.stream_gen = iter(self.stream)
        self.extra = None

        self.before = before
        self.after = after

        self.date = None
        self.dates = {}

    def __str__(self):
        return '<Window on={} before={} after={}>'.format(self.stream, self.before, self.after)

    def seek(self, date=None):
        """ Advances through the stream so that the window is centered on date
        and can yield results for before/after.
        If date is not specified, seek to the next date (or first if no data has been consumed).
        Returns False if the stream is exhausted.
        """
        start, end = self._calculate_date_bounds(date)
        #print('\tExamining stream {} [{}...{}...{}]'.format(self.stream, start, date, end))
        if start and end:
            self._fill(start, end)
            return True
        else:
            self._drop()
            return False

    def _calculate_date_bounds(self, date):
        start = end = date
        # Start of stream and no date specified: find the first date and work forward.
        if self.date is None and date is None:
            assert not self.dates
            d, docs = self._next_item()
            if d:
                self._push_front((d, docs))
                start = date = d
                for i in range(self.before):
                    date += DAY
                end = date
                for i in range(self.after):
                    end += DAY
        # No date specified: find the next date from the stream.
        elif date is None:
            d, docs = self._next_item()
            if d:
                self._push_front((d, docs))
                start = date = d
                for i in range(self.before):
                    start -= DAY
                end = date
                for i in range(self.after):
                    end += DAY
        # Date specified.
        else:
            start = end = date
            for i in range(self.before):
                start -= DAY
            for i in range(self.after):
                end += DAY
        self.date = date
        return start, end

    def _fill(self, start, end):
        """ Fills buckets from the stream between start and end. """
        self._drop(start)
        # Fill from steam.
        while True:
            d, docs = self._next_item()
            if not d:
                break
            if d < start:
                continue
            elif start <= d <= end:
                #print('\tloading', d)
                self.dates[d] = docs
            else: # ie: d > end
                self._push_front((d, docs)) # Save for later.
                break

    def _drop(self, start=None):
        """ Drop unused buckets. """
        for d in list(self.dates.keys()):
            if start is None or d < start:
                del self.dates[d]

    def _next_item(self):
        """ Return the next item. """
        if self.extra:
            d, docs = self.extra
            self.extra = None
        else:
            try:
                d, docs = next(self.stream_gen)
            except StopIteration:
                d, docs = None, []
        return d, docs

    def _push_front(self, item):
        """ Push item back onto the queue. """
        self.extra = item

    def iter_docs(self):
        """ Yields documents from the current window position. """
        for docs in self.dates.values():
            for d in docs:
                yield d


import datetime
from gigacluster.window import Window

STREAM = [
    (datetime.date(2014, 1, 1), ['20140101.a', '20140101.b']),
    (datetime.date(2014, 1, 2), ['20140102.a', '20140102.b']),
]

def test_window():
    w = Window(STREAM)
    w.seek()
    assert STREAM[0][1] == list(w.iter_docs())
    print(list(w.iter_docs()))
    w.seek()
    assert STREAM[1][1] == list(w.iter_docs())
    print(list(w.iter_docs()))

def test_window_gap():
    w = Window(STREAM, before=1)
    w.seek()
    print(list(w.iter_docs()))
    assert sorted(STREAM[0][1] + STREAM[1][1]) == sorted(w.iter_docs())
    assert not w.seek()

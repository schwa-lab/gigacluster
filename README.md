Gigacluster
===========

Clustering gigaword streams.

Installation
============

Mavericks
---------

```bash
brew install libschwa
virtualenv -p python3.4 ve
source ve/bin/activate
pip install libschwa-python
```

Schwalab servers
----------------

```bash
CC=gcc CXX=g++ ve/bin/python3.4 -m pip install -e ../libschwa-python
```

Use
===

Converting gigaword to docrep - 5h, 20m across 8 processors:
```bash
time find ~/schwa/corpora/raw/gigaword-en5/data/ -type f | sort | \
  parallel -j 8 ./gigacluster/xml_to_dr.py --output-dir /data1/gigacluster/dr {}
```

Reorganising into data directories (manually):
```
data/
├── afp
│   └── afp_eng_201001.dr
├── apw
│   └── apw_eng_201001.dr
├── cna
│   └── cna_eng_201001.dr
├── nyt
│   └── nyt_eng_201001.dr
├── wpb
│   └── wpb_eng_201001.dr
└── xin
    └── xin_eng_201001.dr
```

Clustering a month across all streams in 11m:
```bash
time ./gigacluster/print_clusters.py -p data/nyt/ -s data/apw/ \
  -s data/afp/ -s data/cna/ \
  -s data/wpb/ -s data/xin/ > clusters.txt
```

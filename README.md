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
~repos/virtualenv/virtualenv.py -p python3.4 ve
source ve/bin/activate
easy_install-3.4 /path/to/pip-1.2.1.tar.gz
pip install -e ~/repos/nltk
CC=gcc CXX=g++ ve/bin/python3.4 -m pip install libschwa-python
pip install -e .
```

Configuration
=============

Setting a Readability API key
-----------------------------

Change `ve/bin/activate` to include a line like:
```
export READABILITY_API_TOKEN=<hash>
```

Change symlinks
---------------

Change `data` and `cache` to point somewhere you wish to store the data.

Change cronjob dir
------------------

Change the following in `bin/gn_cron.sh` to where you checked out the code.
```
cd /data1/gigacluster/gigacluster
```

Data Preparation
================

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

Building an IDF model:
```bash
find data/ -iname '*dr' | parallel ./gigacluster/print_df_tokens.py {} ">" {.}.df
cat data/*/*dr | dr-count > data/n
cat data/*/*df | ./gigacluster/build_idf_model.py -n $(cat data/n) > data/idf.txt
```

Clustering
==========

Clustering a month across all streams:
```bash
time ./gigacluster/print_clusters.py \
  -t 0.4 -m SentenceBOWOverlap -l 10 \
  -p data/nyt/ -s data/apw/ \
  -s data/afp/ -s data/cna/ \
  -s data/wpb/ -s data/xin/
```

This takes sentences:
* without stopwords
* with more than 10 tokens
* which overlap at more than 0.4

There are also options to weight by IDF.

Doc Sentence clustering
=======================

Generating the jobs
```bash
for i in afp apw cna wpb nyt xin; do for y in `seq 1994 2010`; do echo $i $y; done; done > jobs.txt
```

Running via `parallel`
```bash
cat jobs.txt | parallel -j 
parallel -j 10 ./cluster_year.sh /data1/gigacluster/clustering-0.4-0.4/ {}
```







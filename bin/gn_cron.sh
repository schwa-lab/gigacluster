#!/bin/bash
echo "[gigacluster] indexing on $(hostname)"
date
umask 0002
cd /data1/gigacluster/gigacluster
source ve/bin/activate
./bin/fetch_gn_clusters.py
./bin/fetch_gn_cluster_urls.py
./bin/clean_gn_clusters.py
./bin/gn_stats.py
echo "[used] $(du -Lsh cache)"
echo "[df] $(df -h . | tail -n1)"

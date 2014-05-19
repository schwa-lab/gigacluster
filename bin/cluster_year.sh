#!/bin/bash
set -x
set -e
DIR=$1
IFS=', ' read -a array <<< $2
PRIMARY=${array[0]}
YEAR=${array[1]}
DOC_T=0.4
SEN_T=0.4
PREFIX=$DIR/$YEAR.p$PRIMARY.t$DOC_T.T$SEN_T
#echo $PREFIX
#echo $PRIMARY
#echo $YEAR
./bin/print_clusters.py -p data/$PRIMARY \
    -s data/apw/ -s data/afp/ -s data/cna/ \
    -s data/wpb/ -s data/xin/ -s data/nyt/ \
    -i data/idf.txt \
    -m DocSentenceComparator \
    -t $DOC_T \
    -T $SEN_T \
    -S ".*$YEAR.*" > $PREFIX.clusters.txt 2> $PREFIX.log

#!/usr/bin/env python3
from collections import defaultdict
import hashlib
import json
import os
import sys
from gigacluster import Doc, dr, Tokenizer

tok = Tokenizer()
stats = defaultdict(int)
for root, dirs, files in os.walk(sys.argv[1]):
    dirs.sort()
    files = set(files)
    cluster_dr = os.path.join(root, 'cluster.dr')
    with open(cluster_dr, 'wb') as f_dr:
        writer = dr.Writer(f_dr, Doc)
        written = 0
        for filename in sorted(f for f in files if f.endswith('.readability')):
            path = os.path.join(root, filename)
            with open(path) as f:
                try:
                    data = json.load(f)
                except Exception:
                    stats['bad json'] += 1
                    pass
                else:
                    if not ('url' in data and 'title' in data and 'content' in data):
                        stats['no url/title/content'] += 1
                        continue
                    id = hashlib.md5(data['url'].encode('utf8')).hexdigest()
                    title = data.get('title', '')
                    text = data.get('content', '')
                    doc = Doc(id=id)
                    title = title.encode('utf8')
                    tok.tokenize(title, doc, 0, is_headline=True)
                    tok.tokenize(text.encode('utf8'), doc, len(title) + 1, is_headline=False)
                    writer.write(doc)
                    stats['ok'] += 1
                    written += 1
    if not written:
        print('No docs written for {}'.format(cluster_dr))
        os.remove(cluster_dr)
print('Stats\t{}'.format(dict(stats)))

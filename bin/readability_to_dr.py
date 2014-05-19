#!/usr/bin/env python

import hashlib
import json
import os
import sys

from model import Doc, dr
from tokenizer import Tokenizer

tok = Tokenizer()
for root, dirs, files in os.walk(sys.argv[1]):
    dirs.sort()
    files = set(files)
    cluster_dr = os.path.join(root, 'cluster.dr')
    with open(cluster_dr, 'wb') as f_dr:
        writer = dr.Writer(f_dr, Doc)
        for filename in sorted(f for f in files if f.endswith('.readability')):
            dr_filename = filename.replace('.readability', '.dr')
            if not dr_filename in files:
                path = os.path.join(root, filename)
                with open(path) as f:
                    try:
                        data = json.load(f)
                    except Exception:
                        pass
                    else:
                        if not ('url' in data and 'title' in data and 'content' in data):
                            continue
                        id = hashlib.md5(data['url'].encode('utf8')).hexdigest()
                        title = data.get('title', '')
                        text = data.get('content', '')
                        doc = Doc(id=id)
                        title = title.encode('utf8')
                        tok.tokenize(title, doc, 0, is_headline=True)
                        tok.tokenize(text.encode('utf8'), doc, len(title) + 1, is_headline=False)
                        print(doc)
                        writer.write(doc)

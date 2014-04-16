#!/usr/bin/env python3

import os
import sys
from model import dr, Doc, parse_doc_id, doc_id_to_basename

def dr_to_string(doc):
    lines = [20*'#' + doc.id + 20*'#']
    lines.append(' '.join(t.raw for t in doc.tokens[doc.headline.span]))
    lines.append(' '.join(t.raw for t in doc.tokens[doc.dateline.span]))
    for s in doc.sentences:
        lines.append(' '.join(t.raw for t in doc.tokens[s.span]))
    return '\n'.join(lines) + '\n\n'

base = sys.argv[1]
paths = {}
for doc_id in sys.argv[2:]:
    source, lang, date, sequence = parse_doc_id(doc_id)
    path = os.path.join(base, source.lower(), doc_id_to_basename(doc_id) + '.dr')
    #print(doc_id, '->', path)
    paths.setdefault(path, set()).add(doc_id)

for path, doc_ids in sorted(paths.items()):
    with open(path, 'rb') as f:
        for doc in dr.Reader(f, Doc):
            # FIXME Lame!
            doc_id = doc.id.lstrip("b'").rstrip("'")
            if doc_id in doc_ids:
                print(dr_to_string(doc))
                doc_ids.remove(doc_id)
                if not doc_ids:
                    break

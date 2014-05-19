#!/usr/bin/env python3
from schwa import tokenizer

class Tokenizer:
    def __init__(self):
        self.tokenizer = tokenizer.Tokenizer()

    def tokenize(self, text, doc, start_offset, is_headline=False, is_dateline=False):
        for para in self.tokenizer.tokenize(text, dest=list):
            nsents_before = len(doc.sentences)
            for sent in para:
                ntokens_before = len(doc.tokens)
                for offset, encoded, norm in sent:
                    raw = encoded.decode("utf-8")
                    norm = norm.decode("utf-8") if norm else None
                    start = start_offset + offset
                    span = slice(start, start + len(encoded))
                    doc.tokens.create(span=span, raw=raw, norm=norm)
                ntokens_after = len(doc.tokens)
                sentence = doc.sentences.create(span=slice(ntokens_before, ntokens_after))
                if is_headline:
                    doc.headline = sentence
                elif is_dateline:
                    doc.dateline = sentence

            nsents_after = len(doc.sentences)
            if not is_headline and not is_dateline:
                doc.paras.create(span=slice(nsents_before, nsents_after))

#!/usr/bin/env python3
import logging
import os
import re

from model import Doc, dr
from schwa import tokenizer

DOCREP_EXT = ".dr"

DOC = re.compile(br"<DOC([^>]*)>(\n)*(.*?)</DOC>", re.MULTILINE | re.DOTALL)
HEADLINE = re.compile(br"<HEADLINE>(\n)*(.*?)</HEADLINE>", re.MULTILINE | re.DOTALL)
DATELINE = re.compile(br"<DATELINE>(\n)*(.*?)</DATELINE>", re.MULTILINE | re.DOTALL)
TEXT = re.compile(br"<TEXT>(\n)*(.*?)</TEXT>", re.MULTILINE | re.DOTALL)
ID = re.compile(br'id="([^"]+)"')
TYPE = re.compile(br'type="([^"]+)"')

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s: %(message)s')
log = logging.getLogger(__file__)

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

def extract_docs(fname, tokenizer):
    raw = open(fname, 'rb').read()
    for i, doc in enumerate(DOC.finditer(raw)):
        attrs = doc.group(1)
        content = doc.group(3)
        start_content_offset = doc.start(3)

        if i and i % 1000 == 0:
            log.info("Processed {} docs".format(i))

        _id = ID.search(attrs)
        _type = TYPE.search(attrs)
        _headline = HEADLINE.search(content)
        _dateline = DATELINE.search(content)
        _text = TEXT.search(content)

        if _id:
            id = _id.group(1)
        else:
            id = b""
        if _type:
            type= _type.group(1)
        else:
            type = b""

        if _headline:
            headline, start_headline_offset = _headline.group(2), start_content_offset + _headline.start(2)
        else:
            headline, start_headline_offset = b"", 0

        if _dateline:
            dateline, start_dateline_offset = _dateline.group(), start_content_offset + _dateline.start(2)
        else:
            dateline, start_dateline_offset = b"", 0

        if _text:
            text, start_text_offset = _text.group(2), start_content_offset + _text.start(2)
        else:
            text, start_text_offset = b"", 0
        doc = Doc(id=id.decode(), type=type.decode())
        tokenizer.tokenize(headline, doc, start_headline_offset, is_headline=True)
        tokenizer.tokenize(dateline, doc, start_dateline_offset, is_dateline=True)

        # paragraph hack
        text = text.replace(b"<P>", b"<p>").replace(b"</P>", b"</p>")
        tokenizer.tokenize(text, doc, start_text_offset)
        yield doc

def process(fnames, output_dir):
    tokenizer = Tokenizer()

    for fname in fnames:
        root = os.path.basename(fname)
        base, ext = os.path.splitext(root)
        out = os.path.join(output_dir, base + DOCREP_EXT)
        with open(out, 'wb') as f:
            writer = dr.Writer(f, Doc)
            for doc in extract_docs(fname, tokenizer):
                writer.write(doc)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gigaword to Docrep parser")
    parser.add_argument("--output-dir", help="directory to place processed files")
    parser.add_argument("files", metavar="file", nargs="+", help="Gigaword files to process")
    args = parser.parse_args()
    process(args.files, args.output_dir)

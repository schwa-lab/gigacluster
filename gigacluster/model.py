from schwa import dr

ENC = 'utf-8'

sentence_on_tokens = dr.decorators.reverse_slices('sentences', 'tokens', 'span', 'sentence')
tokens_on_sentences = dr.decorators.materialize_slices('sentences', 'tokens', 'span', 'tokens')
prev_next_tokens = dr.decorators.add_prev_next('tokens', index_attr='index')
prev_next_sentences = dr.decorators.add_prev_next('sentences', index_attr='index')
sentences_on_paragraphs = dr.decorators.materialize_slices('paras', 'sentences', 'span', 'sents')
paragraph_on_sentences = dr.decorators.reverse_slices('paras', 'sentences', 'span', 'paragraph')

@dr.requires_decoration(sentence_on_tokens, tokens_on_sentences, sentences_on_paragraphs, paragraph_on_sentences, prev_next_tokens, prev_next_sentences)
def decorate(doc):
    return doc

class Token(dr.Ann):
    raw = dr.Text(help="Raw string")
    norm = dr.Text(help="Normalised string")
    # pos = dr.Field(help='POS tag')
    # lemma = dr.Field(help='Lemma')
    span = dr.Slice()
    before = dr.Text(help='Raw text between this and the previous token')
    after = dr.Text(help='Raw text between the last token and end of input')

    def __str__(self):
        return 'T({})'.format(self.norm or self.raw)

    def iter_prev(self, n, same_sentence=True):
        return reversed(list(self._iter_context(n, same_sentence, 'prev')))

    def iter_next(self, n, same_sentence=True):
        return self._iter_context(n, same_sentence, 'next')

    def _iter_context(self, n, same_sentence, attr):
        assert hasattr(self, 'sentence'), \
            'Token._iter_context() requires "sentence" attr, please (re)apply sentence_on_tokens'
        t = self
        s = self.sentence
        for i in xrange(n + 1):
            t = getattr(t, attr)
            if t is None or not hasattr(t, 'sentence') or t.sentence != s:
                break
            yield t

    def __cmp__(self, other):
        return cmp(self.index, other.index)

class Sentence(dr.Ann):
    span = dr.Slice(Token)

    @property
    def text(self):
        assert hasattr(self, 'tokens'), \
            'Sentence.text requires "tokens" attr, please (re)apply tokens_on_sentences'
        return u' '.join(t.text for t in self.tokens)

    def iter_prev(self, n):
        return reversed(list(self._iter_context(n, 'prev')))

    def iter_next(self, n):
        return self._iter_context(n, 'next')

    def _iter_context(self, n, attr):
        s = self
        for i in xrange(n + 1):
            s = getattr(s, attr)
            if s is None:
                break
            yield s

    def __str__(self):
        return self.text

class Headline(dr.Ann):
    span = dr.Slice(Sentence)

class Dateline(dr.Ann):
    span = dr.Slice(Sentence)

class Paragraph(dr.Ann):
    span = dr.Slice(Sentence)

def parse_doc_id(doc_id):
    source, lang, date = doc_id.split('_')
    date, sequence = date.split('.')
    return source, lang, date, sequence

def doc_id_to_basename(doc_id):
    source, lang, date, sequence = parse_doc_id(doc_id)
    return '{}_{}_{}'.format(source.lower(), lang.lower(), date[:6])

class Doc(dr.Doc):
    id = dr.Text()
    type = dr.Text()
    headline = dr.Pointer(Sentence) # TODO turn into paragraph
    dateline = dr.Pointer(Sentence)

    tokens = dr.Store(Token)
    sentences = dr.Store(Sentence)
    paras = dr.Store(Paragraph)

    def __str__(self):
        return '<Doc %s>' % self.id

    @property
    def date_str(self):
        return parse_doc_id(self.id)[2]

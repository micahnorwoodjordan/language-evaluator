import enum

from spacy import (
    load,  # methods
    util, tokenizer, matcher, lang  # modules/classes
)

from .language_utilities import titlize_map_entries


def get_regex_matches(matches, doc):
    """
    :param matches: spacy.matcher.Matcher
    :param doc: spacy.tokens.Doc
    obtain all regex matches from a Doc object. as a note, the underlying regex has been baked into the Matcher
    attached to the NLP instance and can't be altered at this point
    """
    for _, start, end in matches:
        span = doc[start:end]
        yield span.text


def get_lemma_override(token, pos):
    """
    access the lemma override in the master LEMMA_OVERRIDE_CONFIGURATION in cases where spaCy yields incorrect lemmas
    :param token: spacy.tokens.token.Token
    :param pos: str
    """
    if token.text in LEMMA_OVERRIDE_CONFIGURATION[pos]:
        override = LEMMA_OVERRIDE_CONFIGURATION[pos][token.text]
        return override


class UnsupportedLanguageException(Exception):
    pass


class LanguageEvaluationException(Exception):
    pass


class SupportedLanguages(enum.Enum):
    english = 1
    spanish = 2


# should language model signatures be masked?
LANGUAGE_MODEL_MAP = {
    SupportedLanguages.english: 'en_core_web_md',
    SupportedLanguages.spanish: 'es_core_web_md',
}

EXTRA_INFIXES = {
    'default': []  # only populate with regexes
}

REJECTION_PATTERN_CONFIGURATION = {
    'PROPER_NOUNS': {
        'FULL_NAME': [
            {'POS': 'PROPN'}, {'POS': 'PROPN'}  # pattern translation ---> part of speech: proper noun
        ],
    },
    'PHONE_NUMBERS': {
        'INTL_CONVENTIONAL': [
            {'ORTH': '+1'}, {'SHAPE': 'ddd'}, {'ORTH': '-', 'OP': '?'},
            {'SHAPE': 'ddd'}, {'ORTH': '-'}, {'SHAPE': 'dddd'}
        ],
        'INTL_PUNCTUATED': [
            {'ORTH': '+1'}, {'ORTH': '('}, {'SHAPE': 'ddd'},
            {'ORTH': ')'}, {'ORTH': '-', 'OP': '?'},
            {'SHAPE': 'ddd'}, {'ORTH': '-'}, {'SHAPE': 'dddd'}
        ],
        'US_CONVENTIONAL': [
            {'SHAPE': 'ddd'}, {'ORTH': '-', 'OP': '?'},
            {'SHAPE': 'ddd'}, {'ORTH': '-'}, {'SHAPE': 'dddd'}
        ],
        'US_PUNCTUATED': [
            {'ORTH': '('}, {'SHAPE': 'ddd'}, {'ORTH': ')'}, {'ORTH': '-', 'OP': '?'},
            {'SHAPE': 'ddd'}, {'ORTH': '-'}, {'SHAPE': 'dddd'}
        ],
    }
}

# peculiarly, spaCy doesn't know what to do with some pronouns. if other parts of speech have these awkward cases, they
# can be easily hooked into these override configuration settings
LEMMA_OVERRIDE_PARTS_OF_SPEECH = ('PRONOUNS', )
LEMMA_OVERRIDE_CONFIGURATION = titlize_map_entries(
    {
        'PRONOUNS': {
            'us': 'we',
            'him': 'he',
        },
    },
    *LEMMA_OVERRIDE_PARTS_OF_SPEECH
)


class LanguageEvaluator:
    """
    evaluate the complexity of a series of strings entered by a user. as a general class specification, these tokens
    will not be considered "words", and will be parsed out of the token indexing process:
        * proper nouns
        * non-lemma forms
        * contractions (will be expanded into their individial components)

    TODO: handle mispelled words
    TODO: ensure English stop words (such as "a") are parsed correctly
    TODO: consider analyzing token frequency within a user's Journal
    TODO: consider part of speech (POS) tagging
    TODO: handle numbers/integers

    reference: https://realpython.com/natural-language-processing-spacy-python
    """
    def _configure_processor(self, language, **kwargs):
        """
        configure the class instance's Natural Language Processor (NLP) by specifying a language. without any extra
        kwargs, the NLP will pull from the default tokenization and pattern matching configurations.
        """
        _processor = load(LANGUAGE_MODEL_MAP[language])
        prefix_re = util.compile_prefix_regex(_processor.Defaults.prefixes)
        suffix_re = util.compile_suffix_regex(_processor.Defaults.suffixes)
        infix_re = util.compile_infix_regex(list(_processor.Defaults.infixes) + EXTRA_INFIXES['default'])
        _processor.tokenizer = tokenizer.Tokenizer(
            _processor.vocab,
            rules=lang.en.tokenizer_exceptions._exc,  # must supply the tokenizer with exceptions and special cases
            prefix_search=prefix_re.search,
            suffix_search=suffix_re.search,
            infix_finditer=infix_re.finditer,
        )
        patterns = []
        _matcher = matcher.Matcher(_processor.vocab)
        rejection_configs = [config for config in REJECTION_PATTERN_CONFIGURATION.values()]
        for config in rejection_configs:
            for rejection_key, pattern in config.items():  # NOTE: iteration is funny, since each dict is only length 1
                patterns.append(pattern)
        _matcher.add(rejection_key, patterns)

        self.matcher = _matcher
        self.NLP = _processor

    def __init__(self, language):
        self._configure_processor(language)

    def tokenize_entry(self, entry, regex_exceptions=None):
        """
        when entries get tokenized, only each token's base form will be considered.
        for example, the tokenizer will parse out the tokens "do", "doing", "did", and "does" from an expression
        containing them all, and only include their lemma ("do") for further processing.

        any matches on the regular expressions and rules configured in the REJECTION_PATTERN_CONFIGURATION will
        also be parsed out.
        """
        tokens = []  # ensure deterministic results for testing
        doc = self.NLP(entry)  # non-intuitive spaCy term
        rejection_regex_matches = [
            token for match in get_regex_matches(self.matcher(doc), doc) for token in match.split(' ')
        ]  # TODO: not safe to assume that ALL matches will be delimited by a space character
        regex_exceptions = regex_exceptions or []

        for token in doc:
            should_reject = token.is_punct or token.lemma_ in tokens or token.text in tokens or \
                any([token.lemma_ in m or token.text in m for m in rejection_regex_matches]) and \
                token.text not in regex_exceptions
            if should_reject:
                continue

            # this is very clunky but it handles incorrect spaCy token lemmas. this is only relevant to
            # pronouns so far, but let's wire this up for any future lemma overrides
            # TODO: explore potential override clashes between different POS's
            for pos in LEMMA_OVERRIDE_CONFIGURATION.keys():
                lemma_override_or_none = get_lemma_override(token, pos)
                if lemma_override_or_none is None:
                    token = token.lemma_
                else:
                    token = lemma_override_or_none
                if token not in tokens:
                    tokens.append(token)
        return tokens

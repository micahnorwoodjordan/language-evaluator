import enum

from spacy import (
    load,  # methods
    util, tokenizer, matcher, lang  # modules/classes
)


class UnsupportedLanguageException(Exception):
    pass


class LanguageEvaluationException(Exception):
    pass


class SupportedLanguages(enum.Enum):
    english = 1
    spanish = 2


# should language model signatures be masked?
SPACY_LANGUAGE_MODEL_MAP = {
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
}


class LanguageEvaluator:
    """
    evaluate the complexity of a series of strings entered by a user. as a general class specification, these tokens
    will not be considered "words", and will be parsed out of the token indexing process:
        * proper nouns
        * non-lemma forms
        * contractions (will be expanded into their individial components)

    TODO: handle mispelled words
    TODO: consider analyzing token frequency within a user's Journal
    TODO: consider part of speech (POS) tagging

    reference: https://realpython.com/natural-language-processing-spacy-python
    """
    def _configure_processor(self, language, **kwargs):
        """
        configure the class instance's Natural Language Processor (NLP) by specifying a language. without any extra
        kwargs, the NLP will pull from the default tokenization and pattern matching configurations.
        """
        _processor = load(SPACY_LANGUAGE_MODEL_MAP[language])
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
        _matcher = matcher.Matcher(_processor.vocab)
        rejection_configs = [config for config in REJECTION_PATTERN_CONFIGURATION.values()]
        for config in rejection_configs:
            for rejection_key, pattern in config.items():  # NOTE: iteration is funny, since each dict is only length 1
                _matcher.add(rejection_key, [pattern])

        self.matcher = _matcher
        self.NLP = _processor

    def __init__(self, language):
        self._configure_processor(language)

    def tokenize_entry(self, entry):
        """
        when entries get tokenized, only each token's base form will be considered.
        for example, the tokenizer will parse out the tokens "do", "doing", "did", and "does" from an expression
        containing them all, and only include their lemma ("do") for further processing.

        any matches on the regular expressions and rules configured in the REJECTION_PATTERN_CONFIGURATION will
        also be parsed out.
        """
        def parse_matches(matches):
            for _, start, end in matches:
                span = doc[start:end]
                yield span.text

        tokens = set()
        doc = self.NLP(entry)  # non-intuitive spaCy term
        rejection_regex_matches = [
            token for match in parse_matches(self.matcher(doc)) for token in match.split(' ')
        ]  # TODO: not safe to assume that ALL matches will be delimited by a space character

        for token in doc:
            if token.is_punct:
                continue
            token = token.lemma_
            if token in tokens or token in rejection_regex_matches:
                continue
            tokens.add(token)
        return tokens

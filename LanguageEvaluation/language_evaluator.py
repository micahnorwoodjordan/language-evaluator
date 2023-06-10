import enum
import copy

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


def titlize_map_entries(m, *args):
    """
    titleize only certain part-of-speech configurations within the master LEMMA_OVERRIDE_CONFIGURATION
    :param m: dict
    :param args: list
    :return m: dict
    """
    m = copy.deepcopy(m)
    root_keys = list(m.keys())
    for root_key in root_keys:
        if root_key not in args:
            continue
        for child_key, child_value in zip(list(m[root_key].keys()), list(m[root_key].values())):
            m[root_key][child_key.title()] = child_value
    return m


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
    TODO: consider analyzing token frequency within a user's Journal
    TODO: consider part of speech (POS) tagging

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
        def parse_regex_matches(matches):
            for _, start, end in matches:
                span = doc[start:end]
                yield span.text

        def handle_lemma_override(token, pos):
            if token.text in LEMMA_OVERRIDE_CONFIGURATION[pos]:
                override = LEMMA_OVERRIDE_CONFIGURATION[pos][token.text]
                return override

        tokens = []  # ensure deterministic results for testing
        doc = self.NLP(entry)  # non-intuitive spaCy term
        rejection_regex_matches = [
            token for match in parse_regex_matches(self.matcher(doc)) for token in match.split(' ')
        ]  # TODO: not safe to assume that ALL matches will be delimited by a space character

        for token in doc:
            should_reject = token.is_punct or \
                token.lemma_ in tokens or token.text in tokens or \
                token.lemma_ in rejection_regex_matches or token.text in rejection_regex_matches
            if should_reject:
                continue

            # this is very clunky but it handles incorrect spaCy token lemmas. this is only relevant to
            # pronouns so far, but let's wire this up for any future lemma overrides
            # TODO: explore potential override clashes between different POS's
            for pos in LEMMA_OVERRIDE_CONFIGURATION.keys():
                override_or_none = handle_lemma_override(token, pos)
                if override_or_none is None:
                    token = token.lemma_
                else:
                    token = override_or_none
                if token not in tokens:
                    tokens.append(token)
        return tokens

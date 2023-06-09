import enum

from spacy import load, util, tokenizer, matcher


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

MATCHING_PATTERNS = {
    'PROPER_NOUNS': {
        'FULL_NAME': [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    },
}


class LanguageEvaluator:
    """
    evaluate the complexity of a series of strings entered by a user
    TODO: handle mispelled words
    TODO: handle conjunctions

    TODO: consider analyzing token frequency within a user's Journal
    TODO: consider part of speech (POS) tagging

    reference: https://realpython.com/natural-language-processing-spacy-python
    """
    def _configure_processor(self, language, **kwargs):
        processor = load(SPACY_LANGUAGE_MODEL_MAP[language])  # natural language processor

        # tokenizer
        # NOTE: this is probably the only tokenizer use case, but new tokenizers can be constructed and swapped in/out
        # preceeding and proceeding punctuation, such as opening and closing parenthesis, need to be accounted for
        prefix_re = util.compile_prefix_regex(processor.Defaults.prefixes)
        suffix_re = util.compile_suffix_regex(processor.Defaults.suffixes)
        infix_re = util.compile_infix_regex(list(processor.Defaults.infixes) + EXTRA_INFIXES['default'])
        processor.tokenizer = tokenizer.Tokenizer(
            processor.vocab,
            prefix_search=prefix_re.search,
            suffix_search=suffix_re.search,
            infix_finditer=infix_re.finditer,
        )

        # matcher
        # parse proper nouns such as names
        _matcher = matcher.Matcher(processor.vocab)  # avoid symbol clash
        key = 'FULL_NAME'
        pattern = MATCHING_PATTERNS['PROPER_NOUNS'][key]
        _matcher.add(key, [pattern])
        self.matcher = _matcher
        self.NLP = processor

    def __init__(self, language):
        self._configure_processor(language)

    def tokenize_entry(self, entry):
        # witness the spaCy magic happen. the instance's processer, tokenizer, and matcher are already configured at this point
        def parse_matches(matches):
            for _, start, end in matches:
                span = doc[start:end]
                yield span.text

        tokens = set()
        doc = self.NLP(entry)
        matches = [
            token for match in parse_matches(self.matcher(doc)) for token in match.split(' ')
        ]  # TODO: it probably won't BUT, evaluate whether this can backfire on new pattern configurations

        for token in doc:
            if not token.is_punct and token.is_alpha:
                token = token.lemma_  # only tokenize the base form of each token (do / doing / did / does ---> do)
                if token not in tokens and token not in matches:  # don't count proper nouns as words
                    tokens.add(token)
        return tokens

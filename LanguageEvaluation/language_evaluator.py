import spacy
from enum import Enum


class UnsupportedLanguageException(Exception):
    pass


class LanguageEvaluationException(Exception):
    pass


class SupportedLanguages(Enum):
    english = 1
    spanish = 2


# should language model signatures be masked?
SPACY_LANGUAGE_MODEL_MAP = {
    SupportedLanguages.english: 'en_core_web_md',
    SupportedLanguages.spanish: 'es_core_web_md',
}

EXTRA_INFIXES = []  # only populate with regexes


class LanguageEvaluator:
    """
    evaluate the complexity of a series of strings entered by a user
    TODO: handle mispelled words
    TODO: handle conjunctions
    """
    def __init__(self, language):
        self.NLP = spacy.load(SPACY_LANGUAGE_MODEL_MAP[language])  # natural language processor
        prefix_re = spacy.util.compile_prefix_regex(self.NLP.Defaults.prefixes)
        suffix_re = spacy.util.compile_suffix_regex(self.NLP.Defaults.suffixes)
        infix_re = spacy.util.compile_infix_regex(list(self.NLP.Defaults.infixes) + EXTRA_INFIXES)

        # NOTE: this is probably the only tokenizer use case, but new tokenizers can be constructed and swapped in/out
        # preceeding and proceeding punctuation, such as opening and closing parenthesis, need to be accounted for
        self.NLP.tokenizer = spacy.tokenizer.Tokenizer(
            self.NLP.vocab,
            prefix_search=prefix_re.search,
            suffix_search=suffix_re.search,
            infix_finditer=infix_re.finditer,
        )

    def tokenize_entry(self, entry):
        tokens = [str(token).strip() for token in self.NLP(entry) if not token.is_punct and token.is_alpha]
        return tokens

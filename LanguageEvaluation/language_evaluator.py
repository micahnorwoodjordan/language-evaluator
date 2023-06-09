import spacy
from enum import Enum


class SupportedLanguages(Enum):
    english = 1
    spanish = 2


# should language model signatures be masked?
SPACY_LANGUAGE_MODEL_MAP = {
    SupportedLanguages.english: 'en_core_web_md',
    SupportedLanguages.spanish: 'es_core_web_md',
}


class LanguageEvaluator:
    """
    evaluate the complexity of a series of strings entered by a user
    TODO: handle mispelled words
    TODO: handle hyphenated words
    """
    def __init__(self, language):
        self.NLP = spacy.load(SPACY_LANGUAGE_MODEL_MAP[language])  # natural language processor
        self.tokens = []

    def tokenize_entry(self, entry):
        tokens = [str(token).strip() for token in self.NLP(entry) if not token.is_punct and token.is_alpha]
        return tokens

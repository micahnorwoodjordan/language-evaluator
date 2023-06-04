from enum import Enum


class SupportedLanguages(Enum):
    english = 1
    spanish = 2


class LanguageDetector:
    def __init__(self, language=None):
        self.language = language
        self.language_tokens = []

    def detect_language(self):
        for token in self.language_tokens:
            pass

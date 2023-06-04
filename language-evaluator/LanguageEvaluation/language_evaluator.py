from LanguageEvaluation.utilities import SupportedLanguages


class LanguageEvaluator:
    """
    evaluate the complexity of a series of strings entered by a user
    """
    def __init__(self, language):
        self.language = language

    @staticmethod
    def sanitize_english_string(string):
        """
        trim non-alpha characters from string
        """
        ascii_A = 65
        ascii_z = 122
        sanitized = ''

        for c in string:
            if ascii_A <= ord(c) <= ascii_z or c == ' ':
                sanitized += c
        return sanitized.strip()

    @staticmethod
    def sanitize_spanish_string(string):
        pass  # coming soon

    def get_distinct_tokens(self, series):
        """
        parse a series of strings to extract the individual tokens
        """
        distinct_tokens = set()

        for sentence in series:
            if self.language == SupportedLanguages.english:
                sentence = LanguageEvaluator.sanitize_english_string(sentence)
            for token in sentence.split(' '):  # tokenize by whitespace
                distinct_tokens.add(token)

        return distinct_tokens

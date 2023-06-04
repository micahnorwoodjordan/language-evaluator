from UserInteraction.utilities import get_language, get_series, display_results
from LanguageEvaluation.language_evaluator import LanguageEvaluator


if __name__ == '__main__':
    """
    I'd like to get a feel for how many words I know in spanish
    """
    def do():
        # TODO: persist these tokens to a file to "grow" the token "database" and keep track of progress
        try:
            language = get_language()
        except Exception as e:
            print(e)
            return

        series = get_series()
        evaluator = LanguageEvaluator(language)
        tokens = evaluator.get_distinct_tokens(series)
        display_results(tokens)

do()

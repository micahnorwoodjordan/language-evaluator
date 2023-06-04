from UserInteraction.user_interaction_utilities import get_language, get_series, display_results
from LanguageEvaluation.language_evaluator import LanguageEvaluator
from TokenStorage.token_storage_utilities import TOKEN_STORAGE_FILE, save_tokens

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

        token_storage_filepath = TOKEN_STORAGE_FILE.format(language=language.name)
        series = get_series()
        evaluator = LanguageEvaluator(language)
        tokens = evaluator.get_distinct_tokens(series)
        save_tokens(token_storage_filepath, tokens)
        display_results(tokens)

    do()

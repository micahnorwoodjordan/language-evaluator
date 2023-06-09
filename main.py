import argparse

from UserInteraction.user_interaction_utilities import get_language, get_entry, display_results
from LanguageEvaluation.language_evaluator import LanguageEvaluator
from TokenIndexing.token_indexing_utilities import save_tokens_for_language

if __name__ == '__main__':
    """
    I'd like to get a feel for how many words I know in spanish.
    This would probably be best accomplished by writing in a journal!
    """
    def run_cli():
        try:
            language = get_language()
        except Exception as e:
            print(e)
            return

        entry = get_entry()
        evaluator = LanguageEvaluator(language)
        tokens = evaluator.tokenize_entry(entry)
        save_tokens_for_language(tokens, language.name)
        display_results(tokens)

    def run_app():
        print('running app')

    parser = argparse.ArgumentParser()
    parser.add_argument('--app', action='store_true', help='whether or not to start the app, instead of cli program')
    args_dictionary = parser.parse_args().__dict__

    if args_dictionary.get('app'):
        run_app()
    else:
        run_cli()

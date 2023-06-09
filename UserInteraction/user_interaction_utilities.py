from LanguageEvaluation.language_evaluator import SupportedLanguages
from exceptions import InputRecursionException


REMINDER_PROMPT_THRESHOLD = 10


def get_entry():
    """
    handle user input
    """
    inp = None
    user_checkin_msg = 'enter "done" whenever you\'re done.\n'  # TODO: randomize messages for UX
    intro_prompt = 'tell an interesting story. ' + user_checkin_msg
    entry = ''
    iterations = 0

    print(intro_prompt)

    while inp != 'done':
        inp = input('>>> ')
        if inp != 'done':
            entry += inp

        if iterations > 0:
            if iterations % REMINDER_PROMPT_THRESHOLD == 0:
                print('remember, ' + user_checkin_msg)  # maybe user forgot how to exit
        iterations += 1

    return entry


def get_language(recurses=None, msg=None):
    recurse_limit = 10
    if recurses is None:  # recurse arg is hacky; it shouldn't be required
        recurses = 0
    if recurses == recurse_limit:  # don't add endless stack frames from bad user input
        raise InputRecursionException('killing program gracefully.')

    if msg is None:
        msg = 'select a language\nenglish: 1\nspanish: 2\n>>> '
    try:
        language = input(msg)
        return SupportedLanguages(int(language))
    except ValueError:
        recurses += 1
        get_language(recurses, msg)  # probably a better solution than recursing


def display_results(tokens, minimal=True):
    msg = 'Here are your results: \n'
    if minimal:
        results = f'The index has been updated with {len(tokens)} distinct word(s).'
    else:  # TODO: define a more detailed presentation scheme
        results = ''
        for token in tokens:
            results += f'{token}\n'
    print(f'{msg}{results}')

from pathlib import Path

TOKEN_STORAGE_FILE = '{language}-tokens.txt'


def get_saved_tokens_for_language(language):
    filepath = TOKEN_STORAGE_FILE.format(language=language)
    with open(filepath, 'r') as file:
        existing_tokens = [token.replace('\n', '') for token in file.readlines()]
    return existing_tokens


def save_tokens_for_language(new_tokens, language):
    filepath = TOKEN_STORAGE_FILE.format(language=language)
    path = Path(filepath)

    if not path.is_file():
        path.touch(exist_ok=False)  # raise exception to fail if any buggy black magic going on

    existing_tokens = get_saved_tokens_for_language(language)
    with open(filepath, 'a') as file:
        for token in new_tokens:
            if token not in existing_tokens:
                file.write(f'{token}\n')

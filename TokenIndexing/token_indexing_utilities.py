from pathlib import Path

TOKEN_INDEX_FILE = 'artifacts/token-indexing/{language}-tokens.txt'


def get_indexed_tokens(language):
    """
    :param language: str<SupportedLanguages.language.name>
    """
    filepath = TOKEN_INDEX_FILE.format(language=language)
    with open(filepath, 'r') as file:
        indexed_tokens = [token.replace('\n', '') for token in file.readlines()]
    return indexed_tokens


def index_tokens(new_tokens, language):
    filepath = TOKEN_INDEX_FILE.format(language=language)
    path = Path(filepath)

    if not path.is_file():
        path.touch(exist_ok=False)  # raise exception to fail if any buggy black magic going on

    indexed_tokens = get_indexed_tokens(language)
    with open(filepath, 'a') as file:
        for token in new_tokens:
            if token not in indexed_tokens:
                file.write(f'{token}\n')

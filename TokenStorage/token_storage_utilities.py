TOKEN_STORAGE_FILE = '{language}-tokens.txt'


def save_tokens(filepath, tokens):
    with open(filepath, 'a') as file:
        for token in tokens:
            file.write(f'{token}\n')

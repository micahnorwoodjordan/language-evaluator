TOKEN_STORAGE_FILE = '{language}-tokens.txt'


def save_tokens(filepath, new_tokens):
    with open(filepath, 'r') as file:
        existing_tokens = [token.replace('\n', '') for token in file.readlines()]

    with open(filepath, 'a') as file:
        for token in new_tokens:
            if token not in existing_tokens:
                file.write(f'{token}\n')

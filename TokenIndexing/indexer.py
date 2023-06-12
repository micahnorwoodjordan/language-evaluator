from pathlib import Path


TOKEN_INDEX_FILE = 'artifacts/token-indexing/{language}-tokens.txt'


class TokenIndexer:
    def __init__(self, language):
        self.filepath = TOKEN_INDEX_FILE.format(language=language)
        self.index = self.get_indexed_tokens()

    def get_indexed_tokens(self):
        """
        :param language: str<SupportedLanguages.language.name>
        """
        with open(self.filepath, 'r') as file:
            indexed_tokens = [token.replace('\n', '') for token in file.readlines()]
        return indexed_tokens

    def index_tokens(self, new_tokens):
        path = Path(self.filepath)

        if not path.is_file():
            path.touch(exist_ok=False)  # be loud and fail if any weird black magic is going on

        with open(path, 'a') as file:
            for token in new_tokens:
                if token not in self.index:
                    file.write(f'{token}\n')

import re

KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',
            'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}

KEYWORD_RE = "class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return"
SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}
SYMBOLS_RE = "{|}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|\||<|>|=|~"
INTEGER_CONSTANT = "integerConstant"  ##lambda x: str(x).isdecimal() and 0 < int(x) < 32767
INTEGER_CONSTANT_RE = "\d+"
STRING_CONSTANT = "stringConstant"
STRING_CONSTANT_RE = "[^\"\n]+"
IDENTIFIER = "identifier"
IDENTIFIER_RE = "[a-zA-Z_][\w]*"

KEYWORD = "keyword"
SYMBOL = "symbol"

REGEXS = {KEYWORD: re.compile(KEYWORD_RE), SYMBOL: re.compile(SYMBOLS_RE),
          INTEGER_CONSTANT: re.compile(INTEGER_CONSTANT_RE), STRING_CONSTANT: re.compile(STRING_CONSTANT_RE),
          IDENTIFIER: re.compile(IDENTIFIER_RE)}


class Tokenizer:
    """
    Class representing a stream of tokens parsed from a .jack file.
    """

    def __init__(self, source_file):
        """
        Create a tokenizer stream over an input file.
        :param source_file: input file
        """
        self.__filename = source_file
        with open(self.__filename, 'r') as file:
            self.__file = file.read()

    def next_token(self):
        """
        :return: next token
        """
        for token in REGEXS:
            match = REGEXS[token].match(self.__file)
            if match:
                token_content = self.__file[match.pos:match.endpos]
                self.__file = self.__file[match.endpos:]
                return Token(token, token_content)

    def has_more_tokens(self):
        return self.__file is not []

    def eat(self, string):
        token = self.next_token()
        if string != token.get_content():
            raise RuntimeError


class Token:
    """
    representing a jack token
    """

    def __init__(self, content, type):
        self.__content = content
        self.__type = type

    def get_content(self):
        return self.__content

    def get_type(self):
        return self.__type
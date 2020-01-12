import re

KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',
            'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}
COMMENTS_RE = '\s*(?:\s*(?:(?:\/\*.*?\*\/)|(?:\/\/[^\n]*))\s*)*\s*'

KEYWORD_RE = COMMENTS_RE + "(class|constructor|function|method|field|static|var|int|char|boolean|void|" \
                           "true|false|null|this|let|do |if|else|while|return)"
SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}
SYMBOLS_RE = COMMENTS_RE + "({|}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|\||<|>|=|~)"
INTEGER_CONSTANT = "integerConstant"
INTEGER_CONSTANT_RE = COMMENTS_RE + "(\d+)"
STRING_CONSTANT = "stringConstant"
STRING_CONSTANT_RE = COMMENTS_RE + "(\"[^\"\n]+\")"
IDENTIFIER = "identifier"
IDENTIFIER_RE = COMMENTS_RE + "([a-zA-Z_][\w]*)"

KEYWORD = "keyword"
SYMBOL = "symbol"

REGEXS = {KEYWORD: re.compile(KEYWORD_RE, flags=re.DOTALL), SYMBOL: re.compile(SYMBOLS_RE, flags=re.DOTALL),
          INTEGER_CONSTANT: re.compile(INTEGER_CONSTANT_RE, flags=re.DOTALL),
          STRING_CONSTANT: re.compile(STRING_CONSTANT_RE, flags=re.DOTALL),
          IDENTIFIER: re.compile(IDENTIFIER_RE, flags=re.DOTALL)}


class Tokenizer:
    """
    Class representing a stream of tokens parsed from a .jack file.
    """

    def __init__(self, source_file: str):
        """
        Create a tokenizer stream over an input file.
        :param source_file: input file
        """
        self.__filename = source_file
        with open(self.__filename, 'r') as file:
            self.__file = file.read()

    def next_token(self, cut=True):
        """
        :return: next token
        """
        for token in REGEXS:
            match = REGEXS[token].match(self.__file)
            if match:
                token_content = match.group(1)
                if cut:
                    self.__file = self.__file[match.span(1)[1]:]
                next_char = ''
                if len(self.__file) > match.span(1)[1]:
                    next_char = self.__file[match.span(1)[1]]
                return Token(token_content, token, next_char)

    def has_more_tokens(self):
        return self.__file is not []

    def eat(self, string: str):
        token = self.next_token()
        if string != token.get_content():
            raise RuntimeError("Unexpected token: " + token.get_content() + " , expected token: " + string)

    def peek(self):
        return self.next_token(cut=False)


class Token:
    """
    representing a jack token
    """

    def __init__(self, content, type, next_char=""):
        self.__content = content
        self.__type = type
        self.__next_char = next_char

    def get_next_char(self):
        return self.__next_char

    def get_content(self):
        return self.__content

    def get_type(self):
        return self.__type

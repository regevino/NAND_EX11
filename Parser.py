from lxml import etree as ET
from Tokenizer import *

EXPRESSION_LIST = 'expressionList'

TERM = 'term'

RETURN_STATEMENT = 'returnStatement'

DO_STATEMENT = 'doStatement'

WHILE_STATEMENT = 'whileStatement'

IF_STATEMENT = 'ifStatement'

EXPRESSION = 'expression'

UNARY_OPS = '-~'

KEYWORD_CONSTS = ['true', 'false', 'null', 'this']

PERIOD = '.'

OPS = '+-*/&|<>='

ELSE = 'else'
EQUALS = '='
CLOSE_BRACKETS = ']'
OPEN_BRACKETS = '['
LET_STATEMENT = 'letStatement'
IF = 'if'
RETURN = 'return'
WHILE = 'while'
LET = 'let'
DO = 'do '
STATEMENTS = 'statements'
VAR_DEC = 'varDec'
SUBROUTINE_BODY = 'subroutineBody'
VAR = 'var'
PARAMETER_LIST = 'parameterList'
CLOSE_PAR = ')'
OPEN_PAR = '('
VOID = 'void'
SUBROUTINE_DEC = 'subroutineDec'
SEMICOLON = ';'
COMMA = ','
CLASS_VAR_DEC = 'classVarDec'
CLASS_TAG = 'class'
IDENTIFIER = 'identifier'
SYMBOL = 'symbol'
END_BLOCK = '}'
CONSTRUCTOR = 'constructor'
FUNCTION = 'function'
METHOD = 'method'
STATIC = 'static'
FIELD = 'field'
START_BLOCK = '{'
CLASS_KEYWORD = 'class'


class Parser:
    """
    Parse a tokenized jack input into a parse tree.
    """

    def __init__(self, tokenizer: Tokenizer):
        """
        Create a new parser over a token stream of jack input.
        """
        self.__tokenizer = tokenizer

    def parse(self) -> ET.ElementTree:
        """
        Parse the token stream until there are no more tokens to parse.
        :return: ElementTree representing the parseTree
        """

        new_element = ET.Element('ROOT')
        try:
            self.__compile_class(new_element)
        except RuntimeError as e:
            print(e)
            print("Dumping Tree:\n")
            ET.dump(new_element[0])
        tree = ET.ElementTree(new_element[0])

        return tree

    def __compile_symbol(self, element: ET.Element, string):
        self.__tokenizer.eat(string)
        new_element = ET.Element(SYMBOL)
        new_element.text = string
        element.append(new_element)

    def __compile_identifier(self, element: ET.Element):
        token = self.__tokenizer.next_token()
        assert token.get_type() == IDENTIFIER, "Token type is: " + token.get_type() \
                                               + ", Token is: " + token.get_content()
        new_element = ET.Element(IDENTIFIER)
        new_element.text = token.get_content()
        element.append(new_element)

    def __compile_keyword(self, element: ET.Element):
        token = self.__tokenizer.next_token()
        assert token.get_type() == KEYWORD, "Token type is: " + token.get_type() + ", Token is: " + token.get_content()
        new_element = ET.Element(KEYWORD)
        new_element.text = token.get_content()
        element.append(new_element)

    def __compile_class(self, element: ET.Element):
        new_element = ET.Element(CLASS_TAG)
        element.append(new_element)
        self.__compile_keyword(new_element)  # Class keyword
        self.__compile_identifier(new_element)  # Class var name
        self.__compile_symbol(new_element, START_BLOCK)
        next_token = self.__tokenizer.peek().get_content()
        while next_token == STATIC or next_token == FIELD:
            self.__compile_class_var_dec(new_element)
            next_token = self.__tokenizer.peek().get_content()
        while next_token == CONSTRUCTOR or next_token == FUNCTION or next_token == METHOD:
            self.__compile__subroutine_dec(new_element)
            next_token = self.__tokenizer.peek().get_content()
        self.__compile_symbol(new_element, END_BLOCK)

    def __compile_class_var_dec(self, element):
        new_element = ET.Element(CLASS_VAR_DEC)
        element.append(new_element)

        self.__compile_keyword(new_element)
        self.__compile_type(new_element)
        self.__compile_identifier(new_element)
        next_token = self.__tokenizer.peek().get_content()
        while next_token == COMMA:
            self.__compile_symbol(new_element, next_token)
            self.__compile_identifier(new_element)
            next_token = self.__tokenizer.peek().get_content()
        self.__compile_symbol(new_element, SEMICOLON)

    def __compile_type(self, element):
        next_token = self.__tokenizer.peek()
        if next_token.get_type() == IDENTIFIER:
            self.__compile_identifier(element)
        elif next_token.get_type() == KEYWORD:
            self.__compile_keyword(element)
        else:
            raise RuntimeError(
                "Type must be identifier or keyword but token" + next_token.get_content() + "was of type "
                + next_token.get_type())

    def __compile__subroutine_dec(self, element):
        new_element = ET.Element(SUBROUTINE_DEC)
        element.append(new_element)
        self.__compile_keyword(new_element)
        if self.__tokenizer.peek().get_content() == VOID:
            self.__compile_keyword(new_element)
        else:
            self.__compile_type(new_element)
        self.__compile_identifier(new_element)
        self.__compile_symbol(new_element, OPEN_PAR)
        self.__compile_parameter_list(new_element)
        self.__compile_symbol(new_element, CLOSE_PAR)
        self.__compile_subroutine_body(new_element)

    def __compile_parameter_list(self, element):
        new_element = ET.Element(PARAMETER_LIST)
        element.append(new_element)
        if self.__tokenizer.peek().get_content() == CLOSE_PAR:
            new_element.text = '\n'
            return
        self.__compile_type(new_element)
        self.__compile_identifier(new_element)
        next_token = self.__tokenizer.peek().get_content()
        while next_token is COMMA:
            self.__compile_symbol(new_element, COMMA)
            self.__compile_type(new_element)
            self.__compile_identifier(new_element)
            next_token = self.__tokenizer.peek().get_content()

    def __compile_subroutine_body(self, element):
        new_element = ET.Element(SUBROUTINE_BODY)
        element.append(new_element)
        self.__compile_symbol(new_element, START_BLOCK)
        while self.__tokenizer.peek().get_content() == VAR:
            self.__compile_var_dec(new_element)
        self.__compile_statements(new_element)
        self.__compile_symbol(new_element, END_BLOCK)

    def __compile_var_dec(self, element):
        new_element = ET.Element(VAR_DEC)
        element.append(new_element)
        self.__compile_keyword(new_element)
        self.__compile_type(new_element)
        self.__compile_identifier(new_element)
        next_token = self.__tokenizer.peek().get_content()
        while next_token == COMMA:
            self.__compile_symbol(new_element, next_token)
            self.__compile_identifier(new_element)
            next_token = self.__tokenizer.peek().get_content()
        self.__compile_symbol(new_element, SEMICOLON)

    def __compile_statements(self, element: ET.Element):
        new_element = ET.Element(STATEMENTS)
        element.append(new_element)
        next_token = self.__tokenizer.peek().get_content()
        while self.__tokenizer.peek().get_type() == KEYWORD:
            if next_token == DO:
                self.__compile_do(new_element)
            elif next_token == LET:
                self.__compile_let(new_element)
            elif next_token == WHILE:
                self.__compile_while(new_element)
            elif next_token == RETURN:
                self.__compile_return(new_element)
            elif next_token == IF:
                self.__compile_if(new_element)
            else:
                if not new_element:
                    new_element.text = '\n'
                return
            next_token = self.__tokenizer.peek().get_content()

    def __compile_let(self, element):
        new_element = ET.Element(LET_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        self.__compile_identifier(new_element)
        if self.__tokenizer.peek().get_content() == OPEN_BRACKETS:
            self.__compile_symbol(new_element, OPEN_BRACKETS)
            self.__compile_expression(new_element)
            self.__compile_symbol(new_element, CLOSE_BRACKETS)
        self.__compile_symbol(new_element, EQUALS)
        self.__compile_expression(new_element)
        self.__compile_symbol(new_element, SEMICOLON)

    def __compile_expression(self, element):
        new_element = ET.Element(EXPRESSION)
        element.append(new_element)
        self.__compile_term(new_element)
        next_token = self.__tokenizer.peek().get_content()
        while next_token in OPS:
            self.__compile_symbol(new_element, next_token)
            self.__compile_term(new_element)
            next_token = self.__tokenizer.peek().get_content()

    def __compile_if(self, element):
        new_element = ET.Element(IF_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        self.__compile_symbol(new_element, OPEN_PAR)
        self.__compile_expression(new_element)
        self.__compile_symbol(new_element, CLOSE_PAR)
        self.__compile_symbol(new_element, START_BLOCK)
        self.__compile_statements(new_element)
        self.__compile_symbol(new_element, END_BLOCK)
        if self.__tokenizer.peek().get_content() == ELSE:
            self.__compile_keyword(new_element)
            self.__compile_symbol(new_element, START_BLOCK)
            self.__compile_statements(new_element)
            self.__compile_symbol(new_element, END_BLOCK)

    def __compile_while(self, element):
        new_element = ET.Element(WHILE_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        self.__compile_symbol(new_element, OPEN_PAR)
        self.__compile_expression(new_element)
        self.__compile_symbol(new_element, CLOSE_PAR)
        self.__compile_symbol(new_element, START_BLOCK)
        self.__compile_statements(new_element)
        self.__compile_symbol(new_element, END_BLOCK)

    def __compile_do(self, element):
        new_element = ET.Element(DO_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        self.__compile_subroutine_call(new_element)
        self.__compile_symbol(new_element, SEMICOLON)

    def __compile_subroutine_call(self, element):
        new_element = element
        self.__compile_identifier(new_element)
        next_token = self.__tokenizer.peek().get_content()
        if next_token == OPEN_PAR:
            self.__compile_symbol(new_element, OPEN_PAR)
            self.__compile_expression_list(new_element)
            self.__compile_symbol(new_element, CLOSE_PAR)
        elif next_token == PERIOD:
            self.__compile_symbol(new_element, PERIOD)
            self.__compile_identifier(new_element)
            self.__compile_symbol(new_element, OPEN_PAR)
            self.__compile_expression_list(new_element)
            self.__compile_symbol(new_element, CLOSE_PAR)

    def __compile_return(self, element):
        new_element = ET.Element(RETURN_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        next_token = self.__tokenizer.peek().get_content()
        if next_token != SEMICOLON:
            self.__compile_expression(new_element)
        self.__compile_symbol(new_element, SEMICOLON)

    def __compile_term(self, element):
        new_element = ET.Element(TERM)
        element.append(new_element)
        next_token = self.__tokenizer.peek()
        if next_token.get_type() == INTEGER_CONSTANT:
            newer_element = ET.Element(INTEGER_CONSTANT)
            newer_element.text = self.__tokenizer.next_token().get_content()
            new_element.append(newer_element)
        elif next_token.get_type() == STRING_CONSTANT:
            newer_element = ET.Element(STRING_CONSTANT)
            newer_element.text = self.__tokenizer.next_token().get_content()[1:-1]
            new_element.append(newer_element)
        elif next_token.get_content() in KEYWORD_CONSTS:
            self.__compile_keyword(new_element)
        elif next_token.get_type() == IDENTIFIER:
            if next_token.get_next_char() == PERIOD:
                self.__compile_subroutine_call(new_element)
                return
            self.__compile_identifier(new_element)
            next_token = self.__tokenizer.peek()
            if next_token.get_content() == OPEN_BRACKETS:
                self.__compile_symbol(new_element, OPEN_BRACKETS)
                self.__compile_expression(new_element)
                self.__compile_symbol(new_element, CLOSE_BRACKETS)
        elif next_token.get_content() in UNARY_OPS:
            self.__compile_symbol(new_element, next_token.get_content())
            self.__compile_term(new_element)
        elif next_token.get_content() == OPEN_PAR:
            self.__compile_symbol(new_element, OPEN_PAR)
            self.__compile_expression(new_element)
            self.__compile_symbol(new_element, CLOSE_PAR)

    def __compile_expression_list(self, element):
        new_element = ET.Element(EXPRESSION_LIST)
        element.append(new_element)
        next_token = self.__tokenizer.peek()
        if self.__is_term(next_token):
            self.__compile_expression(new_element)
        else:
            new_element.text = '\n'
            return
        next_token = self.__tokenizer.peek()
        while next_token.get_content() == COMMA:
            self.__compile_symbol(new_element, COMMA)
            self.__compile_expression(new_element)
            next_token = self.__tokenizer.peek()

    def __is_term(self, token: Token):
        return (token.get_type() == STRING_CONSTANT or token.get_type() == INTEGER_CONSTANT
                or token.get_content() in KEYWORD_CONSTS or token.get_type() == IDENTIFIER
                or token.get_content() in UNARY_OPS or token.get_content() == OPEN_PAR)

from lxml import etree as ET

from SymbolTable import Symbol
from Tokenizer import *
from VMWrter import VMWriter

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
        self.__vm_writer = VMWriter()
        self.__class_name = ""
        self.__if_counter = 0
        self.__while_counter = 0

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

    #DONE
    def __compile_symbol(self, element: ET.Element, string):
        self.__tokenizer.eat(string)
        new_element = ET.Element(SYMBOL)
        new_element.text = string
        element.append(new_element)
        return string

    #DONE
    def __compile_identifier(self, element: ET.Element):
        token = self.__tokenizer.next_token()
        assert token.get_type() == IDENTIFIER, "Token type is: " + token.get_type() \
                                               + ", Token is: " + token.get_content()
        new_element = ET.Element(IDENTIFIER)
        new_element.text = token.get_content()
        element.append(new_element)
        return token.get_content()

    #DONE
    def __compile_keyword(self, element: ET.Element):
        token = self.__tokenizer.next_token()
        assert token.get_type() == KEYWORD, "Token type is: " + token.get_type() + ", Token is: " + token.get_content()
        new_element = ET.Element(KEYWORD)
        new_element.text = token.get_content()
        element.append(new_element)
        return token.get_content()

    #DONE
    def __compile_class(self, element: ET.Element):
        new_element = ET.Element(CLASS_TAG)
        element.append(new_element)
        self.__compile_keyword(new_element)  # Class keyword
        self.__class_name = self.__compile_identifier(new_element)  # Class var name
        self.__compile_symbol(new_element, START_BLOCK)
        next_token = self.__tokenizer.peek().get_content()
        while next_token == STATIC or next_token == FIELD:
            self.__compile_class_var_dec(new_element)
            next_token = self.__tokenizer.peek().get_content()
        while next_token == CONSTRUCTOR or next_token == FUNCTION or next_token == METHOD:
            self.__compile__subroutine_dec(new_element)
            next_token = self.__tokenizer.peek().get_content()
        self.__compile_symbol(new_element, END_BLOCK)

    #DONE
    def __compile_class_var_dec(self, element):
        new_element = ET.Element(CLASS_VAR_DEC)
        element.append(new_element)
        var_names = []
        kind = self.__compile_keyword(new_element)
        type_of = self.__compile_type(new_element)
        var_names.append(self.__compile_identifier(new_element))
        next_token = self.__tokenizer.peek().get_content()
        while next_token == COMMA:
            self.__compile_symbol(new_element, next_token)
            var_names.append(self.__compile_identifier(new_element))
            next_token = self.__tokenizer.peek().get_content()
        self.__compile_symbol(new_element, SEMICOLON)
        for var in var_names:
            self.__vm_writer.declare_var(var, kind, type_of)

    #DONE
    def __compile_type(self, element):
        next_token = self.__tokenizer.peek()
        if next_token.get_type() == IDENTIFIER:
            return self.__compile_identifier(element)
        elif next_token.get_type() == KEYWORD:
            return self.__compile_keyword(element)
        else:
            raise RuntimeError(
                "Type must be identifier or keyword but token" + next_token.get_content() + "was of type "
                + next_token.get_type())

    #NOT DONE
    def __compile__subroutine_dec(self, element):

        func_name = self.__class_name + '.'
        new_element = ET.Element(SUBROUTINE_DEC)
        element.append(new_element)
        self.__compile_keyword(new_element)
        is_void = False
        if self.__tokenizer.peek().get_content() == VOID:
            is_void = True
            self.__compile_keyword(new_element)
        else:
            self.__compile_type(new_element)
        func_name += self.__compile_identifier(new_element)
        self.__compile_symbol(new_element, OPEN_PAR)
        args = self.__compile_parameter_list(new_element)
        self.__compile_symbol(new_element, CLOSE_PAR)
        # TODO handle methods
        self.__vm_writer.declare_func(func_name, args)

        self.__compile_subroutine_body(new_element, is_void)

    #DONE
    def __compile_parameter_list(self, element):
        new_element = ET.Element(PARAMETER_LIST)
        element.append(new_element)
        if self.__tokenizer.peek().get_content() == CLOSE_PAR:
            new_element.text = '\n'
            return
        args = []
        type_of = self.__compile_type(new_element)
        name = self.__compile_identifier(new_element)
        args.append((name, type_of))
        next_token = self.__tokenizer.peek().get_content()
        while next_token is COMMA:
            self.__compile_symbol(new_element, COMMA)
            type_of = self.__compile_type(new_element)
            name = self.__compile_identifier(new_element)
            next_token = self.__tokenizer.peek().get_content()
            args.append((name, type_of))
        return args

    #DONE
    def __compile_subroutine_body(self, element, is_void=False):
        new_element = ET.Element(SUBROUTINE_BODY)
        element.append(new_element)
        self.__compile_symbol(new_element, START_BLOCK)
        while self.__tokenizer.peek().get_content() == VAR:
            self.__compile_var_dec(new_element)
        self.__compile_statements(new_element)
        self.__compile_symbol(new_element, END_BLOCK)
        if is_void:
            self.__vm_writer.write_push_constant('0')
            self.__vm_writer.write_return()

    #DONE
    def __compile_var_dec(self, element):
        new_element = ET.Element(VAR_DEC)
        element.append(new_element)
        self.__compile_keyword(new_element)
        var_names = []
        type_of = self.__compile_type(new_element)
        var_names.append(self.__compile_identifier(new_element))
        next_token = self.__tokenizer.peek().get_content()
        while next_token == COMMA:
            self.__compile_symbol(new_element, next_token)
            self.__compile_identifier(new_element)
            next_token = self.__tokenizer.peek().get_content()
        self.__compile_symbol(new_element, SEMICOLON)
        for var in var_names:
            self.__vm_writer.declare_var(var, Symbol.LOCAL, type_of)

    #DONE
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

    #NOT DONE
    def __compile_let(self, element):
        new_element = ET.Element(LET_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        var_name = self.__compile_identifier(new_element)
        if self.__tokenizer.peek().get_content() == OPEN_BRACKETS:
            # TODO
            self.__compile_symbol(new_element, OPEN_BRACKETS)
            self.__compile_expression(new_element)
            self.__compile_symbol(new_element, CLOSE_BRACKETS)
        self.__compile_symbol(new_element, EQUALS)
        self.__compile_expression(new_element)
        self.__compile_symbol(new_element, SEMICOLON)
        self.__vm_writer.write_pop_var(var_name)

    #DONE
    def __compile_expression(self, element):
        new_element = ET.Element(EXPRESSION)
        element.append(new_element)
        self.__compile_term(new_element)
        next_token = self.__tokenizer.peek().get_content()
        while next_token in OPS:
            op = self.__compile_symbol(new_element, next_token)
            self.__compile_term(new_element)
            next_token = self.__tokenizer.peek().get_content()
            self.__vm_writer.write_arithmetic(op)

    #DONE
    def __compile_if(self, element):
        new_element = ET.Element(IF_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        self.__compile_symbol(new_element, OPEN_PAR)
        self.__compile_expression(new_element)
        self.__vm_writer.write_arithmetic('!')
        if_end_lable = f"END_LABEL{self.__if_counter}"
        if_false_lable = f"FALSE_LABEL{self.__if_counter}"
        self.__if_counter += 1
        self.__vm_writer.write_if_goto(if_false_lable)
        self.__compile_symbol(new_element, CLOSE_PAR)
        self.__compile_symbol(new_element, START_BLOCK)
        self.__compile_statements(new_element)
        self.__compile_symbol(new_element, END_BLOCK)
        self.__vm_writer.write_goto(if_end_lable)
        if self.__tokenizer.peek().get_content() == ELSE:
            self.__compile_keyword(new_element)
            self.__compile_symbol(new_element, START_BLOCK)
            self.__vm_writer.write_label(if_false_lable)
            self.__compile_statements(new_element)
            self.__compile_symbol(new_element, END_BLOCK)
        self.__vm_writer.write_label(if_end_lable)

    #DONE
    def __compile_while(self, element):
        new_element = ET.Element(WHILE_STATEMENT)
        while_label = f'WHILE_START{self.__while_counter}'
        end_label = f'WHILE_END{self.__while_counter}'
        self.__while_counter += 1
        element.append(new_element)
        self.__compile_keyword(new_element)
        self.__vm_writer.write_label(while_label)
        self.__compile_symbol(new_element, OPEN_PAR)
        self.__compile_expression(new_element)
        self.__vm_writer.write_arithmetic('!')
        self.__vm_writer.write_if_goto(end_label)
        self.__compile_symbol(new_element, CLOSE_PAR)
        self.__compile_symbol(new_element, START_BLOCK)
        self.__compile_statements(new_element)
        self.__vm_writer.write_goto(while_label)
        self.__vm_writer.write_label(end_label)
        self.__compile_symbol(new_element, END_BLOCK)

    #DONE
    def __compile_do(self, element):
        new_element = ET.Element(DO_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        self.__compile_subroutine_call(new_element)
        self.__vm_writer.write_pop_temp()
        self.__compile_symbol(new_element, SEMICOLON)

    #NOT DONE
    def __compile_subroutine_call(self, element):
        new_element = element
        func_name = self.__compile_identifier(new_element)
        # TODO handle methods.
        next_token = self.__tokenizer.peek().get_content()
        if next_token == OPEN_PAR:
            func_name = self.__class_name + '.' + func_name
            self.__compile_symbol(new_element, OPEN_PAR)
            self.__compile_expression_list(new_element)
            self.__compile_symbol(new_element, CLOSE_PAR)
        elif next_token == PERIOD:
            func_name += self.__compile_symbol(new_element, PERIOD)
            func_name += self.__compile_identifier(new_element)
            self.__compile_symbol(new_element, OPEN_PAR)
            self.__compile_expression_list(new_element)
            self.__compile_symbol(new_element, CLOSE_PAR)
        self.__vm_writer.write_call(func_name)

    #DONE
    def __compile_return(self, element):
        new_element = ET.Element(RETURN_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        next_token = self.__tokenizer.peek().get_content()
        if next_token != SEMICOLON:
            self.__compile_expression(new_element)
        self.__compile_symbol(new_element, SEMICOLON)
        self.__vm_writer.write_return()

    #NOT DONE
    def __compile_term(self, element):
        new_element = ET.Element(TERM)
        element.append(new_element)
        next_token = self.__tokenizer.peek()
        if next_token.get_type() == INTEGER_CONSTANT:
            newer_element = ET.Element(INTEGER_CONSTANT)
            constant = self.__tokenizer.next_token().get_content()
            newer_element.text = constant
            new_element.append(newer_element)
            self.__vm_writer.write_push_constant(constant)
        elif next_token.get_type() == STRING_CONSTANT:
            #TODO
            newer_element = ET.Element(STRING_CONSTANT)
            newer_element.text = self.__tokenizer.next_token().get_content()[1:-1]
            new_element.append(newer_element)
        elif next_token.get_content() in KEYWORD_CONSTS:
            self.__compile_keyword(new_element)
            # TODO
        elif next_token.get_type() == IDENTIFIER:
            if next_token.get_next_char() == PERIOD:
                self.__compile_subroutine_call(new_element)
                return

            var_name = self.__compile_identifier(new_element)
            next_token = self.__tokenizer.peek()
            if next_token.get_content() == OPEN_BRACKETS:
                # TODO
                self.__compile_symbol(new_element, OPEN_BRACKETS)
                self.__compile_expression(new_element)
                self.__compile_symbol(new_element, CLOSE_BRACKETS)
            else:
                self.__vm_writer.write_push_var(var_name)
        elif next_token.get_content() in UNARY_OPS:
            op = self.__compile_symbol(new_element, next_token.get_content())
            self.__compile_term(new_element)
            self.__vm_writer.write_arithmetic(op)
        elif next_token.get_content() == OPEN_PAR:
            self.__compile_symbol(new_element, OPEN_PAR)
            self.__compile_expression(new_element)
            self.__compile_symbol(new_element, CLOSE_PAR)

    #DONE
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

    #DONE
    def __is_term(self, token: Token):
        return (token.get_type() == STRING_CONSTANT or token.get_type() == INTEGER_CONSTANT
                or token.get_content() in KEYWORD_CONSTS or token.get_type() == IDENTIFIER
                or token.get_content() in UNARY_OPS or token.get_content() == OPEN_PAR)

import typing
from lxml import etree as ET

from SymbolTable import Symbol
from Tokenizer import *
from VMWriter import VMWriter

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

    def parse(self) -> typing.List[str]:
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
        # tree = ET.ElementTree(new_element[0])

        return self.__vm_writer.get_lines()

    def __compile_symbol(self, element: ET.Element, string):
        self.__tokenizer.eat(string)
        new_element = ET.Element(SYMBOL)
        new_element.text = string
        element.append(new_element)
        return string

    def __compile_identifier(self, element: ET.Element):
        token = self.__tokenizer.next_token()
        assert token.get_type() == IDENTIFIER, "Token type is: " + token.get_type() \
                                               + ", Token is: " + token.get_content()
        new_element = ET.Element(IDENTIFIER)
        new_element.text = token.get_content()
        element.append(new_element)
        return token.get_content()

    def __compile_keyword(self, element: ET.Element):
        token = self.__tokenizer.next_token()
        assert token.get_type() == KEYWORD, "Token type is: " + token.get_type() + ", Token is: " + token.get_content()
        new_element = ET.Element(KEYWORD)
        new_element.text = token.get_content()
        element.append(new_element)
        return token.get_content()

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

    def __compile__subroutine_dec(self, element):
        func_name = self.__class_name + '.'
        new_element = ET.Element(SUBROUTINE_DEC)
        element.append(new_element)
        kind = self.__compile_keyword(new_element)
        if self.__tokenizer.peek().get_content() == VOID:
            type_of = self.__compile_keyword(new_element)
        else:
            type_of = self.__compile_type(new_element)
        func_name += self.__compile_identifier(new_element)
        self.__compile_symbol(new_element, OPEN_PAR)
        args = []
        if kind == METHOD:
            args = ['this']
        args += self.__compile_parameter_list(new_element)
        self.__compile_symbol(new_element, CLOSE_PAR)

        self.__compile_subroutine_body(new_element, func_name, args, type_of, kind)

    def __compile_parameter_list(self, element) -> typing.List[typing.Tuple[str, str]]:
        new_element = ET.Element(PARAMETER_LIST)
        element.append(new_element)
        if self.__tokenizer.peek().get_content() == CLOSE_PAR:
            new_element.text = '\n'
            return []
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

    def __compile_subroutine_body(self, element, func_name, args,  type_of: str, kind: str):
        new_element = ET.Element(SUBROUTINE_BODY)
        element.append(new_element)
        self.__vm_writer.start_subroutine()
        self.__compile_symbol(new_element, START_BLOCK)
        is_void = type_of == VOID
        num_vars = 0
        while self.__tokenizer.peek().get_content() == VAR:
            num_vars += self.__compile_var_dec(new_element)
        self.__vm_writer.declare_func(func_name, args, num_vars)
        if kind == METHOD:
            self.__vm_writer.write_set_this()
        if kind == CONSTRUCTOR:
            self.__vm_writer.write_constructor_alloc()
        self.__compile_statements(new_element, is_void)
        self.__compile_symbol(new_element, END_BLOCK)

    def __compile_var_dec(self, element) -> int:
        new_element = ET.Element(VAR_DEC)
        element.append(new_element)
        self.__compile_keyword(new_element)
        var_names = []
        type_of = self.__compile_type(new_element)
        var_names.append(self.__compile_identifier(new_element))
        next_token = self.__tokenizer.peek().get_content()
        while next_token == COMMA:
            self.__compile_symbol(new_element, next_token)
            var_names.append(self.__compile_identifier(new_element))
            next_token = self.__tokenizer.peek().get_content()
        self.__compile_symbol(new_element, SEMICOLON)
        for var in var_names:
            self.__vm_writer.declare_var(var, Symbol.LOCAL, type_of)
        return len(var_names)

    def __compile_statements(self, element: ET.Element, is_void: bool = False):
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
                self.__compile_return(new_element, is_void)
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
        var_name = self.__compile_identifier(new_element)
        if self.__tokenizer.peek().get_content() == OPEN_BRACKETS:

            self.__vm_writer.write_push_var(var_name)

            self.__compile_symbol(new_element, OPEN_BRACKETS)
            self.__compile_expression(new_element)
            self.__compile_symbol(new_element, CLOSE_BRACKETS)

            self.__vm_writer.write_arithmetic('+')

            self.__compile_symbol(new_element, EQUALS)
            self.__compile_expression(new_element)
            self.__compile_symbol(new_element, SEMICOLON)

            self.__vm_writer.write_access_array()
        else:

            self.__compile_symbol(new_element, EQUALS)
            self.__compile_expression(new_element)
            self.__compile_symbol(new_element, SEMICOLON)
            self.__vm_writer.write_pop_var(var_name)

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

    def __compile_if(self, element):
        new_element = ET.Element(IF_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        self.__compile_symbol(new_element, OPEN_PAR)
        self.__compile_expression(new_element)
        self.__vm_writer.write_arithmetic('~', unary=True)
        if_end_label = f"END_LABEL{self.__if_counter}"
        if_false_label = f"FALSE_LABEL{self.__if_counter}"
        self.__if_counter += 1
        self.__vm_writer.write_if_goto(if_false_label)
        self.__compile_symbol(new_element, CLOSE_PAR)
        self.__compile_symbol(new_element, START_BLOCK)
        self.__compile_statements(new_element)
        self.__compile_symbol(new_element, END_BLOCK)
        self.__vm_writer.write_goto(if_end_label)
        self.__vm_writer.write_label(if_false_label)
        if self.__tokenizer.peek().get_content() == ELSE:
            self.__compile_keyword(new_element)
            self.__compile_symbol(new_element, START_BLOCK)
            self.__compile_statements(new_element)
            self.__compile_symbol(new_element, END_BLOCK)
        self.__vm_writer.write_label(if_end_label)

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

        self.__vm_writer.write_arithmetic('~', unary=True)
        self.__vm_writer.write_if_goto(end_label)

        self.__compile_symbol(new_element, CLOSE_PAR)
        self.__compile_symbol(new_element, START_BLOCK)
        self.__compile_statements(new_element)

        self.__vm_writer.write_goto(while_label)
        self.__vm_writer.write_label(end_label)

        self.__compile_symbol(new_element, END_BLOCK)

    def __compile_do(self, element):
        new_element = ET.Element(DO_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        self.__compile_subroutine_call(new_element)
        self.__vm_writer.write_pop_temp()
        self.__compile_symbol(new_element, SEMICOLON)

    def __compile_subroutine_call(self, element):
        new_element = element
        func_name = self.__compile_identifier(new_element)
        next_token = self.__tokenizer.peek().get_content()
        if next_token == OPEN_PAR:
            func_name = self.__class_name + '.' + func_name
            self.__compile_symbol(new_element, OPEN_PAR)
            self.__vm_writer.write_push_keyword_constant('this')
            num_args = self.__compile_expression_list(new_element) + 1
            self.__compile_symbol(new_element, CLOSE_PAR)
        elif next_token == PERIOD:
            name = func_name
            func_name += self.__compile_symbol(new_element, PERIOD)
            identifier = self.__compile_identifier(new_element)
            func_name += identifier
            self.__compile_symbol(new_element, OPEN_PAR)
            num_args = 0
            type_of_obj = self.__vm_writer.is_object(name)
            if type_of_obj:
                self.__vm_writer.write_push_var(name)
                num_args = 1
                func_name = f'{type_of_obj}.{identifier}'
            num_args += self.__compile_expression_list(new_element)
            self.__compile_symbol(new_element, CLOSE_PAR)
        else:
            raise RuntimeError(f'Something went wrong when calling function: {func_name}')
        self.__vm_writer.write_call(func_name, num_args)

    def __compile_return(self, element, is_void: bool):
        new_element = ET.Element(RETURN_STATEMENT)
        element.append(new_element)
        self.__compile_keyword(new_element)
        next_token = self.__tokenizer.peek().get_content()
        if next_token != SEMICOLON:
            self.__compile_expression(new_element)
        self.__compile_symbol(new_element, SEMICOLON)
        if is_void:
            self.__vm_writer.write_push_int_constant('0')
        self.__vm_writer.write_return()

    def __compile_term(self, element):
        new_element = ET.Element(TERM)
        element.append(new_element)
        next_token = self.__tokenizer.peek()
        if next_token.get_type() == INTEGER_CONSTANT:
            newer_element = ET.Element(INTEGER_CONSTANT)
            constant = self.__tokenizer.next_token().get_content()
            newer_element.text = constant
            new_element.append(newer_element)
            self.__vm_writer.write_push_int_constant(constant)
        elif next_token.get_type() == STRING_CONSTANT:
            newer_element = ET.Element(STRING_CONSTANT)
            newer_element.text = self.__tokenizer.next_token().get_content()[1:-1]
            new_element.append(newer_element)
            self.__vm_writer.write_push_string_constant(next_token.get_content()[1:-1])
        elif next_token.get_content() in KEYWORD_CONSTS:
            self.__compile_keyword(new_element)
            self.__vm_writer.write_push_keyword_constant(next_token.get_content())
        elif next_token.get_type() == IDENTIFIER:
            if next_token.get_next_char() == PERIOD:
                self.__compile_subroutine_call(new_element)
                return
            var_name = self.__compile_identifier(new_element)
            next_token = self.__tokenizer.peek()
            if next_token.get_content() == OPEN_BRACKETS:
                self.__vm_writer.write_push_var(var_name)
                self.__compile_symbol(new_element, OPEN_BRACKETS)
                self.__compile_expression(new_element)
                self.__compile_symbol(new_element, CLOSE_BRACKETS)
                self.__vm_writer.write_arithmetic('+')
                self.__vm_writer.write_get_array()
            else:
                self.__vm_writer.write_push_var(var_name)
        elif next_token.get_content() in UNARY_OPS:
            op = self.__compile_symbol(new_element, next_token.get_content())
            self.__compile_term(new_element)
            self.__vm_writer.write_arithmetic(op, unary=True)
        elif next_token.get_content() == OPEN_PAR:
            self.__compile_symbol(new_element, OPEN_PAR)
            self.__compile_expression(new_element)
            self.__compile_symbol(new_element, CLOSE_PAR)

    def __compile_expression_list(self, element) -> int:
        new_element = ET.Element(EXPRESSION_LIST)
        expression_num = 0
        element.append(new_element)
        next_token = self.__tokenizer.peek()
        if self.__is_term(next_token):
            self.__compile_expression(new_element)
            expression_num += 1
        else:
            new_element.text = '\n'
            return expression_num
        next_token = self.__tokenizer.peek()
        while next_token.get_content() == COMMA:
            self.__compile_symbol(new_element, COMMA)
            self.__compile_expression(new_element)
            expression_num += 1
            next_token = self.__tokenizer.peek()
        return expression_num

    def __is_term(self, token: Token):
        return (token.get_type() == STRING_CONSTANT or token.get_type() == INTEGER_CONSTANT
                or token.get_content() in KEYWORD_CONSTS or token.get_type() == IDENTIFIER
                or token.get_content() in UNARY_OPS or token.get_content() == OPEN_PAR)

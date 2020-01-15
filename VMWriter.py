from SymbolTable import SymbolTable, Symbol
import typing


class VMWriter:

    def __init__(self):
        self.__lines = []
        self.__symbol_table = SymbolTable()

    def get_lines(self) -> typing.List[str]:
        return self.__lines

    def write_push_var(self, name: str):
        var = self.__symbol_table.look_up_symbol(name)
        self.__lines.append(f'push {var.get_segment()} {str(var.get_index())}')

    def write_push_int_constant(self, constant: str):
        self.__lines.append(f'push constant {constant}')

    def write_push_string_constant(self, constant: str):
        self.write_push_int_constant(str(len(constant)))
        self.__lines.append('call String.new 1')
        for char in constant:
            self.write_push_int_constant(str(ord(char)))
            self.__lines.append('call String.appendChar 2')

    def is_object(self, name: str):
        symbol = self.__symbol_table.look_up_symbol(name)
        if symbol:
            return symbol.get_type()

    def write_push_keyword_constant(self, keyword: str):
        if keyword == 'null' or keyword == 'false':
            self.write_push_int_constant('0')
        elif keyword == 'this':
            self.__lines.append('push pointer 0')
        elif keyword == 'true':
            self.write_push_int_constant('0')
            self.write_arithmetic('~', unary=True)
        else:
            raise NameError(f'Unknown keyword constant: {keyword}.')

    def write_constructor_alloc(self):
        size = self.__symbol_table.get_field_num()
        self.write_push_int_constant(str(size))
        self.__lines.append(f'call Memory.alloc 1')
        self.__lines.append('pop pointer 0')

    def write_set_this(self):
        self.__lines.append('push argument 0')
        self.__lines.append('pop pointer 0')

    def write_pop_var(self, var_name: str):
        var = self.__symbol_table.look_up_symbol(var_name)
        assert var is not None, f'Name {var_name} is undefined.'
        self.__lines.append(f'pop {var.get_segment()} {str(var.get_index())}')

    def write_pop_temp(self):
        self.__lines.append('pop temp 0')

    def write_arithmetic(self, op: str, unary=False):
        if op == '~':
            self.__lines.append('not')
        elif op == '+':
            self.__lines.append('add')
        elif op == '-':
            if unary:
                self.__lines.append('neg')
            else:
                self.__lines.append('sub')
        elif op == '&':
            self.__lines.append('and')
        elif op == '|':
            self.__lines.append('or')
        elif op == '<':
            self.__lines.append('lt')
        elif op == '>':
            self.__lines.append('gt')
        elif op == '=':
            self.__lines.append('eq')
        elif op == '*':
            self.__lines.append('call Math.multiply 2')
        elif op == '/':
            self.__lines.append('call Math.divide 2')

    def write_call(self, func_name: str, arg_num: int):
        self.__lines.append(f'call {func_name} {str(arg_num)}')

    def write_if_goto(self, label: str):
        self.__lines.append('if-goto ' + label)

    def write_goto(self, label: str):
        self.__lines.append('goto ' + label)

    def write_label(self, label: str):
        self.__lines.append('label  ' + label)

    def write_return(self):
        self.__lines.append('return')

    def declare_func(self, func_name: str, args: typing.List[typing.Tuple[str, str]], num_vars: int):
        self.__lines.append(f'function {func_name} {num_vars}')
        for arg in args:
            self.__symbol_table.register_symbol(arg[0], arg[1], Symbol.ARGS)

    def declare_var(self, name: str, kind: str, type_of: str):
        self.__symbol_table.register_symbol(name, type_of, kind)

    def write_access_array(self):
        self.__lines.append('pop temp 0')
        self.__lines.append('pop pointer 1')
        self.__lines.append('push temp 0')
        self.__lines.append('pop that 0')

    def write_get_array(self):
        self.__lines.append('pop pointer 1')
        self.__lines.append('push that 0')

    def start_subroutine(self):
        self.__symbol_table.start_subroutine()

from SymbolTable import SymbolTable, Symbol
import typing


class VMWriter:

    def __init__(self):
        self.__lines = []
        self.__symbol_table = SymbolTable()

    def write_push_var(self, name: str):
        var = self.__symbol_table.look_up_symbol(name)
        self.__lines.append('push ' + var.get_segment() + str(var.get_index()))

    def write_push_constant(self, constant: str):
        self.__lines.append('push constant ' + constant)

    def write_pop_var(self, var_name: str):
        var = self.__symbol_table.look_up_symbol(var_name)
        self.__lines.append('pop ' + var.get_segment() + str(var.get_index()))

    def write_pop_temp(self):
        self.__lines.append('pop temp 0')

    def write_arithmetic(self, op: str):  # '*/<>='
        if op == '!':
            self.__lines.append('neg')
        elif op == '+':
            self.__lines.append('add')
        elif op == '-':
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

    def write_call(self, func_name: str, arg_num: int):
        self.__lines.append('call ' + func_name + str(arg_num))

    def write_if_goto(self, label: str):
        self.__lines.append('if-goto ' + label)

    def write_goto(self, label: str):
        self.__lines.append('goto ' + label)

    def write_label(self, label: str):
        self.__lines.append('label  ' + label)

    def write_return(self):
        self.__lines.append('return')

    def declare_func(self, func_name: str, args: typing.List[typing.Tuple[str, str]]):
        self.__lines.append('function' + func_name)
        self.__symbol_table.start_subroutine()
        for arg in args:
            self.__symbol_table.register_symbol(arg[0], arg[1], Symbol.ARGS)

    def declare_var(self, name: str, kind: str, type_of: str):
        self.__symbol_table.register_symbol(name, type_of, kind)

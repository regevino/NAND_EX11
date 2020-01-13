from SymbolTable import SymbolTable, Symbol
import typing


class VMWriter:


    def __init__(self):
        self.__lines = []
        self.__symbol_table = SymbolTable()




    def write_push_var(self, name: str):
        pass


    def write_push_constant(self, constant: str):
        pass
        #TODO

    def write_pop_var(self, var_name: str):
        #TODO
        pass

    def write_pop_temp(self):
        self.__lines.append('pop temp 0')

    def write_arithmetic(self, op: str):
        #TODO
        pass

    def write_call(self, func_name: str):
        #TODO
        pass

    def write_if_goto(self, label: str):
        #TODO
        pass

    def write_goto(self, label: str):
        #TODO
        pass

    def write_label(self, label: str):
        #TODO
        pass

    def write_return(self):
        #TODO
        pass

    def declare_func(self, func_name: str, args: typing.List[typing.Tuple[str, str]]):
        self.__lines.append('function' + func_name)
        self.__symbol_table.start_subroutine()
        for arg in args:
            self.__symbol_table.register_symbol(arg[0], arg[1], Symbol.ARGS)

    def declare_var(self, name: str, kind:str, type_of: str):
        self.__symbol_table.register_symbol(name, type_of, kind)
import typing


class Symbol:
    """
    Represent a single JACK symbol, including name, it's type, kind and index.
    """

    # KIND:
    FIELD = 'field'
    STATIC = 'static'
    LOCAL = 'local'
    ARGS = 'argument'

    def __init__(self, name: str, kind: str, type_of: str, index: int):
        """
        Create new symbol with the following details.
        :param name: name of the symbol.
        :param kind: kind of the symbol.
        :param type_of: type of the symbol.
        :param index: index of the symbol in segment.
        """
        self.__name = name
        self.__type = type_of
        self.__kind = kind
        self.__index = index

    def get_segment(self):
        if self.__kind == Symbol.FIELD:
            return 'this'
        return self.__kind

    def get_index(self):
        return self.__index

    def get_type(self):
        return self.__type


class SymbolTable:
    """
    Represent a symbol table for a jack class and subroutine.
    """

    def __init__(self):
        """
        Create new symbol table.
        """
        self.__class_table = {}
        self.__subroutine_table = {}
        self.__kind_count = {Symbol.ARGS: 0, Symbol.FIELD: 0, Symbol.LOCAL: 0, Symbol.STATIC: 0}


    def register_symbol(self, name: str, type_of: str, kind: str):
        """
        register a new symbol on the table
        :param name:
        :param type_of:
        :param kind:
        :return:
        """
        assert name not in self.__subroutine_table, f'Tried to register name {name}, but it is already registered.'
        new_symbol = Symbol(name, kind, type_of, self.__kind_count[kind])
        self.__kind_count[kind] += 1
        if kind == Symbol.ARGS or kind == Symbol.LOCAL:
            self.__subroutine_table[name] = new_symbol
        elif kind == Symbol.FIELD or kind == Symbol.STATIC:
            self.__class_table[name] = new_symbol
        else:
            raise RuntimeError(f'Unknown kind {kind}')


    def start_subroutine(self):
        """
        start a new subroutine table
        """
        self.__subroutine_table = {}
        self.__kind_count[Symbol.ARGS] = 0
        self.__kind_count[Symbol.LOCAL] = 0

    def look_up_symbol(self, name: str) -> typing.Union[Symbol, None]:
        if name in self.__subroutine_table:
            return self.__subroutine_table[name]
        elif name in self.__class_table:
            return self.__class_table[name]
        else:
            return None

    def get_field_num(self) -> int:
        # print(self.__class_table.keys())
        # exit(1)
        return len(list(filter(lambda x: (self.__class_table[x].get_segment() == 'this'), self.__class_table.keys())))

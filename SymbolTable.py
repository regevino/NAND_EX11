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
        self.KIND_TO_TABLE = {Symbol.STATIC: self.__class_table, Symbol.FIELD: self.__class_table,
                              Symbol.LOCAL: self.__subroutine_table, Symbol.ARGS: self.__subroutine_table}

    def register_symbol(self, name: str, type_of: str, kind: str):
        """
        register a new symbol on the table
        :param name:
        :param type_of:
        :param kind:
        :return:
        """
        # TODO
        assert name not in self.__subroutine_table and name not in self.__class_table
        new_symbol = Symbol(name, type_of, kind, self.__kind_count[kind])
        self.__kind_count[kind] += 1
        self.KIND_TO_TABLE[kind][name] = new_symbol

    def start_subroutine(self):
        """
        start a new subroutine table
        """
        self.__subroutine_table = {}
        self.__kind_count[Symbol.ARGS] = 0
        self.__kind_count[Symbol.LOCAL] = 0

    def look_up_symbol(self, name: str):
        if name in self.__subroutine_table:
            return self.__subroutine_table[name]
        return self.__class_table[name]


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

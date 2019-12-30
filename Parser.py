import xml.etree.ElementTree as ET

from Tokenizer import Tokenizer


class Parser:
    """
    Parse a tokenized jack input into a parse tree.
    """

    def __init__(self, tokenizer: Tokenizer):
        """
        Create a new parser over a token stream of jack input.
        """
        self.__tokenizer = tokenizer

    def parse(self):
        """
        Parse the token stream until there are no more tokens to parse.
        :return: ElementTree representing the parseTree
        """
    # TODO: implement

    def __compile_symbol(self, element: ET.Element, string: str):
        self.__tokenizer.eat(string)
        new_element = ET.Element('Symbol')
        new_element.text = string
        element.append(new_element)

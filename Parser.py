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

    def parse(self) -> ET.ElementTree:
        """
        Parse the token stream until there are no more tokens to parse.
        :return: ElementTree representing the parseTree
        """
        # TODO: implement
        new_element = ET.Element()
        tree = ET.ElementTree(new_element)
        return tree

    def __compile_symbol(self, element: ET.Element):
        token = self.__tokenizer.next_token()
        string = token.get_content()
        new_element = ET.Element('Symbol')
        new_element.text = string
        element.append(new_element)

    def __compile_class(self, element: ET.Element, string: str):
        element.append(ET.Element('class'))
        self.__compile_keyword(element)
        self.__compile_symbol(element)


    def __compile_keyword(self, element: ET.Element):
        token = self.__tokenizer.next_token()
        string = token.get_content()
        new_element = ET.Element('Keyword')
        new_element.text = string
        element.append(new_element)

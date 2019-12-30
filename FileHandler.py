import os

from Parser import Parser
from Tokenizer import Tokenizer


class FileHandler:
    """
    A class that handles the parsing and compilation of .jack files.
    """

    def __init__(self, source_file, source_dir):
        """
        Create a new file handler for a specific .jack file.
        :param source_file:
        :param source_dir:
        """
        self.__tokenizer = Tokenizer(source_file)
        self.__parser = Parser(self.__tokenizer)
        self.__target_file_name = os.path.join(source_dir, source_file[:-4] + '.xml')


    def compile(self):
        """
        compile the .jack file and output the xml result into the relevant file.
        :return:
        """
        element_tree = self.__parser.parse()
        element_tree.write(self.__target_file_name)

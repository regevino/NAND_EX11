"""
A program that compiles jack files.
"""
import os
import sys
from FileHandler import FileHandler

if __name__ == '__main__':
    if len(sys.argv) is not 2:
        print("Bad Parameters!")
        exit(1)
    input_path = sys.argv[1]
    if os.path.isfile(input_path):
        source_dir = os.path.dirname(input_path)
        file_list = [os.path.basename(input_path)]
    else:
        source_dir = input_path
        file_list = os.listdir(source_dir)

    for file in filter(lambda file: file[-5:] == ".jack", file_list):
        handler = FileHandler(file, source_dir)
        handler.compile()


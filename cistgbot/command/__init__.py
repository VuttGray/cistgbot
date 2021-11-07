"""A library that provides bot commands realizations"""

from os import listdir
from os.path import dirname

__package__ = 'cistgbot.command'


# Dynamic import modules
for module in listdir(dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(__package__ + "." + module[:-3], locals(), globals())
del module

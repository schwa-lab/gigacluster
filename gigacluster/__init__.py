from .comparators import *
from .model import *
from .stream import *
from .tokenizer import Tokenizer
from .window import *
import os
DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
CACHE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')

# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/99a_examples-multilabel.ipynb (unless otherwise specified).

__all__ = []

# Cell
import torch, nlp
from transformers import *

from fastai.text.all import *
from fastai.callback.hook import _print_shapes

from ..utils import *
from ..data.core import *
from ..modeling.core import *

logging.set_verbosity_error()
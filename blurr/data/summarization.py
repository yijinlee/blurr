# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01e_data-summarization.ipynb (unless otherwise specified).

__all__ = ['HF_SummarizationInput', 'HF_SummarizationBatchTransform']

# Cell
import ast
from functools import reduce

import torch
from transformers import *
from fastai.text.all import *

from ..utils import *
from .core import *

logging.set_verbosity_error()

# Cell
class HF_SummarizationInput(HF_BaseInput): pass

# Cell
class HF_SummarizationBatchTransform(HF_BatchTransform):
    def __init__(self, hf_arch, hf_tokenizer, max_length=None, padding=True, truncation=True,
                 is_split_into_words=False, n_tok_inps=2, hf_input_return_type=HF_SummarizationInput,
                 tok_kwargs={}, **kwargs):

        super().__init__(hf_arch, hf_tokenizer, max_length=max_length, padding=padding, truncation=truncation,
                         is_split_into_words=is_split_into_words, n_tok_inps=n_tok_inps,
                         hf_input_return_type=hf_input_return_type,
                         tok_kwargs=tok_kwargs.copy(), **kwargs)

    def encodes(self, samples):
        samples = super().encodes(samples)
        if (len(samples[0]) == 1): return samples

        updated_samples = []
        for s in samples:
            s[0]['decoder_input_ids'] = s[1]['input_ids'][:-1].clone()
            s[0]['labels'] = s[1]['input_ids'][1:].clone()
            s[0]['labels'][s[0]['labels'] == self.hf_tokenizer.pad_token_id] = -100

            targ_ids = s[1]['input_ids']

            updated_samples.append((s[0], targ_ids))

        return updated_samples

    def decodes(self, encoded_samples):
        input_ids = encoded_samples['input_ids'] if (isinstance(encoded_samples, dict)) else encoded_samples
        return self.hf_input_return_type(input_ids, hf_tokenizer=self.hf_tokenizer)

# Cell
@typedispatch
def show_batch(x:HF_SummarizationInput, y, samples, dataloaders, ctxs=None, max_n=6, input_trunc_at=None, target_trunc_at=None, **kwargs):
    hf_tokenizer = dataloaders.before_batch[0].hf_tokenizer

    res = L([ (hf_tokenizer.decode(s[0], skip_special_tokens=True)[:input_trunc_at], hf_tokenizer.decode(s[1], skip_special_tokens=True)[:target_trunc_at])
             for s in samples ])

    display_df(pd.DataFrame(res, columns=['text', 'target'])[:max_n])
    return ctxs
# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_data-core.ipynb (unless otherwise specified).

__all__ = ['HF_BaseInput', 'HF_BatchTransform', 'HF_TextBlock']

# Cell
from functools import reduce

import torch, nlp,pdb
from transformers import *
from fastai.text.all import *

from ..utils import *

logging.set_verbosity_error()

# Cell
class HF_BaseInput(TensorBase):
    def show(self, hf_tokenizer, ctx=None, trunc_at=None, **kwargs):
        input_ids = filter(lambda el: el != hf_tokenizer.pad_token_id, self.cpu().numpy())
        decoded_input = str(hf_tokenizer.decode(input_ids, skip_special_tokens=True))[:trunc_at]

        return show_title(decoded_input, ctx=ctx, label='text')

# Cell
class HF_BatchTransform(Transform):
    """Handles everything you need to assemble a mini-batch of inputs and targets, as well as decode the dictionary produced
    as a byproduct of the tokenization process in the `encodes` method.
    """
    def __init__(self, hf_arch, hf_tokenizer, max_length=None, padding=True, truncation=True,
                 is_split_into_words=False, n_tok_inps=1, hf_input_return_type=HF_BaseInput,
                 tok_kwargs={}, **kwargs):

         # gpt2, roberta, bart (and maybe others) tokenizers require a prefix space
        if (hasattr(hf_tokenizer, 'add_prefix_space')): tok_kwargs['add_prefix_space'] = True

        store_attr(self=self, names='hf_arch, hf_tokenizer, max_length, padding, truncation, is_split_into_words')
        store_attr(self=self, names='n_tok_inps, hf_input_return_type, tok_kwargs, kwargs')

    def encodes(self, samples):
        tokenized_samples = [[]] * len(samples)

        samples = L(samples)
        for inp_idx in range(self.n_tok_inps)[::-1]:
            if ((inp_idx+1) > len(samples[0])): continue

            n_seqs =  len(samples[0][inp_idx]) if (is_listy(samples[0][inp_idx]) and not self.is_split_into_words) else 1
            inps = samples.itemgot(inp_idx).items if (n_seqs == 1 ) else list(zip(samples.itemgot(inp_idx,0), samples.itemgot(inp_idx,1)))

            hf_tokenizer, tok_params, tok_kwargs = self._get_tokenization_params(inp_idx)
            tok_d = hf_tokenizer(inps, **tok_params, return_tensors='pt', **tok_kwargs)

            d_keys = tok_d.keys()
            tokenized_samples= [ [{k: tok_d[k][idx]for k in d_keys}] + tokenized_samples[idx]
                                for idx in range(len(samples)) ]

        updated_samples= [ (*tokenized_samples[idx], *sample[self.n_tok_inps:]) for idx, sample in enumerate(samples) ]
        return updated_samples

    def decodes(self, encoded_samples):
        if (isinstance(encoded_samples, dict)):
            return self.hf_input_return_type(encoded_samples['input_ids'], hf_tokenizer=self.hf_tokenizer)
        return encoded_samples


    def _get_tokenization_params(self, inp_idx):
        hf_tokenizer = self.hf_tokenizer if (not is_listy(self.hf_tokenizer)) else self.hf_tokenizer[inp_idx]
        tok_kwargs = self.tok_kwargs if ('input_kwargs' not in self.tok_kwargs) else self.tok_kwargs[inp_idx]

        params_d = {}
        params_d['max_length'] = self.max_length if (not is_listy(self.max_length)) else self.max_length[inp_idx]
        params_d['padding'] = self.padding if (not is_listy(self.padding)) else self.padding[inp_idx]
        params_d['truncation'] = self.truncation if (not is_listy(self.truncation)) else self.truncation[inp_idx]
        params_d['is_split_into_words'] = self.is_split_into_words if (not is_listy(self.is_split_into_words)) else self.is_split_into_words[inp_idx]

        return hf_tokenizer, params_d, tok_kwargs

# Cell
class HF_TextBlock(TransformBlock):
    def __init__(self, hf_arch=None, hf_tokenizer=None, hf_batch_tfm=None,
                 max_length=512, padding=True, truncation=True, is_split_into_words=False,
                 n_tok_inps=1, tok_kwargs={}, hf_input_return_type=HF_BaseInput, dl_type=SortedDL,
                 batch_kwargs={}, **kwargs):

        if(hf_batch_tfm is None and (hf_arch is None or hf_tokenizer is None)):
            raise ValueError("""You must supply both the huggingfrace architecture and tokenizer - or -
                                an instance of HF_BatchTransform""")

        if (hf_batch_tfm is None):
            hf_batch_tfm = HF_BatchTransform(hf_arch, hf_tokenizer,
                                             max_length=max_length, padding=padding, truncation=truncation,
                                             is_split_into_words=is_split_into_words,
                                             n_tok_inps=n_tok_inps, hf_input_return_type=hf_input_return_type,
                                             tok_kwargs=tok_kwargs.copy(), **batch_kwargs.copy())

        return super().__init__(dl_type=dl_type, dls_kwargs={ 'before_batch': [hf_batch_tfm]})

# Cell
@typedispatch
def show_batch(x:HF_BaseInput, y, samples, dataloaders, ctxs=None, max_n=6, trunc_at=None, **kwargs):
    kwargs['hf_tokenizer'] = dataloaders.before_batch[0].hf_tokenizer
    kwargs['trunc_at'] = trunc_at

    if ctxs is None: ctxs = get_empty_df(min(len(samples), max_n))
    ctxs = show_batch[object](x, y, samples, max_n=max_n, ctxs=ctxs, **kwargs)

    display_df(pd.DataFrame(ctxs))
    return ctxs
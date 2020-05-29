from typing import *
import re

import torch
import random
import numpy

from transformers import GPT2LMHeadModel, GPT2Tokenizer


class AI(object):
    """
    The class responsible for handling raw text-generation using a gpt-2 model.
    """
    def __init__(
        self,
        model_path=None,
        use_gpu=True,
    ):
        assert model_path, "No model specified!"

        self.model_path = str(model_path)
        self.use_gpu = torch.cuda.is_available() and use_gpu
        self.dtype = torch.float16
        self.device = torch.device("cuda" if self.use_gpu else "cpu")

        self.max_length: int = 60
        self.beam_searches: int = 1
        self.temperature: float = 0.8
        self.top_k: int = 40
        self.top_p: float = 0.9
        self.repetition_penalty: float = 1.1

        seed = random.randint(0, 2147483647)
        numpy.random.seed(seed)
        torch.random.manual_seed(seed)

        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_path)
        self.eos_token_id = self.tokenizer.encode('<|endoftext|>')[0]

        self.model = GPT2LMHeadModel.from_pretrained(self.model_path)
        self.model.to(self.dtype).to(self.device)
        self.model.eval()

    @property
    def model_info(self) -> str:
        return f'{self.dtype} precision model running on {"gpu" if self.use_gpu else "cpu"}'

    def prime(
        self,
        max_length: int,
        beam_searches: int,
        temperature: float,
        top_k: int,
        top_p: float,
        repetition_penalty: float,
    ):
        self.max_length = max_length
        self.beam_searches = beam_searches
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.repetition_penalty = repetition_penalty

    def encode(
        self,
        text: str
    ):
        return self.tokenizer.encode(text)

    def decode(
        self,
        text: str
    ):
        return self.tokenizer.decode(
            text,
            clean_up_tokenization_spaces=False,
            skip_special_tokens=True,
        )

    def generate(
        self,
        input_ids: Union[List[int], str]
    ):
        if input_ids is str:
            input_ids = self.encode(input_ids)
        assert 0 < len(input_ids) <= 1024, "Input exceeds maximum AI memory!"
        input_len = len(input_ids)
        input_ids = torch.tensor([input_ids], dtype=torch.long, device=self.device)
        result = self.model.generate(
            input_ids=input_ids,
            min_length=input_len,
            max_length=input_len + self.max_length,
            do_sample=True,
            num_beams=self.beam_searches,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            repetition_penalty=self.repetition_penalty,
            pad_token_id=self.eos_token_id,
            eos_token_id=self.eos_token_id,
        )
        return self.decode(result[0][input_len:])

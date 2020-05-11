import os
import re

import torch
import random
import numpy

from transformers import GPT2LMHeadModel, GPT2Tokenizer

from aiventure.ai.sample import sample_sequence


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

        seed = random.randint(0, 2147483647)
        numpy.random.seed(seed)
        torch.random.manual_seed(seed)

        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_path)
        self.model = GPT2LMHeadModel.from_pretrained(self.model_path)
        self.model.to(self.dtype).to(self.device)
        self.model.eval()

    @property
    def model_info(self) -> str:
        return f'{self.dtype} precision model running on {"gpu" if self.use_gpu else "cpu"}'

    def generate_raw(
            self,
            text: str,
            length: int,
            batch_size: int,
            temperature: float,
            top_k: float,
            top_p: float,
            rep_pen: float,
    ) -> str:
        """
        Generates a raw, unaltered string from a single input.
        :param text: The text to use to generate the string.
        :param length: The maximum length of string to generate.
        :param batch_size: The number of strings to generate in sequence.
        :param temperature: The temperature used by the sampling algorithm.
        :param top_k: The top_k value used by the sampling algorithm.
        :param top_p: The top_p value used by the sampling algorithm.
        :param rep_pen: The repetition penalty. 1.0 is no penalty.
        :return: An unaltered string generated by the AI.
        """
        tokens = self.tokenizer.encode(text)
        result = sample_sequence(
            model=self.model,
            context=tokens,
            device=self.device,
            length=length,
            batch_size=batch_size,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            rep_pen=rep_pen,
        )
        result = result[:, len(tokens):].tolist()
        text = ""
        for i in range(batch_size):
            text += self.tokenizer.decode(
                result[i],
                clean_up_tokenization_spaces=False,
                skip_special_tokens=True,
            )
        return text

    def generate(
            self,
            text: str = None,
            length: int = None,
            batch_size: int = None,
            temperature: float = None,
            top_k: float = None,
            top_p: float = None,
            rep_pen: float = None,
    ) -> str:
        """
        Generates a preprocessed string from the AI.
        :param text: The text to use to generate the string.
        :param length: The maximum length of string to generate.
        :param batch_size: The number of strings to generate in sequence.
        :param temperature: The temperature used by the sampling algorithm.
        :param top_k: The top_k value used by the sampling algorithm.
        :param top_p: The top_p value used by the sampling algorithm.
        :param rep_pen: The repetition penalty. 1.0 is no penalty.
        :return: An unaltered string generated by the AI.
        """
        text = self.generate_raw(
            text,
            length=length,
            batch_size=batch_size,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            rep_pen=rep_pen,
        )
        text = text.split("<|endoftext|>")[0]
        text = re.sub(r"\n+", '\n', text)
        text = re.sub(r"[ \t]+", ' ', text)
        text = text.strip()
        return text
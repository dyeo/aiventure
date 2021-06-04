from typing import *
import os
import json

import torch
import random
import numpy

from transformers import GPT2LMHeadModel, AutoTokenizer, GPTNeoForCausalLM

model_types = {
    "": GPT2LMHeadModel,
    "neo": GPTNeoForCausalLM 
} # type: Dict[str, Type]

model_memory_lengths = {
    "": lambda c: c["n_positions"],
    "neo": lambda c: c["max_position_embeddings"]
}

class AI(object):
    """
    The class responsible for handling raw text-generation using a LM model.
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
        self.ttype = torch.long
        self.device = torch.device("cuda" if self.use_gpu else "cpu")

        self.max_length: int = 60
        self.beam_searches: int = 1
        self.temperature: float = 0.8
        self.top_k: int = 40
        self.top_p: float = 0.9
        self.repetition_penalty: float = 1.1

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.eos_token_id = self.tokenizer.encode("<|endoftext|>")[0]
        
        self.reseed()
        
        model_key = ""
        with open(os.path.join(str(self.model_path), "config.json")) as f:
            model_config = json.load(f)
        neo_in_path = "gpt-neo" in str(model_path).lower()
        neo_in_architectures = "architectures" in model_config and "GPTNeoForCausalLM" in model_config["architectures"]
        neo_in_model_type = "model_type" in model_config and "gpt_neo" == model_config["model_type"]
        model_key = "neo" if neo_in_path or neo_in_architectures or neo_in_model_type else model_key

        self.max_memory: int = model_memory_lengths[model_key](model_config)
        self.model_type = model_types[model_key]
        
        try:
            self.model = self.model_type.from_pretrained(self.model_path)
            self.model.to(self.dtype).to(self.device)
            self.model.eval()
        except Exception as e:
            print("")

    @property
    def model_info(self) -> str:
        return "; ".join([
            "gpu" if self.use_gpu else "cpu",
            str(self.dtype)[6:],
            f"{self.max_memory} tokens"
        ])

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

    def reseed(self):
        seed = random.randint(0, 2147483647)
        numpy.random.seed(seed)
        torch.random.manual_seed(seed)

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
        self.reseed()      
        if isinstance(input_ids, str):
            input_ids = self.encode(input_ids)
        assert 0 < len(input_ids) <= self.max_memory, "Input exceeds maximum AI memory!"
        input_len = len(input_ids)
        input_ids = torch.tensor([input_ids], dtype=self.ttype, device=self.device)
        result = self.model.generate(
            input_ids=input_ids,
            min_length=input_len,
            max_length=input_len + self.max_length,
            do_sample=(self.beam_searches > 0),
            num_beams=max(self.beam_searches, 1),
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            repetition_penalty=self.repetition_penalty,
            pad_token_id=self.eos_token_id,
            eos_token_id=self.eos_token_id,
        )
        return self.decode(result[0][input_len:])
        

"""
    Original code by TaeHwan Jung (graykode)
    Modified by Dan Yeomans (dyeo)
    top_k and top_p sampling by Thomas Wolf (thomwolf)
    Original Paper and repository here : https://github.com/openai/gpt-2
    GPT2 Pytorch Model : https://github.com/huggingface/pytorch-pretrained-BERT
"""

import torch
import torch.nn.functional as F

from transformers.modeling_utils import top_k_top_p_filtering


def sample_sequence(
        model,
        context,
        device="cuda",
        length=60,
        batch_size=1,
        temperature=1,
        top_k=0,
        top_p=0.9,
        rep_pen=1.0,
):
    context = torch.tensor(context, device=device, dtype=torch.long)
    context = context.unsqueeze(0).repeat(batch_size, 1)
    next = context
    output = context
    past = None
    with torch.no_grad():
        for i in range(length):
            logits, past = model(next, past=past)
            logits = logits[:, -1, :] / (temperature if temperature > 0 else 1.0)
            for j in range(batch_size):
                for k in set(output[j].tolist()):
                    logits[j, k] /= rep_pen
            logits = top_k_top_p_filtering(logits, top_k=top_k, top_p=top_p, filter_value=-float("Inf"))
            log_probs = F.softmax(logits, dim=-1)
            next = torch.multinomial(log_probs, num_samples=1)
            output = torch.cat((output, next), dim=1)
    return output

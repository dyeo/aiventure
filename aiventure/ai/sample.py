"""
    Original code by TaeHwan Jung (graykode)
    Modified by Dan Yeomans (dyeo)
    top_k and top_p sampling by Thomas Wolf (thomwolf)
    Original Paper and repository here : https://github.com/openai/gpt-2
    GPT2 Pytorch Model : https://github.com/huggingface/pytorch-pretrained-BERT
"""

import torch
import torch.nn.functional as F


def top_k_logits(logits, k, filter_value=-float("Inf")):
    if k == 0:
        return logits
    indices_to_remove = logits < torch.topk(logits, k)[0][..., -1, None]
    logits[indices_to_remove] = filter_value
    return logits


def top_p_logits(logits, p, filter_value=-float("Inf")):
    if p == 0:
        return logits
    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
    # Remove tokens with cumulative probability above the threshold
    sorted_indices_to_remove = cumulative_probs > p
    # Shift the indices to the right to keep also the first token above the threshold
    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
    sorted_indices_to_remove[..., 0] = 0
    # scatter sorted tensors to original indexing
    indices_to_remove = sorted_indices_to_remove.scatter(
        dim=1, index=sorted_indices, src=sorted_indices_to_remove
    )
    logits[indices_to_remove] = filter_value
    return logits


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
            logits = top_k_logits(logits, k=top_k)
            logits = top_p_logits(logits, p=top_p)
            log_probs = F.softmax(logits, dim=-1)
            next = torch.multinomial(log_probs, num_samples=1)
            output = torch.cat((output, next), dim=1)
    return output

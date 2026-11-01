"""Exact JSON UTF-8 byte packing. This is not a model-token estimator."""
import json
from dataclasses import asdict
from .contracts import Recall


def encode(packet: dict) -> bytes:
    return json.dumps(packet,ensure_ascii=False,separators=(',',':')).encode('utf-8')


def pack(recalls: list[Recall], budget_bytes: int) -> dict:
    if type(budget_bytes) is not int or budget_bytes < 0:
        raise ValueError('budget_bytes must be a nonnegative integer')
    packet = {'kind':'memory_data','items':[], 'considered':len(recalls), 'omitted':len(recalls)}
    if len(encode(packet)) > budget_bytes:
        raise ValueError('budget is smaller than the empty packet wrapper')
    for recall in recalls:
        item = asdict(recall)
        proposal = {**packet,'items':packet['items']+[item], 'omitted':packet['omitted']-1}
        if len(encode(proposal)) <= budget_bytes:
            packet = proposal
    return packet

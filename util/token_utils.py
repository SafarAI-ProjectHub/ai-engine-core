from typing import Iterable, List

import tiktoken 

def _get_encoding(model: str) -> tiktoken.Encoding:
    """ Resolve the tiktoken encoding for a model, falling back to gbt-4o-mini."""

    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.encoding_for_model("gpt-4o-mini")

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count how many tokens a single text would consume for the given model"""

    if not isinstance(text, str):
        raise TypeError(f"text must be a string, got {type(text)}")

    encoding = _get_encoding(model)
    return len(encoding.encode(text))


def count_tokens_batch(texts: Iterable[str], model: str = "gpt-4o-mini") -> List[int]:
    """count tokens for each text in an iterable. returns a list of counts in order."""

    encoding = _get_encoding(model)
    counts: list[int] = []

    for idx, text in enumerate(texts):
        if not isinstance(text, str):
            raise TypeError(f"text at index {idx} must be a string, got {type(text)}")
        counts.append(len(encoding.encode(text)))
    return counts
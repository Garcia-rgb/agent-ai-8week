import hashlib
import math
import re

DIMENSION = 384


def tokenize(text: str) -> list[str]:
    """Tokenize Chinese characters and alphanumeric words without external models."""
    return re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9_]+", text.lower())


def local_embedding(text: str, dimension: int = DIMENSION) -> list[float]:
    """Create a deterministic hashing embedding for free local development.

    It is intentionally simple. Configure a hosted embedding model before production.
    """
    vector = [0.0] * dimension
    for token in tokenize(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=False))

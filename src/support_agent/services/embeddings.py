import hashlib
import math
import re

DIMENSION = 384


def tokenize(text: str) -> list[str]:
    """不依赖外部模型，将中文按单字、英文和数字按连续单词切分。"""
    return re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9_]+", text.lower())


def local_embedding(text: str, dimension: int = DIMENSION) -> list[float]:
    """生成结果稳定的哈希向量，供免费的本地开发和流程演示使用。

    这只是为了跑通 RAG 流程，并不能真正理解语义；生产环境应接入正式的
    Embedding 模型。
    """
    vector = [0.0] * dimension
    for token in tokenize(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        # 同一个词每次都会落到同一个位置，因此测试结果可重复。
        bucket = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign
    # 归一化后，向量点积就可以直接作为余弦相似度。
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=False))

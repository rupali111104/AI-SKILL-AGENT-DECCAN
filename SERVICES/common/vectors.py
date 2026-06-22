import hashlib
import math
import re
from typing import List


VECTOR_SIZE = 384


def create_embedding(text: str) -> List[float]:
    tokens = re.findall(r"[a-zA-Z0-9+#.]+", (text or "").lower())
    vector = [0.0] * VECTOR_SIZE

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % VECTOR_SIZE
        sign = 1 if digest[4] % 2 == 0 else -1
        vector[index] += sign

    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector

    return [value / magnitude for value in vector]


def cosine_similarity(embedding1, embedding2) -> float:
    if not embedding1 or not embedding2:
        return 0.0

    dot_product = sum(value1 * value2 for value1, value2 in zip(embedding1, embedding2))
    magnitude1 = math.sqrt(sum(value * value for value in embedding1))
    magnitude2 = math.sqrt(sum(value * value for value in embedding2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)

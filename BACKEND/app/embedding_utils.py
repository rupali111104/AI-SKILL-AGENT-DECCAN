from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embedding(text: str):
    embedding = model.encode(text)
    return embedding.tolist()


def calculate_cosine_similarity(embedding1, embedding2) -> float:
    emb1 = np.array(embedding1).reshape(1, -1)
    emb2 = np.array(embedding2).reshape(1, -1)

    score = cosine_similarity(emb1, emb2)[0][0]
    return float(score)

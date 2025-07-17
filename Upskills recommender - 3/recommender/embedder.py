# utils/embedder.py

from sentence_transformers import SentenceTransformer

# Load model once and reuse
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """
    Returns the embedding tensor for a given input string.
    """
    return model.encode(text, convert_to_tensor=True)


def get_similarity(text1, text2):
    """
    Computes cosine similarity between two texts using sentence embeddings.
    """
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    from sentence_transformers.util import pytorch_cos_sim
    return pytorch_cos_sim(emb1, emb2)[0][0].item()

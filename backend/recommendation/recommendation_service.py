import pickle
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "product_embeddings.pkl")



def load_data():
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing file: {file_path}")

    with open(file_path, "rb") as f:
        data = pickle.load(f)

    return data



def get_text_recommendations(text, top_k=5):
    data = load_data()
    df = data["products"]
    embeddings = data["embeddings"]

    query_vec = model.encode([text])

    scores = cosine_similarity(query_vec, embeddings)[0]

    best_idx = np.argsort(scores)[::-1][:top_k]

    return [df.iloc[i].to_dict() for i in best_idx]


def get_similar_products(product_id, top_k=5):
    data = load_data()
    df = data["products"]
    embeddings = data["embeddings"]

    idx_list = df.index[df["id"] == product_id]

    if len(idx_list) == 0:
        return []

    idx = idx_list[0]

    scores = cosine_similarity([embeddings[idx]], embeddings)[0]
    sorted_idx = np.argsort(scores)[::-1]

    results = []
    for i in sorted_idx:
        if df.iloc[i]["id"] == product_id:
            continue

        results.append(df.iloc[i].to_dict())

        if len(results) == top_k:
            break

    return results



def get_hybrid_recommendations(
    text="",
    cart_items=None,
    wishlist_items=None,
    order_items=None,
    history_items=None,
    top_k=10
):
    data = load_data()
    df = data["products"]
    embeddings = data["embeddings"]

    score_boost = np.zeros(len(df))

    # 1. AI TEXT SEARCH (MAIN SIGNAL)
    if text:
        query_vec = model.encode([text])
        scores = cosine_similarity(query_vec, embeddings)[0]
        score_boost += scores * 2.0  # highest weight

    # 2. CART BOOST
    if cart_items:
        for pid in cart_items:
            idx = df.index[df["id"] == pid]
            if len(idx):
                score_boost += cosine_similarity([embeddings[idx[0]]], embeddings)[0] * 1.5

    # 3. WISHLIST BOOST
    if wishlist_items:
        for pid in wishlist_items:
            idx = df.index[df["id"] == pid]
            if len(idx):
                score_boost += cosine_similarity([embeddings[idx[0]]], embeddings)[0] * 1.3

    # 4. ORDER HISTORY BOOST
    if order_items:
        for pid in order_items:
            idx = df.index[df["id"] == pid]
            if len(idx):
                score_boost += cosine_similarity([embeddings[idx[0]]], embeddings)[0] * 1.8

    # 5. RECENTLY VIEWED BOOST
    if history_items:
        for pid in history_items:
            idx = df.index[df["id"] == pid]
            if len(idx):
                score_boost += cosine_similarity([embeddings[idx[0]]], embeddings)[0] * 1.2

    best_idx = np.argsort(score_boost)[::-1][:top_k]

    return [df.iloc[i].to_dict() for i in best_idx]
import os
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, CrossEncoder

# Confirmed against the real vectorizer.py — this is the right model.
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "all-MiniLM-L6-v2")
RERANK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

app = FastAPI(title="NexaForge Model Service")

_embed_model = None
_reranker = None


def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model


def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANK_MODEL_NAME)
    return _reranker


class EmbedRequest(BaseModel):
    # Always a list, even for one piece of text — remote_model.py wraps
    # single strings into a one-item list before sending. This lets
    # ingestion (which embeds hundreds of chunks at once) send them all
    # in a single HTTP call instead of one call per chunk.
    texts: list[str]


class RerankRequest(BaseModel):
    query: str
    candidates: list[str]


@app.get("/")
def health():
    return {"status": "ok", "embed_model": EMBED_MODEL_NAME, "rerank_model": RERANK_MODEL_NAME}


@app.post("/embed")
def embed(req: EmbedRequest):
    model = get_embed_model()
    vectors = model.encode(req.texts, show_progress_bar=False).tolist()
    return {"embeddings": vectors}


@app.post("/rerank")
def rerank(req: RerankRequest):
    reranker = get_reranker()
    pairs = [[req.query, c] for c in req.candidates]
    scores = reranker.predict(pairs)
    return {"scores": [float(s) for s in scores]}

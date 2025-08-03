from pydantic_ai import RunContext
import faiss
from Agents.models import GradingAgentDeps
from Agents.rag_pipeline import TransformerEmbedder,SentenceSplitter
from sklearn.pipeline import Pipeline
import numpy as np
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

def rag_tool(ctx: RunContext[GradingAgentDeps], query: str) -> str:
    logger.info(f"RAG tool invoked for exam_id={ctx.deps.exam_id}, user_id={ctx.deps.user_id}")
    index_path = f"faiss_indexes/{ctx.deps.exam_id}_{ctx.deps.user_id}.faiss"
    logger.info(f"Loading FAISS index from {index_path}")
    try:
        index = faiss.read_index(index_path)
    except Exception as e:
        logger.error(f"faiss.read_index error: {e}")
    chunks_doc = ctx.deps.db["Chunks"].find_one({
        "exam_id": ObjectId(ctx.deps.exam_id),
        "user_id": ObjectId(ctx.deps.user_id)
    })
    if not chunks_doc or "chunks" not in chunks_doc:
        logger.warning("No chunks found for the given exam_id and user_id.")
        return ""
    chunks = chunks_doc["chunks"]
    logger.info(f"Loaded {len(chunks)} chunks from database.")
    pipeline = Pipeline([
        ('split', SentenceSplitter()),
        ('embed', TransformerEmbedder())
    ])
    logger.info("Generating embedding for query.")
    query_embedding = pipeline.transform([query])
    top_k = 3
    logger.info(f"Searching top {top_k} similar chunks in FAISS index.")
    D, I = index.search(query_embedding.astype(np.float32), top_k)
    results = [chunks[i] for i in I[0] if i < len(chunks)]
    logger.info(f"Found {len(results)} relevant chunks.")
    context = '\n\n\n'.join(results)
    return context
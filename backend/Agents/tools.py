from pydantic_ai import RunContext
import faiss
from Agents.models import GradingAgentDeps
from Agents.rag_pipeline import TransformerEmbedder,SentenceSplitter
from sklearn.pipeline import Pipeline
import numpy as np

def rag_tool(query: str,ctx: RunContext[GradingAgentDeps]):
    index = faiss.read_index(f"faiss_indexes/{ctx.deps.exam_name}_{ctx.deps.user_id}.faiss")
    chunks = ctx.deps.db["Chunks"].find_one({
        "exam_name": ctx.deps.exam_name,
        "user_id": ctx.deps.exam_name
    })
    pipeline = Pipeline([
        ('split',SentenceSplitter()),
        ('embed',TransformerEmbedder())
    ])
    query_embedding = pipeline.transform([query])
    top_k = 3
    D,I = index.search(query_embedding.astype(np.float32),top_k)
    results = [chunks[i] for i in I[0]]
    context = '\n\n\n'.join(results)
    return context
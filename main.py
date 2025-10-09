import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Fallback to transformers LLM if OpenAI not available
try:
    from langchain.llms import HuggingFacePipeline
    from transformers import pipeline, AutoTokenizer
except Exception:
    HuggingFacePipeline = None
    pipeline = None
    AutoTokenizer = None


app = FastAPI(title="GenAI-Powered Healthcare Q&A System")

DB_PATH = os.environ.get("DB_PATH", "./faiss_index")
EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
HF_MODEL = os.environ.get("HF_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
# HF LLM model (used for text generation fallback). Default to small gpt2 for local CPU use.
HF_LLM_MODEL = os.environ.get("HF_LLM_MODEL", "gpt2")

class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3


# Load embeddings and vectorstore at startup
@app.on_event("startup")
def load_vectorstore():
    global vectorstore, embeddings
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    if not os.path.exists(DB_PATH):
        raise RuntimeError(f"Vector DB not found at {DB_PATH}. Run the data prep script first.")
    # The FAISS serialization uses a pickle under the hood. This flag must be
    # enabled to allow loading local, trusted indexes. Only enable this if
    # you trust the files in `DB_PATH` (we created them locally in this repo).
    vectorstore = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
    print("Vectorstore loaded.")


def get_llm():
    # Prefer OpenAI if API key present
    if os.environ.get("OPENAI_API_KEY"):
        return OpenAI(temperature=0)
    # Fallback: use a small HF model via transformers pipeline
    if HuggingFacePipeline and pipeline is not None and AutoTokenizer is not None:
        model_name = os.environ.get("HF_LLM_MODEL", HF_LLM_MODEL)
        # Load tokenizer and create a generation pipeline with safe defaults.
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Ensure pad token exists (some models like GPT2 don't have one)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id

        gen_pipe = pipeline(
            "text-generation",
            model=model_name,
            tokenizer=tokenizer,
            device=-1,
            # prefer max_new_tokens over max_length to avoid conflicts with input length
            max_new_tokens=int(os.environ.get("HF_MAX_NEW_TOKENS", 128)),
        )
        return HuggingFacePipeline(pipeline=gen_pipe)
    raise RuntimeError("No LLM backend available. Set OPENAI_API_KEY or install transformers and provide HF_MODEL.")


@app.post("/ask")
def ask(req: AskRequest):
    try:
        llm = get_llm()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Build RetrievalQA
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever(search_kwargs={"k": req.top_k}))
    answer = qa.run(req.question)
    return {"answer": answer}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

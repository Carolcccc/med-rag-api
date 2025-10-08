import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# LangChain provides embeddings wrappers; use SentenceTransformer via the embeddings API
from langchain.embeddings import SentenceTransformerEmbeddings
# FAISS vectorstore is provided by langchain.vectorstores
from langchain.vectorstores import FAISS

# --- Configuration Parameters ---
# Folder containing raw documents
DATA_PATH = "./data" 
# Folder where the resulting vector database will be saved
DB_PATH = "./faiss_index" 

# A small, efficient open-source embedding model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def create_vector_database():
    """
    Executes the entire RAG data preparation pipeline: Load -> Split -> Embed -> Store.
    This simulates the data prep work often done in environments like Databricks.
    """
    print("--- Step 1: Loading Documents ---")
    documents = []
    
    # Check if the data folder exists and iterate through .txt files
    if not os.path.exists(DATA_PATH):
        print(f"Error: Directory '{DATA_PATH}' not found. Please create it and add .txt files.")
        return

    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".txt"):
            file_path = os.path.join(DATA_PATH, filename)
            print(f"Loading document: {file_path}")
            # Use TextLoader to load the file content
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                documents.extend(loader.load())
            except Exception as e:
                print(f"Could not load {file_path}: {e}")
                continue

    if not documents:
        print(f"Error: No .txt files were loaded from {DATA_PATH}. Please ensure you have added content.")
        return

    print(f"Total documents loaded: {len(documents)}")

    print("\n--- Step 2: Document Chunking ---")
    # Set up the splitter: split into 500-character chunks with 50-character overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len
    )
    texts = text_splitter.split_documents(documents)
    print(f"Documents were split into {len(texts)} total chunks.")

    print("\n--- Step 3: Generating Embeddings ---")
    # Load the Sentence Transformer model to calculate vectors for the chunks
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    print("\n--- Step 4: Storing in FAISS Vector Store ---")
    # Create the FAISS vector database and save it locally
    # This asset will be used by the FastAPI service
    db = FAISS.from_documents(texts, embeddings)
    db.save_local(DB_PATH)
    
    print(f"✅ Vector database successfully created and saved to folder: {DB_PATH}/")
    print("Data preparation phase completed.")


if __name__ == "__main__":
    create_vector_database()
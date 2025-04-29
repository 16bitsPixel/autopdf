import chromadb
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from embedding import get_embedding_function
import os

# --- Initialize Models and Database ---
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

CHROMA_PATH = "chroma"

# --- Helper Functions ---
def split_documents(documents: list[Document]):
    """
    Split documents into smaller chunks using a text splitter.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: list[Document]):
    """
    Add chunks to a Chroma database.
    """
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function(),
    )

    # calculate Page IDs for each chunk
    chunks_with_ids = calculate_chunk_ids(chunks)

    # add/update documents
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # add documents that don't exist in DB
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adding {len(new_chunks)} new chunks to DB.")
        new_chunks_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunks_ids)
    else:
        print("No new chunks to add.")

def calculate_chunk_ids(chunks):
    """
    Calculate unique chunk IDs based on source and page number.
    """
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # if page ID is same as last, increment index
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # calculate chunk ID
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # add to metadata
        chunk.metadata["id"] = chunk_id

    return chunks

def delete_texts_from_chroma(source_id: str):
    """Delete all documents from ChromaDB by source ID."""
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function(),
    )

    # Fetch all documents and their metadata
    existing_items = db.get(include=["documents", "metadatas"])

    # Collect ids for documents that match the source_id in metadata
    existing_ids = set()
    for i, metadata in enumerate(existing_items["metadatas"]):
        if metadata.get("source") == source_id:
            existing_ids.add(existing_items["ids"][i])  # We want to collect the id (document ID)

    # print existing_ids for debugging
    print(f"Existing IDs for source ID {source_id}: {existing_ids}")

    # If we found any documents for the source_id, delete them
    if existing_ids:
        db.delete(ids=list(existing_ids))  # Now delete by ids
        print(f"Deleted {len(existing_ids)} documents from ChromaDB for source ID: {source_id}")
    else:
        print(f"No documents found for source ID: {source_id}")

def retrieve_similar_documents(query, k=5):
    """Retrieve top-k similar documents from Chroma DB."""
    query_embedding = embedding_model.encode([query])
    results = collection.query(query_embeddings=query_embedding, n_results=k)

    # Ensure results contain 'documents' and 'metadatas'
    documents = results.get('documents', [])
    print(documents)
    metadatas = results.get('metadatas', [])

    # If no documents are found, return empty lists
    if not documents:
        return [], []

    # Return documents and their corresponding metadata
    return documents, metadatas

def answer_question(question, context):
    """Use QA model to answer a question given the context."""
    result = qa_pipeline(question=question, context=context)
    return result.get('answer', 'No answer found.')

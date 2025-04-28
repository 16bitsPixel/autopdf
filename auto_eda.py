import os
import re
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm
from transformers import pipeline
from db import collection

def fetch_page_texts(collection):
    """
    Fetches the text from all pages in the MongoDB collection.
    """
    documents = collection.find({})
    all_texts = []
    for doc in documents:
        pages = doc.get("pages", [])
        for page in pages:
            text = page.get("text", "")
            if text.strip():
                all_texts.append(text.strip())
    return all_texts

def split_into_chunks(text, chunk_size=512):
    """
    Splits the text into chunks of a specified size.
    """
    text = re.sub(r'\s+', ' ', text.strip())  # Normalize whitespace
    words = text.split(' ')
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def perform_ner(texts, model_name="dslim/bert-base-NER", chunk_size=512):

    """
    Performs Named Entity Recognition (NER) on the provided texts using a specified model.
    """
    ner_pipeline = pipeline("ner", model=model_name, grouped_entities=True)
    all_entities = []
    for text in tqdm(texts, desc="Performing NER"):
        chunks = split_into_chunks(text, chunk_size=chunk_size)
        for chunk in chunks:
            if chunk.strip() == "":
                continue
            try:
                entities = ner_pipeline(chunk)
                all_entities.extend([entity['word'] for entity in entities])
            except Exception as e:
                print(f"Error processing chunk: {chunk[:30]}... Error: {e}")
    return all_entities

def plot_top_entities(entities, top_n=10, output_dir="outputs"):
    """
    Create a bar plot of the top N extracted entities.
    """
    counter = Counter(entities)
    labels, values = zip(*counter.most_common(top_n))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.title(f'Top {top_n} Named Entities')
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'top_entities.png')
    plt.savefig(output_path)
    plt.show()
    print(f"Figure saved to {output_path}")

def perform_eda_on_documents(documents, chunk_size=400):
    """
    Perform EDA on a list of MongoDB document objects directly.
    """
    # Extract text from pages
    all_texts = []
    for doc in documents:
        pages = doc.get("pages", [])
        for page in pages:
            text = page.get("text", "")
            if text.strip():
                all_texts.append(text.strip())

    if not all_texts:
        print("No text found in selected documents.")
        return

    # Perform NER
    entities = perform_ner(all_texts, chunk_size=chunk_size)
    if not entities:
        print("No entities extracted.")
        return

    # Plot the results
    plot_top_entities(entities)

def main():
    CHUNK_SIZE = 400  # Words per chunk

    # --- Fetch data ---
    texts = fetch_page_texts(collection)
    if not texts:
        print("No text found in the database.")
        return

    # --- Perform NER ---
    entities = perform_ner(texts, chunk_size=CHUNK_SIZE)
    if not entities:
        print("No entities extracted.")
        return

    # --- Plot Results ---
    plot_top_entities(entities)

if __name__ == "__main__":
    main()

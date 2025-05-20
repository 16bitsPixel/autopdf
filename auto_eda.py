# auto_full_eda.py

import os
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from tqdm import tqdm
from bson import ObjectId
import pandas as pd

from transformers import pipeline
from db import collection

from sklearn.feature_extraction.text import CountVectorizer

# summarizer model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# --- Helper Functions ---

def fetch_document_text(document_id):
    """
    Fetch the text from a single document by ID.
    """
    doc = collection.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise ValueError(f"No document found with id: {document_id}")
    
    all_texts = []
    pages = doc.get("pages", [])
    for page in pages:
        text = page.get("text", "")
        if text.strip():
            all_texts.append(text.strip())
    return all_texts

def clean_texts(texts):
    """
    Basic cleaning: remove extra whitespace.
    """
    cleaned = [re.sub(r'\s+', ' ', text.strip()) for text in texts]
    return cleaned

def plot_word_frequency(texts, top_n=20, output_dir="outputs"):
    """
    Plot most common words.
    """
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(texts)
    word_counts = X.sum(axis=0).A1
    vocab = vectorizer.get_feature_names_out()
    
    counter = Counter(dict(zip(vocab, word_counts)))
    labels, values = zip(*counter.most_common(top_n))

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='coral')
    plt.xticks(rotation=45, ha='right')
    plt.title(f'Top {top_n} Words')
    plt.tight_layout()
    save_plot('top_words.svg', output_dir)

def plot_wordcloud(texts, output_dir="outputs"):
    """
    Generate a WordCloud.
    """
    full_text = ' '.join(texts)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(full_text)

    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("Word Cloud")
    save_plot('wordcloud.svg', output_dir)

def plot_top_bigrams(texts, top_n=20, output_dir="outputs"):
    """
    Find and plot most common bigrams.
    """
    vectorizer = CountVectorizer(ngram_range=(2,2), stop_words='english')
    X = vectorizer.fit_transform(texts)
    bigram_counts = X.sum(axis=0).A1
    bigram_vocab = vectorizer.get_feature_names_out()

    counter = Counter(dict(zip(bigram_vocab, bigram_counts)))
    labels, values = zip(*counter.most_common(top_n))

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='purple')
    plt.xticks(rotation=45, ha='right')
    plt.title(f'Top {top_n} Bigrams')
    plt.tight_layout()
    save_plot('top_bigrams.svg', output_dir)

def perform_ner_collect(texts):
    """
    Perform Named Entity Recognition and collect entities.
    """
    ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
    entities = []
    for text in texts:
        if not text.strip():
            continue
        try:
            results = ner_pipeline(text)
            entities.extend([r['word'] for r in results])
        except Exception as e:
            print(f"NER error: {e}")
    return entities

def perform_sentiment_analysis_collect(texts):
    """
    Perform Sentiment Analysis and collect labels.
    """
    sentiment_pipeline = pipeline("sentiment-analysis")
    sentiments = []
    for text in texts:
        if not text.strip():
            continue
        try:
            result = sentiment_pipeline(text[:512])
            sentiments.append(result[0]['label'])
        except Exception as e:
            print(f"Sentiment error: {e}")
    return sentiments

def plot_top_entities(entities, output_dir="outputs", filename="top_entities.svg"):
    """
    Plot top Named Entities.
    """
    counter = Counter(entities)
    if not counter:
        print("No entities to plot.")
        return
    labels, values = zip(*counter.most_common(10))

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='teal')
    plt.xticks(rotation=45, ha='right')
    plt.title("Top Named Entities")
    plt.tight_layout()
    save_plot(filename, output_dir)

def plot_sentiment_distribution(sentiments, output_dir="outputs", filename="sentiment_distribution.svg"):
    """
    Plot Sentiment Distribution.
    """
    counter = Counter(sentiments)
    if not counter:
        print("No sentiments to plot.")
        return
    labels, values = zip(*counter.items())

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Sentiment Distribution")
    plt.tight_layout()
    save_plot(filename, output_dir)

def save_plot(filename, output_dir="outputs"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path)
    plt.close()
    print(f"Saved plot: {output_path}")

def summarize_texts(texts, max_tokens=1024):
    """
    Summarize the combined texts. Truncate if necessary.
    """
    full_text = ' '.join(texts)
    full_text = full_text[:max_tokens]  # Make sure it doesn't exceed model limits

    try:
        summary = summarizer(full_text, max_length=200, min_length=50, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Summarization error: {e}")
        return "Summarization failed."
    
def save_summary_csv(overall_stats, output_dir="outputs/summary"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df = pd.DataFrame(overall_stats)
    df.to_csv(os.path.join(output_dir, "document_summaries.csv"), index=False)
    print(f"Saved document summaries to {os.path.join(output_dir, 'document_summaries.csv')}")

# --- Main Workflow ---
def full_eda_batch(document_ids, base_output_dir="outputs"):
    overall_stats = []
    all_entities = []
    all_sentiments = []

    for doc_id in tqdm(document_ids, desc="Running batch EDA"):
        # Create a subfolder for each document
        doc_output_dir = os.path.join(base_output_dir, str(doc_id))
        texts = fetch_document_text(doc_id)

        if not texts:
            print(f"No text found for document {doc_id}")
            continue

        print(f"\n--- Document {doc_id} Info ---")
        print(f"Pages: {len(texts)}")
        print(f"Total words: {sum(len(t.split()) for t in texts)}")
        print(f"Characters: {sum(len(t) for t in texts)}")

        cleaned_texts = clean_texts(texts)

        # Run EDA steps, but save each document's plots separately
        plot_word_frequency(cleaned_texts, output_dir=doc_output_dir)
        plot_wordcloud(cleaned_texts, output_dir=doc_output_dir)
        plot_top_bigrams(cleaned_texts, output_dir=doc_output_dir)

        # Perform NER and collect entities
        entities = perform_ner_collect(cleaned_texts)
        all_entities.extend(entities)

        # Perform sentiment and collect sentiments
        sentiments = perform_sentiment_analysis_collect(cleaned_texts)
        all_sentiments.extend(sentiments)

        # Save per-document plots
        plot_top_entities(entities, output_dir=doc_output_dir)
        plot_sentiment_distribution(sentiments, output_dir=doc_output_dir)

        # Summarize the document
        doc_summary = summarize_texts(cleaned_texts)

        # Collect simple stats
        doc_stats = {
            "document_id": str(doc_id),
            "pages": len(texts),
            "total_words": sum(len(t.split()) for t in texts),
            "total_characters": sum(len(t) for t in texts),
            "summary": doc_summary
        }
        overall_stats.append(doc_stats)

    # After all documents, plot overall aggregation
    overall_output_dir = os.path.join(base_output_dir, "summary")
    if not os.path.exists(overall_output_dir):
        os.makedirs(overall_output_dir)

    plot_top_entities(all_entities, output_dir=overall_output_dir, filename='overall_top_entities.svg')
    plot_sentiment_distribution(all_sentiments, output_dir=overall_output_dir, filename='overall_sentiment_distribution.svg')

    save_summary_csv(overall_stats)

    return overall_stats

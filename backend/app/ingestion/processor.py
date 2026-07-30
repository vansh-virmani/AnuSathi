import os
import sys
import uuid
import json
from app.ingestion.loaders.pdf import load_pdf
from app.ingestion.chunking.splitter import split_documents
from app.services.retrieval.embeddings import embed_texts
from app.config import settings
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Local folder where parsed + chunked JSON metadata is saved for debugging practice
PROCESSED_DATA_DIR = "processed_data"

# Initialize Qdrant Client
qdrant_client = QdrantClient(
    url=settings.QDRANT_ENDPOINT,
    api_key=settings.QDRANT_KEY,
    timeout=60.0
)

#this function save chunk metadata
def save_processed_locally(data: dict, filename: str) -> str:
    """Save parsed chunk metadata as JSON in processed_data/<source_type>/."""
    folder =(PROCESSED_DATA_DIR)
    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, f"{filename}.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return dest  ##it returns the destination of the saved folder in local storage of hard disk


def process_file(file_path: str, filename: str):
    """Parse → chunk → save locally → embed → index in Qdrant."""
#1 Parse pdf
    documents = load_pdf(file_path)
    if not documents:
        raise ValueError("NO content extracted from pdf")
    
        # 2. Chunk text
    chunks = split_documents(documents)
    if not chunks:
        raise ValueError("No valid chunks found!")

    # 3. Save processed metadata locally
    processed_data = {
        "filename": filename,
        "chunks": [
    {
        "page": chunk.metadata.get("page"),
        "text": chunk.page_content,
    }
    for chunk in chunks
]
    }
    
    #calling save_processes function and storing in json 
    
    save_processed_locally(processed_data, filename)

    # 4. Embed and index in Qdrant
    texts_to_embed = [chunk.page_content for chunk in chunks]
    embeddings = embed_texts(texts_to_embed)
    
    
    #verification of len(chunks) and len(embeddings) they must be same
    #for development test#!!!!
    if len(chunks) != len(embeddings):
        raise ValueError(
            f" CRITICAL BUG: Embedding alignment mismatch for {filename}! "
            f"Expected {len(chunks)} vectors, but model generated {len(embeddings)}."
        )
    else:
        print(f"Embedding Verification Passed: {len(chunks)} chunks perfectly mapped to {len(embeddings)} vectors.")
    #Creating points req for qdrant db
    points = [
        models.PointStruct(  #point are objects containing info 
            id=str(uuid.uuid4()),  #unique id required for quadrant collection for each chunk
            vector=vector,
            payload={
                "text": chunk.page_content,
                "source": filename,
                "page": chunk.metadata.get("page", 1),
            },
        )
        for chunk, vector in zip(chunks, embeddings)   
    ]
    #"The embedding list preserves the same order as the chunk list, so zip naturally pairs each chunk with its corresponding embedding."

    qdrant_client.upsert(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points=points,
    )


def process_directory(dir_path: str): # for development/testing purpose not for users
    """Process every PDF file in a directory Data\Papers."""

    files = [
        f for f in os.listdir(dir_path) 
         if f.lower().endswith(".pdf")
    ]

    for filename in files:
        file_path = os.path.join(dir_path, filename)
        process_file(file_path, filename)


def initialize_quadrant(wipe: bool = False):
    """
    
    Pass --wipe to drop and recreate the Qdrant collection before ingestion.
    """

    # Wipe collection if requested
    if wipe:

        if qdrant_client.collection_exists(settings.QDRANT_COLLECTION_NAME):

            qdrant_client.delete_collection(settings.QDRANT_COLLECTION_NAME)

    # Recreate collection — dimension resolved at runtime after embedding model probe
    if not qdrant_client.collection_exists(settings.QDRANT_COLLECTION_NAME):
        dim = 384
        qdrant_client.create_collection(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=dim,
                distance=models.Distance.COSINE,
            ),
        )
        #to create a index named source for particular filtering of pdf's on basis of their filename
        qdrant_client.create_payload_index(
             collection_name=settings.QDRANT_COLLECTION_NAME,
             field_name="source",
             field_schema=models.PayloadSchemaType.KEYWORD, #imp edge case always create payload index if filtering
)

       


if __name__ == "__main__":
    # Usage:
    #   python -m app.ingestion.processor --wipe use wipe if wanted to del old collection
   
    wipe_requested = "--wipe" in sys.argv

    target_dir = os.path.join("Data", "Papers")

    if not os.path.exists(target_dir):
        print(f"Error: path '{target_dir}' does not exist.")
        sys.exit(1)
    initialize_quadrant(wipe_requested)
    process_directory(target_dir)

    

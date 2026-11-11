
from pathlib import Path
import json
import chromadb
from sentence_transformers import SentenceTransformer

project_dir = Path(__file__).resolve().parent.parent
chunks_file = project_dir / "data" / "processed" / "chunks.jsonl"
db_path = project_dir / "data" / "vector_db"

chunks = []

with chunks_file.open("r", encoding="utf-8") as file:
    for line in file:
        chunks.append(json.loads(line))

print(f"Loaded {len(chunks)} chunks.")

print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=str(db_path))

# Rebuild collection from scratch
try:
    client.delete_collection("coursemate_knowledge")
except Exception:
    pass

collection = client.create_collection(
    name="coursemate_knowledge",
    metadata={"hnsw:space": "cosine"}
)

batch_size = 32

for start in range(0, len(chunks), batch_size):
    batch = chunks[start:start + batch_size]

    texts = [item["content"] for item in batch]

    embeddings = model.encode(
        texts,
        show_progress_bar=False
    ).tolist()

    ids = [
        f'{item["course"]}_{item["source"]}_{item["chunk_id"]}'
        for item in batch
    ]

    metadatas = [
        {
            "course": item["course"],
            "source": item["source"],
            "chunk_id": item["chunk_id"],
            "file_type": item.get("file_type", ".txt")
        }
        for item in batch
    ]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"Processed {min(start + batch_size, len(chunks))}/{len(chunks)}")

print("\nVector database rebuilt successfully!")
print(f"Total stored chunks: {collection.count()}")
print(f"Database location: {db_path}")

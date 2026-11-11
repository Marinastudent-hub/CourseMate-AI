
from pathlib import Path
import re
import chromadb
from sentence_transformers import SentenceTransformer

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "data" / "vector_db"

print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=str(db_path))
collection = client.get_collection(name="coursemate_knowledge")

STOPWORDS = {
    "what", "is", "are", "the", "a", "an", "in",
    "of", "for", "to", "and", "how", "does", "do",
    "used", "use", "with", "from", "on", "it",
    "this", "that", "be", "can", "i", "me",
    "material", "materials", "course", "file",
    "explain", "tell", "about", "give", "me"
}

COURSE_HINTS = {
    "database": [
        "primary key",
        "foreign key",
        "database",
        "sql",
        "normalization",
        "entity",
        "er model",
        "relational"
    ],

    "machine_learning": [
        "overfitting",
        "underfitting",
        "supervised learning",
        "unsupervised learning",
        "training data",
        "machine learning",
        "classification",
        "regression",
        "hypothesis"
    ],

    "python": [
        "python",
        "variable",
        "dictionary",
        "function",
        "loop",
        "string"
    ]
}


def detect_course(question):
    question = question.lower()

    for course, hints in COURSE_HINTS.items():
        if any(hint in question for hint in hints):
            return course

    return None

def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return {
        word for word in words
        if word not in STOPWORDS and len(word) > 1
    }


def search_courses(question, top_k=5):

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    query_tokens = tokenize(question)

    question_embedding = model.encode(
        [question]
    ).tolist()

    results = collection.query(
        query_embeddings=question_embedding,
        n_results=total_chunks
    )

    candidates = []

    for i, content in enumerate(results["documents"][0]):

        metadata = results["metadatas"][0][i]

        source = metadata["source"]
        course = metadata["course"]

        target_course = detect_course(question)

        if target_course and course.lower() != target_course:
             continue

        source_tokens = tokenize(
            Path(source).stem.replace("_", " ")
        )

        course_tokens = tokenize(course)

        specific_file_tokens = source_tokens - course_tokens

        file_match = bool(
            query_tokens & specific_file_tokens
        )

        course_match = bool(
            query_tokens & course_tokens
        )

        content_tokens = tokenize(content)

        ranking_tokens = query_tokens - course_tokens

        if file_match:
            ranking_tokens -= specific_file_tokens

        matched_tokens = ranking_tokens & content_tokens

        keyword_score = (
            len(matched_tokens) / len(ranking_tokens)
            if ranking_tokens else 0
        )

        distance = results["distances"][0][i]
        semantic_score = 1 / (1 + max(distance, 0))

        candidates.append({
            "content": content,
            "course": course,
            "source": source,
            "chunk_id": metadata["chunk_id"],
            "file_type": metadata.get("file_type", "unknown"),
            "distance": distance,
            "semantic_score": semantic_score,
            "keyword_score": keyword_score,
            "file_match": file_match,
            "course_match": course_match
        })

    # Prioritize a specifically mentioned file.
    matching_files = [
        item for item in candidates
        if item["file_match"]
    ]

    if matching_files:
        candidates = matching_files

    # Otherwise, prioritize the requested course.
    else:
        matching_courses = [
            item for item in candidates
            if item["course_match"]
        ]

        if matching_courses:
            candidates = matching_courses

    # Calculate final relevance score.
    for item in candidates:

        item["hybrid_score"] = (
            0.35 * item["semantic_score"] +
            0.65 * item["keyword_score"]
        )

    candidates.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True
    )

    # Limit repeated chunks from the same source.
    selected = []
    source_counts = {}

    for item in candidates:

        source = item["source"]

        if source_counts.get(source, 0) >= 2:
            continue

        selected.append(item)
        source_counts[source] = source_counts.get(source, 0) + 1

        if len(selected) == top_k:
            break

    return selected


if __name__ == "__main__":

    question = input("Ask a question: ")

    results = search_courses(question)

    print("\nRetrieval Results:\n")

    for result in results:
        print(f"Course: {result['course']}")
        print(f"Source: {result['source']}")
        print(f"File Type: {result['file_type']}")
        print(f"Chunk: {result['chunk_id']}")
        print(f"Distance: {result['distance']:.4f}")
        print(f"Semantic Score: {result['semantic_score']:.4f}")
        print(f"Keyword Score: {result['keyword_score']:.4f}")
        print(f"Final Score: {result['hybrid_score']:.4f}")
        print(f"Content: {result['content'][:400]}")
        print("-" * 60)

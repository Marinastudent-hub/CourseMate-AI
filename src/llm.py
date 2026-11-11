
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

project_dir = Path(__file__).resolve().parent.parent
load_dotenv(project_dir / ".env")

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY was not found in .env")

client = genai.Client(api_key=api_key)


def generate_answer(question, retrieved_chunks):

    context_parts = []

    for i, chunk in enumerate(retrieved_chunks, 1):
        context_parts.append(
            f"""
SOURCE ID: {i}
COURSE: {chunk['course']}
FILE: {chunk['source']}
CONTENT:
{chunk['content']}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are CourseMate AI, an academic question-answering assistant.

Your task is to answer the student's question accurately
using ONLY the provided sources.

STRICT RULES:

1. Read all provided sources before answering.
2. Identify which sources directly contain information
   that answers the question.
3. Do not use general knowledge or outside information.
4. Do not invent definitions, examples, or explanations.
5. Every factual statement must have a citation.
6. Cite sources using their exact IDs:
   [Source 1], [Source 2], etc.
7. A source ID is valid ONLY if it appears in the
   provided sources below.
8. Never invent or guess a source ID.
9. Only cite a source if its content directly supports
   the specific statement.
10. Do not cite unrelated sources.
11. Do not combine information from different courses
    unless the question explicitly requires comparison.
12. If the sources do not contain enough information,
    clearly say that the information is unavailable.
13. Keep the answer clear, accurate, and concise.

IMPORTANT:
The source ID refers to the numbered source heading.
Never change or renumber source IDs.

PROVIDED SOURCES:
{context}

STUDENT QUESTION:
{question}

Write the answer with accurate inline citations.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text or "I couldn't generate an answer."

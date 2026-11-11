
import json
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.retriever import search_courses
from src.llm import generate_answer


questions_file = Path(__file__).parent / "test_questions.json"

with open(questions_file, "r", encoding="utf-8") as file:
    test_questions = json.load(file)


retrieval_hits = 0
valid_citations = 0
citation_tests = 0
out_of_scope_passes = 0
out_of_scope_tests = 0

print("=" * 65)
print("COURSEMATE AI - EVALUATION")
print("=" * 65)

for index, test in enumerate(test_questions, 1):

    question = test["question"]
    expected_source = test["expected_source"]
    expected_course = test["expected_course"]

    print(f"\nTest {index}: {question}")
    print("-" * 65)

    results = search_courses(question, top_k=5)

    answer = generate_answer(question, results)

    if expected_source is not None:

        found_source = any(
            expected_source.lower() in item["source"].lower()
            for item in results
        )

        found_course = any(
            item["course"].lower() == expected_course
            for item in results
        )

        if found_source:
            retrieval_hits += 1

        print(f"Expected Source Retrieved: {found_source}")
        print(f"Expected Course Retrieved: {found_course}")

        citation_ids = [
            int(number)
            for number in re.findall(
                r"\[Source\s+(\d+)\]",
                answer
            )
        ]

        citation_tests += 1

        citations_are_valid = (
            bool(citation_ids)
            and all(1 <= number <= len(results) for number in citation_ids)
        )

        if citations_are_valid:
            valid_citations += 1

        print(f"Valid Citation IDs: {citations_are_valid}")

    else:

        out_of_scope_tests += 1

        refusal_phrases = [
            "not contain",
            "not available",
            "unavailable",
            "not enough information",
            "no information"
        ]

        refused = any(
            phrase in answer.lower()
            for phrase in refusal_phrases
        )

        if refused:
            out_of_scope_passes += 1

        print(f"Out-of-Scope Refusal: {refused}")

    print("\nAnswer:")
    print(answer)

    print("\nRetrieved Sources:")
    for item in results:
        print(f"- {item['course']} | {item['source']}")

    print("=" * 65)


total_in_scope = citation_tests

print("\nFINAL EVALUATION RESULTS")
print("=" * 65)

if total_in_scope:
    print(
        f"Retrieval Hit Rate: "
        f"{retrieval_hits / total_in_scope:.2%}"
    )

    print(
        f"Valid Citation Rate: "
        f"{valid_citations / total_in_scope:.2%}"
    )

if out_of_scope_tests:
    print(
        f"Out-of-Scope Refusal Rate: "
        f"{out_of_scope_passes / out_of_scope_tests:.2%}"
    )

print("=" * 65)

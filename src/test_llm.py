
from llm import generate_answer

test_chunks = [
    {
        "course": "python",
        "source": "python_for_everyone.txt",
        "content": "A variable is a name that refers to a value. For example, message = 'Hello' assigns a string to the variable message."
    }
]

answer = generate_answer(
    "What is a variable in Python?",
    test_chunks
)

print("\nGemini Answer:\n")
print(answer)

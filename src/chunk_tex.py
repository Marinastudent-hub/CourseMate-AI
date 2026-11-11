
from pathlib import Path
import json
import re
import csv
import fitz
from docx import Document

project_dir = Path(__file__).resolve().parent.parent
raw_dir = project_dir / "data" / "raw"
processed_dir = project_dir / "data" / "processed"

output_file = processed_dir / "chunks.jsonl"

CHUNK_SIZE = 300
OVERLAP = 50

SUPPORTED_FORMATS = {".pdf", ".txt", ".csv", ".docx"}


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text(file_path):
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        pages = []
        with fitz.open(file_path) as pdf:
            for page in pdf:
                pages.append(page.get_text())
        return "\n".join(pages)

    elif extension == ".txt":
        return file_path.read_text(
            encoding="utf-8",
            errors="replace"
        )

    elif extension == ".docx":
        document = Document(file_path)
        parts = []

        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                parts.append(paragraph.text)

        for table in document.tables:
            for row in table.rows:
                parts.append(
                    " | ".join(cell.text for cell in row.cells)
                )

        return "\n".join(parts)

    return ""


def process_csv(file_path, course_name):
    chunks = []

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        errors="replace",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for chunk_id, row in enumerate(reader, start=1):
            row_content = " | ".join(
                f"{key}: {value}"
                for key, value in row.items()
                if key and value
            )

            if row_content.strip():
                chunks.append({
                    "course": course_name,
                    "source": file_path.name,
                    "file_type": ".csv",
                    "chunk_id": chunk_id,
                    "content": clean_text(row_content)
                })

    return chunks


all_chunks = []

for course_folder in raw_dir.iterdir():

    if not course_folder.is_dir():
        continue

    for file_path in course_folder.rglob("*"):

        if file_path.suffix.lower() not in SUPPORTED_FORMATS:
            continue

        try:
            # CSV: one chunk per row
            if file_path.suffix.lower() == ".csv":
                csv_chunks = process_csv(
                    file_path,
                    course_folder.name
                )

                all_chunks.extend(csv_chunks)

                print(
                    f"Processed: {file_path.name} "
                    f"({len(csv_chunks)} row chunks)"
                )
                continue

            # PDF, TXT, DOCX
            content = clean_text(extract_text(file_path))

            if not content:
                print(f"Skipped empty file: {file_path.name}")
                continue

            words = content.split()
            start = 0
            chunk_id = 1

            while start < len(words):
                end = start + CHUNK_SIZE
                chunk_words = words[start:end]

                if chunk_words:
                    all_chunks.append({
                        "course": course_folder.name,
                        "source": file_path.name,
                        "file_type": file_path.suffix.lower(),
                        "chunk_id": chunk_id,
                        "content": " ".join(chunk_words)
                    })

                    chunk_id += 1

                start += CHUNK_SIZE - OVERLAP

            print(f"Processed: {file_path.name}")

        except Exception as error:
            print(f"Error reading {file_path.name}: {error}")


processed_dir.mkdir(parents=True, exist_ok=True)

with output_file.open("w", encoding="utf-8") as file:
    for chunk in all_chunks:
        file.write(
            json.dumps(chunk, ensure_ascii=False) + "\n"
        )

print("\nDocument processing completed!")
print(f"Total chunks: {len(all_chunks)}")
print(f"Output: {output_file}")


from pathlib import Path
import pandas as pd
from docx import Document
import re

project_dir = Path(__file__).resolve().parent.parent
processed_dir = project_dir / "data" / "processed"

for course_folder in processed_dir.iterdir():
    if not course_folder.is_dir():
        continue

    txt_files = list(course_folder.glob("*.txt"))

    for txt_file in txt_files:
        content = txt_file.read_text(
            encoding="utf-8",
            errors="replace"
        )

        # Remove invalid XML control characters
        content = re.sub(
            r"[\x00-\x08\x0B\x0C\x0E-\x1F]",
            "",
            content
        )

        # Create DOCX
        doc = Document()
        doc.add_heading(course_folder.name.replace("_", " ").title(), 0)

        # Split into paragraphs to avoid oversized Word paragraphs
        for paragraph in content.split("\n"):
            if paragraph.strip():
                doc.add_paragraph(paragraph)

        docx_path = course_folder / f"{course_folder.name}.docx"
        doc.save(docx_path)

        # Create CSV
        words = content.split()
        chunk_size = 250
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])

            if chunk.strip():
                chunks.append({
                    "course": course_folder.name,
                    "source": txt_file.name,
                    "chunk_id": len(chunks) + 1,
                    "content": chunk
                })

        csv_path = course_folder / f"{course_folder.name}.csv"

        pd.DataFrame(chunks).to_csv(
            csv_path,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"Created: {docx_path.name}")
        print(f"Created: {csv_path.name}")
        print(f"Chunks: {len(chunks)}")
        print("-" * 40)

print("All formats created successfully!")

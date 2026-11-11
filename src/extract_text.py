
from pathlib import Path
import fitz

project_dir = Path(__file__).resolve().parent.parent
raw_dir = project_dir / "data" / "raw"
output_dir = project_dir / "data" / "processed"

pdf_files = list(raw_dir.rglob("*.pdf"))

for pdf_path in pdf_files:
    relative_folder = pdf_path.parent.relative_to(raw_dir)
    txt_folder = output_dir / relative_folder
    txt_folder.mkdir(parents=True, exist_ok=True)

    text_content = []

    with fitz.open(pdf_path) as document:
        for page in document:
            text_content.append(page.get_text())

    full_text = "\n".join(text_content).strip()

    txt_path = txt_folder / f"{pdf_path.stem}.txt"
    txt_path.write_text(full_text, encoding="utf-8")

    print(f"Converted: {pdf_path.name}")
    print(f"Text length: {len(full_text)} characters")
    print("-" * 40)

print(f"\nFinished! Total PDF files: {len(pdf_files)}")

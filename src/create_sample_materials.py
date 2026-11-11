
from pathlib import Path
import csv
from docx import Document

project_dir = Path(__file__).resolve().parent.parent
raw_dir = project_dir / "data" / "raw"

# 1. Python CSV material
python_dir = raw_dir / "python"
python_dir.mkdir(parents=True, exist_ok=True)

csv_file = python_dir / "python_concepts.csv"

with csv_file.open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Concept", "Description", "Example"])

    writer.writerows([
        ["Variable", "A named reference to a stored value", "age = 20"],
        ["Integer", "A whole number data type", "count = 10"],
        ["String", "A sequence of characters", 'name = "Marina"'],
        ["List", "An ordered and mutable collection", "numbers = [1, 2, 3]"],
        ["Tuple", "An ordered and immutable collection", "point = (3, 5)"],
        ["Dictionary", "A collection of key-value pairs", 'student = {"name": "Ali"}'],
        ["Function", "A reusable block of code", "def greet(): pass"]
    ])

# 2. Machine Learning DOCX material
ml_dir = raw_dir / "machine_learning"
ml_dir.mkdir(parents=True, exist_ok=True)

doc = Document()
doc.add_heading("Machine Learning Supplementary Notes", 0)

doc.add_heading("Supervised Learning", level=1)
doc.add_paragraph(
    "Supervised learning is a machine learning approach "
    "that trains a model using labeled training data. "
    "Each training example contains input features and "
    "a known target output."
)

doc.add_heading("Classification", level=1)
doc.add_paragraph(
    "Classification predicts a category or class. "
    "Examples include spam detection and image recognition."
)

doc.add_heading("Regression", level=1)
doc.add_paragraph(
    "Regression predicts a continuous numerical value. "
    "Examples include house price prediction and temperature forecasting."
)

doc.add_heading("Overfitting", level=1)
doc.add_paragraph(
    "Overfitting happens when a model learns the training data "
    "too closely, including noise. It may perform well on training "
    "data but poorly on unseen data."
)

doc.save(ml_dir / "machine_learning_notes.docx")

# 3. Database TXT material
database_dir = raw_dir / "database"
database_dir.mkdir(parents=True, exist_ok=True)

database_text = """
Database Supplementary Notes

A database is an organized collection of data that can be stored,
managed, and retrieved.

A Database Management System (DBMS) is software used to create,
manage, and interact with databases.

A primary key uniquely identifies each row in a table.
A primary key cannot contain NULL values.

A foreign key is an attribute that references a key in another table.
It helps establish relationships between tables.

Normalization is the process of organizing database tables
to reduce data redundancy and improve data integrity.

SQL is a language used to communicate with relational databases.
"""

(database_dir / "database_notes.txt").write_text(
    database_text.strip(),
    encoding="utf-8"
)

print("Supplementary materials created successfully!")
print("Created: python_concepts.csv")
print("Created: machine_learning_notes.docx")
print("Created: database_notes.txt")

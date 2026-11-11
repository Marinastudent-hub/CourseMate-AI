# CourseMate AI 🎓

**An Academic Question-Answering System Powered by Retrieval-Augmented Generation (RAG)**

CourseMate AI is an intelligent academic assistant that helps students find answers to questions using their course materials. It retrieves relevant information from multiple documents and generates answers grounded in the provided sources, with inline source citations.

## ✨ Features

- Supports three academic courses: Python, Machine Learning, and Database Design.
- Processes PDF, CSV, DOCX, and TXT files.
- Extracts, cleans, and splits documents into text chunks.
- Generates semantic embeddings using Sentence Transformers.
- Stores and searches document embeddings using ChromaDB.
- Uses hybrid retrieval combining semantic similarity and keyword matching.
- Generates grounded answers using Google's Gemini API.
- Provides inline source citations.
- Displays original source files inside the application.
- Handles questions that are outside the available course materials.
- Includes an evaluation script for testing retrieval and answer behavior.

## 🏗️ System Architecture

1. **Document Ingestion:** Load course materials in different file formats.
2. **Text Processing:** Extract, clean, and split the content into chunks.
3. **Embedding Generation:** Convert chunks into vector representations.
4. **Vector Storage:** Store embeddings and metadata in ChromaDB.
5. **Retrieval:** Retrieve relevant chunks using semantic and keyword-based ranking.
6. **Answer Generation:** Pass retrieved context to Gemini to generate grounded answers.
7. **Source Attribution:** Display citations and allow users to view the original documents.

## 🛠️ Tech Stack

- Python
- Streamlit
- Google Gemini API
- ChromaDB
- Sentence Transformers
- PyTorch
- Hugging Face
- Pandas
- python-docx
- PyPDF

## 📂 Project Structure

```text
CourseMate-AI/
│
├── app/
│   └── streamlit_app.py
│
├── data/
│   ├── raw/
│   │   ├── python/
│   │   ├── machine_learning/
│   │   └── database/
│   │
│   ├── processed/
│   └── vector_db/
│
├── src/
│   ├── extract_text.py
│   ├── create_formats.py
│   ├── chunk_tex.py
│   ├── build_vector_db.py
│   ├── retriever.py
│   ├── llm.py
│   └── test_llm.py
│
├── evaluation/
│   ├── test_questions.json
│   └── run_evaluation.py
│
├── assets/
│   └── screenshots/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Marinastudent-hub/CourseMate-AI.git
cd CourseMate-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API Key

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_api_key_here
```

Replace the placeholder with your own Google Gemini API key.

**Important:** Never upload your `.env` file or expose your API key publicly.

### 5. Build the Vector Database

If you are setting up the project from scratch, run:

```bash
python src/build_vector_db.py
```

This creates the ChromaDB collection from the processed course chunks.

### 6. Run the Application

```bash
streamlit run app/streamlit_app.py
```

The application will be available at:

`http://localhost:8501`

## 📊 Evaluation

The system was tested using seven questions across the three courses, including one out-of-scope question.

| Evaluation Metric | Result |
|---|---:|
| Expected Source Retrieval Rate | 100% |
| Valid Citation ID Rate | 100% |
| Out-of-Scope Refusal Rate | 100% |

**Evaluation details:**
- 6 out of 6 in-scope questions retrieved their expected source.
- 1 out of 1 out-of-scope question was correctly refused.
- Citation ID validation checks that cited source numbers exist among the retrieved results. It does not independently verify factual support for every cited statement.

## 📚 Course Materials

The project uses course materials covering:

- Python — *Python for Everybody* by Charles R. Severance.
- Machine Learning — *Machine Learning* by Tom M. Mitchell.
- Database Design — *Database Design, 2nd Edition* by Adrienne Watt and Nelson Eng.

Additional supplementary materials are included in CSV, DOCX, and TXT formats.

## 🔮 Future Improvements

- Improve retrieval for questions outside the available knowledge base.
- Expand the evaluation dataset.
- Add more course materials and document formats.
- Improve citation-level factual verification.
- Deploy the application for public access.


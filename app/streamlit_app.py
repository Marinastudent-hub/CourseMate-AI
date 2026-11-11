
import streamlit as st
import sys
import re
import base64
from pathlib import Path

import pandas as pd

project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir / "src"))

from retriever import search_courses
from llm import generate_answer


st.set_page_config(
    page_title="CourseMate AI",
    page_icon="📚",
    layout="wide"
)


SUGGESTED_QUESTIONS = [
    "What is a variable in Python?",
    "What is supervised learning?",
    "What is a primary key?",
    "What is overfitting in machine learning?",
    "What is a database management system?",
    "What is the difference between a list and a tuple?",
    "How does a machine learning model learn?",
    "What is database normalization?",
    "What are Python functions?"
]


if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_source" not in st.session_state:
    st.session_state.selected_source = None


def find_source_file(course, source_name):
    """Find the original file inside data/raw."""

    raw_dir = project_dir / "data" / "raw"
    file_name = Path(source_name).name

    course_dir = raw_dir / course

    if course_dir.exists():
        direct_path = course_dir / file_name

        if direct_path.is_file():
            return direct_path

    matches = list(raw_dir.rglob(file_name))

    if matches:
        return matches[0]

    return None


def get_cited_sources(answer, results):
    """Extract citations and map them to retrieved source files."""

    cited_numbers = []

    citation_groups = re.findall(
        r"\[([^\]]+)\]",
        answer
    )

    for group in citation_groups:

        numbers = re.findall(
            r"Source\s+(\d+)",
            group,
            re.IGNORECASE
        )

        for number in numbers:

            number = int(number)

            if number not in cited_numbers:
                cited_numbers.append(number)

    sources = []

    for number in cited_numbers:

        if 1 <= number <= len(results):

            result = results[number - 1]

            source_name = result["source"]
            course = result["course"]

            file_path = find_source_file(
                course,
                source_name
            )

            sources.append({
                "number": number,
                "course": course.replace("_", " ").title(),
                "file_name": Path(source_name).name,
                "chunk_id": result["chunk_id"],
                "content": result["content"],
                "file_path": str(file_path) if file_path else None
            })

    return sources


def display_sources(sources, key_prefix):
    """Display clickable source buttons."""

    for i, source in enumerate(sources):

        st.caption(
            f"Source {source['number']} | "
            f"{source['course']} | "
            f"Chunk {source['chunk_id']}"
        )

        if source.get("file_path"):

            if st.button(
                f"📄 View {source['file_name']}",
                key=f"{key_prefix}_{i}",
                use_container_width=True
            ):

                st.session_state.selected_source = source
                st.rerun()

        else:

            st.warning(
                f"Original file not found: {source['file_name']}"
            )


def show_source_content(source):
    """Display the original source file inside Streamlit."""

    file_path = source.get("file_path")

    if not file_path or not Path(file_path).is_file():

        st.error("The original source file could not be found.")
        return

    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    st.subheader(f"📄 {source['file_name']}")

    st.caption(
        f"Course: {source['course']} | "
        f"Referenced Chunk: {source['chunk_id']}"
    )

    # PDF Viewer
    if extension == ".pdf":

        pdf_bytes = file_path.read_bytes()

        base64_pdf = base64.b64encode(
            pdf_bytes
        ).decode("utf-8")

        pdf_html = f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}#toolbar=1"
            width="100%"
            height="750"
            style="border: none;"
            type="application/pdf">
        </iframe>
        """

        st.components.v1.html(
            pdf_html,
            height=760,
            scrolling=True
        )

    # DOCX Viewer
    elif extension == ".docx":

        from docx import Document

        document = Document(str(file_path))

        st.markdown("### Document Content")

        for paragraph in document.paragraphs:

            if paragraph.text.strip():
                st.write(paragraph.text)

        for table_index, table in enumerate(document.tables, 1):

            st.markdown(f"**Table {table_index}**")

            table_data = [
                [cell.text for cell in row.cells]
                for row in table.rows
            ]

            if table_data:
                st.table(
                    pd.DataFrame(table_data)
                )

    # CSV Viewer
    elif extension == ".csv":

        st.markdown("### Dataset Content")

        try:
            dataframe = pd.read_csv(
                file_path,
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            dataframe = pd.read_csv(
                file_path,
                encoding="latin-1"
            )

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Rows: {len(dataframe)} | "
            f"Columns: {len(dataframe.columns)}"
        )

    # TXT Viewer
    elif extension == ".txt":

        st.markdown("### Text File Content")

        text_content = file_path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        st.text_area(
            "File Content",
            value=text_content,
            height=500,
            disabled=True
        )

    else:

        st.warning(
            f"Unsupported file format: {extension}"
        )
        return

    # Retrieved Chunk
    st.divider()

    st.markdown(
        f"### 🔎 Retrieved Chunk {source['chunk_id']}"
    )

    st.info(source["content"])


# Sidebar
with st.sidebar:

    st.title("📚 CourseMate AI")
    st.caption("Your Learning Assistant")
    st.divider()

    st.subheader("💡 Suggested Questions")
    st.caption("Choose any question or write your own.")

    for i, q in enumerate(SUGGESTED_QUESTIONS):

        if st.button(
            q,
            key=f"suggested_{i}",
            use_container_width=True
        ):

            st.session_state.selected_question = q
            st.rerun()

    st.divider()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.selected_source = None
        st.rerun()


# Main Chat Area
st.title("CourseMate AI")
st.caption("Ask anything about your course materials.")
st.divider()


# Display Chat History
for message_index, message in enumerate(
    st.session_state.messages
):

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            with st.expander("📄 View Sources"):

                display_sources(
                    message["sources"],
                    f"history_{message_index}"
                )


# User Input
typed_question = st.chat_input(
    "Ask your question here..."
)

selected_question = st.session_state.pop(
    "selected_question",
    None
)

question = selected_question or typed_question


# Process Question
if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "Searching materials and generating your answer..."
            ):

                results = search_courses(question)

                if results:

                    answer = generate_answer(
                        question,
                        results
                    )

                    sources = get_cited_sources(
                        answer,
                        results
                    )

                    st.write(answer)

                    if sources:

                        with st.expander(
                            "📄 View Sources",
                            expanded=True
                        ):

                            display_sources(
                                sources,
                                f"current_{len(st.session_state.messages)}"
                            )

                    else:

                        st.caption(
                            "No valid source citations were returned for this answer."
                        )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                else:

                    answer = (
                        "I couldn't find relevant information "
                        "in the available course materials."
                    )

                    st.warning(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": []
                    })

        except Exception as e:

            st.error(f"An error occurred: {e}")


# Source Viewer
if st.session_state.selected_source:

    st.divider()

    with st.container(border=True):

        col1, col2 = st.columns([5, 1])

        with col1:
            st.header("📖 Source Viewer")

        with col2:

            if st.button(
                "✖ Close",
                use_container_width=True
            ):

                st.session_state.selected_source = None
                st.rerun()

        show_source_content(
            st.session_state.selected_source
        )


st.divider()

st.caption(
    "Powered by Gemini | Sentence Transformers | ChromaDB | Streamlit"
)

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

SAMPLE_FILES = {
    "📦 Sample Documents ZIP": "samples/sample.zip",
}


# =========================================================
# Page configuration
# =========================================================

st.set_page_config(
    page_title="AI Document Q&A",
    page_icon="📄",
    layout="wide",
)


# =========================================================
# Session state
# =========================================================

if "processed" not in st.session_state:
    st.session_state.processed = False

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []


# =========================================================
# API helpers
# =========================================================

def upload_file(
    filename: str,
    file_bytes: bytes,
    content_type: str,
):
    response = requests.post(
        f"{API_URL}/upload/file",
        files={
            "file": (
                filename,
                file_bytes,
                content_type,
            )
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def ingest_file(file_id: str):
    response = requests.post(
        f"{API_URL}/ingestion/{file_id}",
        timeout=300,
    )

    response.raise_for_status()

    return response.json()


def build_index():
    response = requests.post(
        f"{API_URL}/ingestion/build-index",
        timeout=300,
    )

    response.raise_for_status()

    return response.json()


def ask_question(query: str):
    response = requests.post(
        f"{API_URL}/ask/query",
        params={
            "query": query,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# Process uploaded/sample files
# =========================================================

def process_files(files):
    """
    Common flow for both sample files and user uploads:

        Upload
          ↓
        Ingest
          ↓
        Build BM25 index
    """

    st.session_state.processed = False
    st.session_state.processed_files = []

    progress = st.progress(0)

    try:
        total_files = len(files)

        for index, file_data in enumerate(files):

            filename = file_data["filename"]
            file_bytes = file_data["bytes"]
            content_type = file_data["content_type"]

            with st.status(
                f"Processing {filename}...",
                expanded=True,
            ) as status:

                # -----------------------------------------
                # 1. Upload
                # -----------------------------------------

                st.write("⬆️ Uploading...")

                upload_result = upload_file(
                    filename=filename,
                    file_bytes=file_bytes,
                    content_type=content_type,
                )

                file_id = upload_result["file_id"]

                st.write(
                    f"✓ Uploaded: `{file_id}`"
                )

                # -----------------------------------------
                # 2. Ingestion
                # -----------------------------------------

                st.write(
                    "⚙️ Extracting and creating chunks..."
                )

                ingestion_result = ingest_file(
                    file_id
                )

                chunks_count = ingestion_result.get(
                    "chunks_count",
                    0,
                )

                st.write(
                    f"✓ Created {chunks_count} chunks"
                )

                st.session_state.processed_files.append(
                    {
                        "file_id": file_id,
                        "filename": filename,
                        "file_type": ingestion_result.get(
                            "file_type"
                        ),
                        "chunks_count": chunks_count,
                    }
                )

                status.update(
                    label=f"✓ {filename} processed",
                    state="complete",
                )

            progress.progress(
                (index + 1) / total_files
            )

        # ---------------------------------------------
        # 3. Build index ONCE after all files
        # ---------------------------------------------

        with st.spinner(
            "🔎 Building search index..."
        ):
            index_result = build_index()

        st.session_state.processed = True

        st.success(
            f"🎉 Ready! "
            f"{index_result.get('files_count', 0)} "
            f"file(s) processed and search index built."
        )

    except requests.RequestException as exc:

        st.error(
            f"❌ Backend API error: {exc}"
        )

    except Exception as exc:

        st.error(
            f"❌ Processing failed: {exc}"
        )


# =========================================================
# Header
# =========================================================

st.title("📄 AI Document Q&A")

st.write(
    "Upload one or more documents and ask questions "
    "about their content."
)


# =========================================================
# Choose testing method
# =========================================================

st.subheader("🚀 Get Started")

mode = st.radio(
    "How would you like to test?",
    [
        "🧪 Use Sample Files",
        "📤 Upload My Files",
    ],
    horizontal=True,
)


# =========================================================
# SAMPLE FILE MODE
# =========================================================

if mode == "🧪 Use Sample Files":

    st.subheader("🧪 Try with Sample Files")

    st.write(
        "Use one of the built-in files. "
        "No download is required."
    )

    selected_sample = st.selectbox(
        "Choose a sample",
        list(SAMPLE_FILES.keys()),
    )

    sample_path = SAMPLE_FILES[selected_sample]

    st.info(
        f"Selected: **{selected_sample}**"
    )

    if st.button(
        "🚀 Process Sample",
        type="primary",
        use_container_width=True,
    ):

        if not os.path.exists(sample_path):

            st.error(
                f"Sample file not found: {sample_path}"
            )

        else:

            with open(
                sample_path,
                "rb",
            ) as file:

                file_bytes = file.read()

            extension = os.path.splitext(
                sample_path
            )[1].lower()

            content_types = {
                ".pdf": "application/pdf",
                ".xlsx": (
                    "application/vnd.openxmlformats-officedocument"
                    ".spreadsheetml.sheet"
                ),
                ".txt": "text/plain",
                ".csv": "text/csv",
                ".json": "application/json",
                ".md": "text/markdown",
                ".zip": "application/zip",
            }

            process_files(
                [
                    {
                        "filename": os.path.basename(
                            sample_path
                        ),
                        "bytes": file_bytes,
                        "content_type": content_types.get(
                            extension,
                            "application/octet-stream",
                        ),
                    }
                ]
            )


# =========================================================
# USER UPLOAD MODE
# =========================================================

else:

    st.subheader("📤 Upload Documents")

    uploaded_files = st.file_uploader(
        "Choose one or more files",
        type=[
            "pdf",
            "doc",
            "docx",
            "ppt",
            "pptx",
            "xls",
            "xlsx",
            "csv",
            "json",
            "txt",
            "md",
            "png",
            "jpg",
            "jpeg",
            "zip",
        ],
        accept_multiple_files=True,
    )

    if uploaded_files:

        st.write(
            f"**{len(uploaded_files)} file(s) selected**"
        )

        for file in uploaded_files:

            st.write(
                f"📄 {file.name} "
                f"({file.size / 1024:.1f} KB)"
            )

        if st.button(
            "🚀 Upload & Process",
            type="primary",
            use_container_width=True,
        ):

            files = []

            for uploaded_file in uploaded_files:

                files.append(
                    {
                        "filename": uploaded_file.name,
                        "bytes": uploaded_file.getvalue(),
                        "content_type": (
                            uploaded_file.type
                            or "application/octet-stream"
                        ),
                    }
                )

            process_files(files)


# =========================================================
# PROCESSED FILES
# =========================================================

if st.session_state.processed:

    st.divider()

    st.subheader("📚 Documents Ready")

    for file_info in st.session_state.processed_files:

        st.write(
            f"📄 **{file_info['filename']}** "
            f"— {file_info['chunks_count']} chunks"
        )


    # =====================================================
    # QUESTION / ANSWER
    # =====================================================

    st.divider()

    st.subheader("💬 Ask a Question")

    query = st.text_input(
        "Ask anything about your documents",
        placeholder=(
            "Example: What was the total revenue?"
        ),
    )

    if st.button(
        "🔍 Ask",
        type="primary",
        use_container_width=True,
    ):

        if not query.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            try:

                with st.spinner(
                    "🔎 Searching your documents..."
                ):

                    result = ask_question(query)

                st.subheader("💡 Answer")

                answer = result.get(
                    "answer",
                    result,
                )

                st.write(answer)

                # -----------------------------------------
                # Sources
                # -----------------------------------------

                sources = result.get(
                    "sources",
                    [],
                )

                if sources:

                    st.subheader("📚 Sources")

                    for source in sources:

                        filename = source.get(
                            "filename",
                            "Unknown file",
                        )

                        source_type = source.get(
                            "source_type",
                            "",
                        )

                        source_number = source.get(
                            "source_number",
                            "",
                        )

                        st.write(
                            f"📄 **{filename}** — "
                            f"{source_type} "
                            f"{source_number}"
                        )

            except requests.RequestException as exc:

                st.error(
                    f"❌ Could not connect to API: {exc}"
                )

            except Exception as exc:

                st.error(
                    f"❌ Question failed: {exc}"
                )
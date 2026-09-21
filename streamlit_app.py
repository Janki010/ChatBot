import io
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.services.ask_service import AskService
from app.services.bm25_service import BM25Service
from app.services.ingestion_service import IngestionService
from app.services.upload_file_service import UploadFileService

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
SAMPLES_DIR = BASE_DIR / "samples"

SAMPLE_FILES = {
    "📦 Sample Documents ZIP": SAMPLES_DIR / "sample.zip",
}

SAMPLE_QUESTIONS = [
    "What should be avoided to ensure statements are not disparaging toward healthcare professionals?",
    "Where prescribing information (PI) can be found should be provided prominently?",
    "Which department does Priya Patel work in?",
    "What role does Rahul Sharma have?",
    "What does the boy ask about the “world’s greatest lie”?",
    "How does the idea of a “Personal Legend” relate to a person’s life?",
]


st.set_page_config(
    page_title="AI Document Q&A",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .subtitle {
            color: #6b7280;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 650;
            margin-top: 1rem;
            margin-bottom: 0.75rem;
        }

        .info-card {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 12px;
            margin-bottom: 1rem;
        }

        .result-card {
            padding: 1rem;
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 12px;
            margin-bottom: 0.75rem;
        }

        .sample-question {
            font-size: 0.9rem;
            line-height: 1.35;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.2);
        }

        [data-testid="stSidebar"] .stButton button {
            text-align: left;
            white-space: normal;
            height: auto;
            min-height: 3rem;
            padding: 0.65rem 0.75rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


if "processed" not in st.session_state:
    st.session_state.processed = False

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "index_ready" not in st.session_state:
    st.session_state.index_ready = False


@st.cache_resource
def get_bm25_service() -> BM25Service:
    return BM25Service()


bm25_service = get_bm25_service()

upload_service = UploadFileService()

ingestion_service = IngestionService(
    bm25_service=bm25_service,
)

ask_service = AskService(
    bm25_service=bm25_service,
)


def initialize_index():
    """
    Build BM25 from the already persisted chunks.json.

    This means the application can answer the sample questions
    immediately without uploading or processing the sample files.
    """

    if st.session_state.index_ready:
        return

    try:
        with st.spinner("🔎 Preparing sample documents..."):
            result = ingestion_service.build_index()

        st.session_state.index_ready = True

        return result

    except Exception as exc:
        st.session_state.index_ready = False
        st.session_state.startup_index_error = str(exc)
        return None


initialize_index()

def create_upload_file(
    filename: str,
    file_bytes: bytes,
    content_type: str,
) -> UploadFile:
    """
    Convert Streamlit uploaded bytes into a FastAPI-compatible
    UploadFile object.
    """

    return UploadFile(
        file=io.BytesIO(file_bytes),
        filename=filename,
        headers=Headers(
            {
                "content-type": content_type,
            }
        ),
    )


def upload_file(
    filename: str,
    file_bytes: bytes,
    content_type: str,
):
    upload_file_object = create_upload_file(
        filename=filename,
        file_bytes=file_bytes,
        content_type=content_type,
    )

    file_id = upload_service.upload_file(
        upload_file_object
    )

    return {
        "file_id": str(file_id),
    }


def ingest_file(file_id: str):
    return ingestion_service.ingest_file(
        file_id=file_id
    )


def build_index():
    return ingestion_service.build_index()


def ask_question(query: str):
    return ask_service.ask(
        query=query,
    )


def process_files(files: list[dict]):
    """
    Upload and ingest user files.

    After all files are processed, rebuild BM25 once.
    """

    st.session_state.processed = False
    st.session_state.processed_files = []

    if not files:
        st.warning("No files selected.")
        return

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

                st.write("⬆️ Saving file...")

                upload_result = upload_file(
                    filename=filename,
                    file_bytes=file_bytes,
                    content_type=content_type,
                )

                file_id = upload_result["file_id"]

                st.write(
                    f"✓ Saved: `{file_id}`"
                )

                st.write(
                    "⚙️ Extracting and creating chunks..."
                )

                ingestion_result = ingest_file(
                    file_id=file_id,
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

        with st.spinner("🔎 Updating search index..."):
            index_result = build_index()

        st.session_state.processed = True
        st.session_state.index_ready = True

        st.success(
            f"🎉 Ready! "
            f"{index_result.get('files_count', 0)} "
            f"file(s) processed and search index built."
        )

    except Exception as exc:
        st.error(
            f"❌ Processing failed: {exc}"
        )

def run_search(query: str):
    """
    Execute BM25 search and store the results in session state.
    """

    query = query.strip()

    if not query:
        st.warning("Please enter a question.")
        return

    try:
        with st.spinner("🔎 Searching documents..."):
            results = ask_question(query)

        st.session_state.search_query = query
        st.session_state.search_results = results

    except Exception as exc:
        st.error(
            f"❌ Question failed: {exc}"
        )


with st.sidebar:

    st.markdown("## 💡 Sample Questions")

    st.caption(
        "Try a question instantly using the built-in sample documents."
    )

    st.divider()

    for index, question in enumerate(SAMPLE_QUESTIONS):

        if st.button(
            question,
            key=f"sample_question_{index}",
            use_container_width=True,
        ):
            st.session_state.selected_question = question
            run_search(question)

    st.divider()

    st.markdown("### 📚 How it works")

    st.caption(
        """
        Sample documents are indexed automatically when the app starts.

        You can:
        - Ask a sample question instantly
        - Upload your own documents
        - Search across processed documents
        """
    )

st.markdown(
    '<div class="main-title">📄 AI Document Q&A</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        Ask questions across your documents using fast, keyword-based retrieval.
    </div>
    """,
    unsafe_allow_html=True,
)


startup_error = st.session_state.get(
    "startup_index_error"
)

if startup_error:
    st.warning(
        "⚠️ Sample document index could not be loaded. "
        "You can still upload and process your own documents."
    )

else:
    st.success(
        "✓ Sample documents are ready. "
        "Choose a sample question from the sidebar or ask your own question."
    )

st.markdown(
    '<div class="section-title">💬 Ask a Question</div>',
    unsafe_allow_html=True,
)

query = st.text_input(
    "Ask anything about the documents",
    value=st.session_state.selected_question,
    placeholder="Example: Which department does Priya Patel work in?",
    label_visibility="collapsed",
)

ask_col, clear_col = st.columns(
    [5, 1]
)

with ask_col:

    if st.button(
        "🔍 Ask Question",
        type="primary",
        use_container_width=True,
    ):
        run_search(query)

with clear_col:

    if st.button(
        "Clear",
        use_container_width=True,
    ):
        st.session_state.selected_question = ""
        st.session_state.search_query = ""
        st.session_state.search_results = []

        st.rerun()


if st.session_state.search_results:

    st.divider()

    st.markdown(
        '<div class="section-title">💡 Relevant Results</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.search_query:
        st.caption(
            f"Results for: **{st.session_state.search_query}**"
        )

    results = st.session_state.search_results

    for index, result in enumerate(
        results,
        start=1,
    ):

        filename = result.get(
            "filename",
            "Unknown file",
        )

        source_type = result.get(
            "source_type",
            "",
        )

        source_number = result.get(
            "source_number",
            "",
        )

        element_type = result.get(
            "element_type",
            "",
        )

        score = result.get(
            "score",
            0,
        )

        metadata = result.get(
            "metadata",
            {},
        )

        text = result.get(
            "text",
            "",
        )

        st.markdown(
            f"""
            <div class="result-card">
                <strong>{index}. {filename}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            if source_type or source_number:
                location = " ".join(
                    part
                    for part in [
                        str(source_type),
                        str(source_number),
                    ]
                    if part
                )

                st.caption("📍 Location")
                st.write(location)

        with info_col2:
            if element_type:
                st.caption("🧩 Element Type")
                st.write(element_type)

        with info_col3:
            st.caption("🔎 BM25 Score")
            st.write(f"{score:.2f}")

        if metadata:
            with st.expander("View metadata"):
                st.json(metadata)

        st.markdown("**Content**")

        st.write(
            text or "No text content available."
        )

        if index < len(results):
            st.divider()


st.divider()

st.markdown(
    '<div class="section-title">📤 Upload Your Documents</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Upload one or more supported files to add them to the searchable document collection."
)


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


if st.session_state.processed:
    st.divider()

    st.markdown(
        '<div class="section-title">📚 Documents Ready</div>',
        unsafe_allow_html=True,
    )

    for file_info in st.session_state.processed_files:
        file_type = file_info.get(
            "file_type",
            "",
        )

        chunks_count = file_info.get(
            "chunks_count",
            0,
        )

        st.write(
            f"📄 **{file_info['filename']}** "
            f"— {chunks_count} chunks"
            + (
                f" · `{file_type}`"
                if file_type
                else ""
            )
        )

st.divider()

with st.expander("📦 Sample Documents"):
    selected_sample = st.selectbox(
        "Choose a sample",
        list(SAMPLE_FILES.keys()),
    )

    sample_path = SAMPLE_FILES[selected_sample]

    if not sample_path.exists():

        st.error(
            f"❌ Sample file not found:\n\n"
            f"`{sample_path}`"
        )

    else:

        sample_size = (
            sample_path.stat().st_size / 1024
        )

        st.caption(
            f"Sample ZIP size: {sample_size:.1f} KB"
        )

        with open(
            sample_path,
            "rb",
        ) as file:

            sample_bytes = file.read()

        st.download_button(
            label="⬇️ Download Sample ZIP",
            data=sample_bytes,
            file_name="sample.zip",
            mime="application/zip",
            use_container_width=True,
        )

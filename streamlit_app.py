import io
import mimetypes
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.services.ask_service import AskService
from app.services.bm25_service import BM25Service
from app.services.chunk_storage_service import ChunkStorageService
from app.services.ingestion_service import IngestionService
from app.services.upload_file_service import UploadFileService

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

SAMPLES_DIR = BASE_DIR / "samples"

SAMPLE_FILES = {
    "📦 Sample Documents ZIP": SAMPLES_DIR / "sample.zip",
}


st.set_page_config(
    page_title="AI Document Q&A",
    page_icon="📄",
    layout="wide",
)


if "processed" not in st.session_state:
    st.session_state.processed = False

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

if "bm25_service" not in st.session_state:
    st.session_state.bm25_service = BM25Service()

upload_service = UploadFileService()

chunk_storage_service = ChunkStorageService()

ingestion_service = IngestionService(
    bm25_service=st.session_state.bm25_service,
)

ask_service = AskService(
    bm25_service=st.session_state.bm25_service,
)



def create_upload_file(
    filename: str,
    file_bytes: bytes,
    content_type: str,
) -> UploadFile:
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
        query=query
    )

def process_files(files: list[dict]):

    st.session_state.processed = False
    st.session_state.processed_files = []

    progress = st.progress(0)

    try:

        if not files:
            st.warning("No files selected.")
            return

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
                    file_id=file_id
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

    except Exception as exc:

        st.error(
            f"❌ Processing failed: {exc}"
        )


st.title("📄 AI Document Q&A")

st.write(
    "Upload one or more documents and ask questions "
    "about their content."
)

st.subheader("🚀 Get Started")

mode = st.radio(
    "How would you like to test?",
    [
        "🧪 Use Sample Files",
        "📤 Upload My Files",
    ],
    horizontal=True,
)


if mode == "🧪 Use Sample Files":

    st.subheader("🧪 Try with Sample Files")

    st.write(
        "Use the built-in sample ZIP. "
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

    if not sample_path.exists():

        st.error(
            f"❌ Sample file not found.\n\n"
            f"Expected location:\n"
            f"`{sample_path}`"
        )

        st.warning(
            "Make sure `sample.zip` exists inside "
            "`samples/` and that the samples directory "
            "is committed to GitHub."
        )

    else:
        st.success(
            f"✓ Sample file found "
            f"({sample_path.stat().st_size / 1024:.1f} KB)"
        )

        if st.button(
            "🚀 Process Sample",
            type="primary",
            use_container_width=True,
        ):
            with open(
                sample_path,
                "rb",
            ) as file:

                file_bytes = file.read()

            content_type = (
                mimetypes.guess_type(
                    str(sample_path)
                )[0]
                or "application/zip"
            )

            process_files(
                [
                    {
                        "filename": sample_path.name,
                        "bytes": file_bytes,
                        "content_type": content_type,
                    }
                ]
            )


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

if st.session_state.processed:

    st.divider()

    st.subheader("📚 Documents Ready")

    for file_info in st.session_state.processed_files:

        st.write(
            f"📄 **{file_info['filename']}** "
            f"— {file_info['chunks_count']} chunks"
        )

    st.divider()

    st.subheader("💬 Ask a Question")

    query = st.text_input(
        "Ask anything about your documents",
        placeholder="Example: What was the total revenue?",
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
                    results = ask_question(
                        query=query
                    )

                if not results:
                    st.warning(
                        "No relevant information found."
                    )
                else:
                    st.subheader(
                        "💡 Relevant Results"
                    )

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

                        st.markdown(
                            f"### {index}. {filename}"
                        )

                        source_parts = []

                        if source_type:
                            source_parts.append(
                                source_type
                            )

                        if source_number:
                            source_parts.append(
                                str(source_number)
                            )

                        source_location = " ".join(
                            source_parts
                        )

                        if source_location:
                            st.write(
                                f"📍 **Location:** "
                                f"{source_location}"
                            )

                        if element_type:
                            st.write(
                                f"🧩 **Type:** "
                                f"{element_type}"
                            )

                        st.write(
                            f"🔎 **BM25 Score:** "
                            f"{score:.2f}"
                        )

                        metadata = result.get(
                            "metadata",
                            {},
                        )

                        if metadata:
                            with st.expander(
                                "View metadata"
                            ):
                                st.json(metadata)

                        st.markdown(
                            "**Content:**"
                        )

                        st.write(
                            result.get(
                                "text",
                                "",
                            )
                        )

                        st.divider()

            except Exception as exc:
                st.error(
                    f"❌ Question failed: {exc}"
                )

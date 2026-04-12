from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import tempfile
import os


class PDFReader:
    """PDF document loader and chunker."""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=64,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len,
        )

    def load_and_chunk_pdf(
        self, file_content: bytes, source_name: str
    ) -> tuple[List[str], List[Dict]]:
        """Load PDF and split into chunks.

        Args:
            file_content: PDF file bytes
            source_name: Name to identify this document

        Returns:
            Tuple of (texts, metadata) where:
            - texts: List of text chunks
            - metadata: List of metadata dicts with page and chunk_index
        """
        # Write to temporary file (PyPDFLoader requires file path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name

        try:
            # Load PDF
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()

            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)

            # Extract texts and metadata
            texts = []
            metadata = []

            for i, chunk in enumerate(chunks):
                texts.append(chunk.page_content)
                metadata.append({
                    "source": source_name,
                    "page": chunk.metadata.get("page", 0),
                    "chunk_index": i,
                })

            return texts, metadata

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# Singleton instance
pdf_reader = PDFReader()

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.tools.pdf_reader import pdf_reader
from app.services.embedding_service import embedding_service
from app.tools.vector_store import vector_store
from typing import Dict

router = APIRouter()


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(..., description="PDF file to upload"),
    source_name: str = Form(..., description="Name to identify this document"),
) -> Dict:
    """Upload and ingest a PDF document into the vector store.

    Pipeline:
    1. Validate file is PDF
    2. Load and chunk PDF (512 chars, 64 overlap)
    3. Generate embeddings for all chunks
    4. Upsert to Qdrant collection

    Args:
        file: PDF file upload
        source_name: Document identifier

    Returns:
        Dict with chunks_ingested, collection, source
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Only PDF files are supported"
        )

    try:
        # Read file content
        file_content = await file.read()

        # Load and chunk PDF
        texts, metadata = pdf_reader.load_and_chunk_pdf(file_content, source_name)

        if not texts:
            raise HTTPException(
                status_code=400, detail="No text content found in PDF"
            )

        # Generate embeddings
        embeddings = embedding_service.embed_documents(texts)

        # Upsert to Qdrant
        chunks_ingested = vector_store.upsert_documents(
            texts=texts,
            embeddings=embeddings,
            source=source_name,
            metadata=metadata,
        )

        return {
            "status": "success",
            "chunks_ingested": chunks_ingested,
            "collection": vector_store.collection_name,
            "source": source_name,
            "filename": file.filename,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}"
        )

from fastapi import APIRouter, UploadFile, File
from server.services.ocr import extract_text_from_file
from server.services.llm import normalize_invoice

router = APIRouter(prefix="/api")

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    extracted_text = extract_text_from_file(file)

    try:
        structured_data = normalize_invoice(extracted_text)
    except Exception as e:
        structured_data = {"error": str(e)}

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "extracted_text": extracted_text,
        "structured_data": structured_data,
    }
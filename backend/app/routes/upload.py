from pathlib import Path
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ingestion.processor import process_file,initialize_quadrant
from app.schemas.upload import UploadResponse

router = APIRouter(tags=["Upload"])

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):  #Helps uploading large pdf in streaming chunks in temp folder

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    upload_dir = Path("Data/Papers")
    upload_dir.mkdir(exist_ok=True,parents=True)

    file_path = upload_dir / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #Initialize qdrant first time if not done:
        initialize_quadrant()

        # Next: Call processor.process_pdf(file_path)
        process_file(
            file_path=str(file_path),
            filename=file.filename,
        )
        return UploadResponse(
            document_id= file.filename,
            status= "success",
            message="PDF processed successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to process PDF: {str(e)}")


    finally:
        #delete temporary file
        file_path.unlink(missing_ok=True) #equivalent to os.remove(file_path)

  

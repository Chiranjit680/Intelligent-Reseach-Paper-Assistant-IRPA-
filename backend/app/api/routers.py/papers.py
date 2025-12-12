from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Paper, PDFDocument    
import os
from datetime import datetime

# SAFE WINDOWS PATH
Upload_DIR = r"D:\IRPA\Intelligent-Reseach-Paper-Assistant-IRPA-\storage\uploads"
os.makedirs(Upload_DIR, exist_ok=True)

router = APIRouter(
    prefix="/papers",
    tags=["papers"],
)

@router.post("/")
async def upload_paper(
    title: str = Query(...),
    abstract: Optional[str] = Query(None),
    author_id: int = Query(...),
    pdf_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Read file into memory
    file_bytes = await pdf_file.read()

    # Generate a NICE unique filename using title + timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = title.replace(" ", "_")
    stored_filename = f"{safe_name}_{timestamp}.pdf"

    file_location = os.path.join(Upload_DIR, stored_filename)

    # Save file to disk
    with open(file_location, "wb") as f:
        f.write(file_bytes)

    # Save PDF metadata into DB
    pdf_document = PDFDocument(
        filename=pdf_file.filename,        # original name
        stored_filename=stored_filename,   # saved name
        file_path=file_location,
        file_size=len(file_bytes)
    )

    db.add(pdf_document)
    db.commit()
    db.refresh(pdf_document)

    # Save paper entry
    paper = Paper(
        title=title,
        abstract=abstract,
        author_id=author_id,
        pdf_id=pdf_document.id
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return JSONResponse(
        status_code=201,
        content={
            "message": "PDF uploaded successfully",
            "paper_id": paper.id,
            "pdf_id": pdf_document.id,
            "original_filename": pdf_document.filename,
            "saved_as": stored_filename,
            "file_path": file_location,
            "file_size": pdf_document.file_size
        }
    )


@router.get("/{paper_id}", response_model=Paper)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.get("/", response_model=List[Paper])
def get_papers(db: Session = Depends(get_db)):
    return db.query(Paper).all()

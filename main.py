from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import shutil

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Database setup
Base = declarative_base()
engine = create_engine("sqlite:///./database.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    content = Column(Text)


@app.post("/upload/")
async def upload(file: UploadFile = File(None), text: str = Form(None)):
    if file:
        filename = file.filename
        content = (await file.read()).decode()

    doc = Document(name=filename, content=content)
    session.add(doc)
    session.commit()
    return {"message": "Uploaded", "id": doc.id}


@app.get("/documents/")
def list_documents():
    docs = session.query(Document).all()
    return [{"id": d.id, "name": d.name} for d in docs]


@app.get("/search/")
def search(doc_id: int, query: str):
    doc = session.query(Document).filter(Document.id == doc_id).first()

    if not doc:
        return JSONResponse(status_code=404, content={"message": "Document not found"})
    
    contents = doc.content.splitlines()
    results = []

    for content in contents:
        if query.lower() in content.lower():
            results.append({"content": content})
    return results

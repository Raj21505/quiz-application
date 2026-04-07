# backend/fastapi_app.py
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from backend.schema import Quiz, init_db, engine
from backend.firebase_auth import init_firebase, verify_firebase_token
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
import logging
import os

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    init_db()
    public_base_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")
    logger.info("Swagger docs: %s/", public_base_url.rstrip("/"))
    yield

app = FastAPI(title="Quiz API", version="1.0", lifespan=lifespan, docs_url="/", redoc_url=None)
    
# Dependency to get DB session
def get_db():
    with Session(engine) as session:
        yield session

@app.get("/questions")
def get_questions(db: Session = Depends(get_db)):
    questions = db.exec(select(Quiz)).all()
    # The response model is usually a Pydantic model for lists, 
    # but using a dictionary comprehension for simplicity as done originally.
    result = [
        {
            "id": q.id,
            "Que": q.Que,
            "A": q.A,
            "B": q.B,
            "C": q.C,
            "D": q.D,
            "Ans": q.Ans
        }
        for q in questions
    ]
    return result

    
@app.get("/questions/{qid}", response_model=Quiz)
def get_question(qid: int, db: Session = Depends(get_db)):
    q = db.get(Quiz, qid)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return JSONResponse(
        content={
            "id": q.id,
            "Que": q.Que,
            "A": q.A,
            "B": q.B,
            "C": q.C,
            "D": q.D,
            "Ans": q.Ans,
        }
    )

@app.post("/questions", response_model=Quiz)
def add_question(
    q: Quiz,
    db: Session = Depends(get_db),
    _user=Depends(verify_firebase_token),
):
    # Validate and normalize the answer
    if not q.Ans or q.Ans.upper() not in ['A', 'B', 'C', 'D']:
        raise HTTPException(status_code=400, detail="Answer must be A, B, C, or D (case insensitive)")
    q.Ans = q.Ans.upper()  # Normalize to uppercase
    
    db.add(q)
    db.commit()
    db.refresh(q)
    return q

@app.put("/questions/{qid}", response_model=Quiz)
def update_question(
    qid: int,
    updated_q: Quiz,
    db: Session = Depends(get_db),
    _user=Depends(verify_firebase_token),
):
    q = db.get(Quiz, qid)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    # Use dict(exclude_unset=True) to only update fields provided in the payload
    for field, value in updated_q.model_dump(exclude_unset=True).items():
        setattr(q, field, value)

    # Validate the answer if it was updated
    if hasattr(q, 'Ans') and q.Ans is not None:
        if q.Ans.upper() not in ['A', 'B', 'C', 'D']:
            raise HTTPException(status_code=400, detail="Answer must be A, B, C, or D (case insensitive)")
        q.Ans = q.Ans.upper()  # Normalize to uppercase

    db.add(q)
    db.commit()
    db.refresh(q)
    return q

@app.delete("/questions/{qid}")
def delete_question(
    qid: int,
    db: Session = Depends(get_db),
    _user=Depends(verify_firebase_token),
):
    q = db.get(Quiz, qid)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return {"detail": "Deleted successfully"}
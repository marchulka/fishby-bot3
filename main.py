from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from supabase import create_client, Client
import os
import jwt

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

def log_attempt(user_id: str, question: str, selected: str, correct: bool):
    data = {
        "user_id": user_id,
        "question": question,
        "selected": selected,
        "correct": correct
    }
    res = supabase.table("attempts").insert(data).execute()
    return res

@app.post("/submit")
async def submit_answer(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    body = await request.json()
    
    user_id = body.get("user_id") or payload.get("sub") or "anon"
    question = body.get("question")
    selected = body.get("selected")
    correct = body.get("correct", False)

    if not question or not selected:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Missing question or selected"})

    result = log_attempt(user_id, question, selected, correct)
    return {"status": "saved", "response": result.data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

from fastapi import FastAPI, Request, Header, HTTPException
from supabase import create_client, Client
from jose import jwt, JWTError
import os

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

# Проверка валидности токена
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError as e:
        print(f"JWT verification failed: {e}")
        return None

# Запись попытки в Supabase
def log_attempt(user_id: str, question: str, selected: str, correct: bool):
    data = {
        "user_id": user_id,
        "question": question,
        "selected": selected,
        "correct": correct
    }
    res = supabase.table("attempts").insert(data).execute()
    return res

# Эндпоинт приёма ответов
@app.post("/submit")
async def submit_answer(request: Request, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.split(" ")[1]  # Отделяем "Bearer"
    payload = verify_jwt_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    body = await request.json()
    result = log_attempt(
        user_id=payload.get("sub", "anon"),
        question=body.get("question", "unknown"),
        selected=body.get("selected", "none"),
        correct=body.get("correct", False)
    )
    return {"status": "saved", "response": result.data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

from fastapi import FastAPI, Request, HTTPException
from supabase import create_client, Client
import os
import jwt
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Переменные окружения
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

# Клиент Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

# Правильная запись попытки
def log_attempt(user_id: str, question: str, selected: str, correct: bool):
    data = {
        "user_id": str(user_id),
        "question": str(question),
        "selected": str(selected),
        "correct": bool(correct)
    }
    res = supabase.table("attempts").insert(data).execute()
    return res

@app.post("/submit")
async def submit_answer(request: Request):
    try:
        # Чтение заголовка
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

        token = auth_header.split(" ")[1]

        # Проверка токена
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("sub") or payload.get("user_id") or "anon"
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logging.error(f"Invalid Token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")

        # Чтение тела запроса
        body = await request.json()
        question = body.get("question")
        selected = body.get("selected")
        correct = body.get("correct", False)

        if not question or not selected:
            raise HTTPException(status_code=400, detail="Missing 'question' or 'selected' field")

        result = log_attempt(user_id=user_id, question=question, selected=selected, correct=correct)
        return {"status": "saved", "response": result.data}

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

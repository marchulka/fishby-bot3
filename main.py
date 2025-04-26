from fastapi import FastAPI, Request
from supabase import create_client, Client
import os
import jwt
import logging

# Логи
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Подключение к Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

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
        # Чтение тела запроса
        body = await request.json()

        # Проверка токена
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise Exception("Missing Authorization Header")

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            logging.info(f"Payload: {payload}")
        except jwt.InvalidTokenError:
            raise Exception("Invalid JWT Token")

        # Получение данных с проверкой типов
        user_id = str(body.get("user_id", "anon"))
        question = str(body.get("question", "unknown"))
        selected = str(body.get("selected", "none"))
        correct = bool(body.get("correct", False))

        # Логирование попытки
        result = log_attempt(user_id, question, selected, correct)
        return {"status": "saved", "response": result.data}

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"detail": f"Internal Server Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

from fastapi import FastAPI, Request, HTTPException
from supabase import create_client, Client
from jose import jwt, JWTError
import os
import logging

# Инициализация FastAPI приложения
app = FastAPI()

# Конфигурация Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Логирование ошибок
logging.basicConfig(level=logging.INFO)

# Эндпоинт для проверки работы сервера
@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

# Функция записи попытки в базу
def log_attempt(user_id: str, question: str, selected: str, correct: bool):
    data = {
        "user_id": user_id,
        "question": question,
        "selected": selected,
        "correct": str(correct).lower()  # <-- Ключевая правка здесь
    }
    res = supabase.table("attempts").insert(data).execute()
    return res

# Эндпоинт для отправки ответа пользователя
@app.post("/submit")
async def submit_answer(request: Request):
    try:
        # Чтение токена из заголовка
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        token = auth_header.split(" ")[1]

        # Проверка валидности токена
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except JWTError as e:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Получение данных запроса
        body = await request.json()

        result = log_attempt(
            user_id=body.get("user_id", "anon"),
            question=body.get("question", "unknown"),
            selected=body.get("selected", "none"),
            correct=body.get("correct", False)
        )

        return {"status": "saved", "response": result.data}

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# Запуск сервера локально
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

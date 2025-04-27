# Импортируем нужные библиотеки
from fastapi import FastAPI, Request
from supabase import create_client, Client
from jose import jwt
import os
import logging

# Создаём экземпляр FastAPI-приложения
app = FastAPI()

# Подключение к Supabase с использованием переменных окружения
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

# Создаём клиента Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Конфигурация логирования
logging.basicConfig(level=logging.INFO)

# Эндпоинт для проверки жизни сервера
@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

# Функция для логирования попытки в базу данных Supabase
def log_attempt(user_id: str, question: str, selected: str, correct: bool, bot_id: str):
    data = {
        "user_id": user_id,
        "question": question,
        "selected": selected,
        "correct": correct,
        "bot_id": bot_id,
    }
    res = supabase.table("attempts").insert(data).execute()
    return res

# Эндпоинт для приёма ответа от пользователя и логирования
@app.post("/submit")
async def submit_answer(request: Request):
    try:
        body = await request.json()

        # Получение заголовка Authorization
        token = request.headers.get('Authorization')
        if not token:
            raise ValueError("Authorization header missing")
        token = token.replace('Bearer ', '')

        # Декодируем токен, чтобы достать bot_id
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        bot_id = decoded.get("bot_id", "default_bot")  # если нет bot_id - ставим дефолт

        # Логируем попытку
        result = log_attempt(
            user_id=body.get("user_id", "anon"),
            question=body.get("question", "unknown"),
            selected=body.get("selected", "none"),
            correct=body.get("correct", False),
            bot_id=bot_id
        )

        return {"status": "saved", "response": result.data}

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"status": "error", "message": str(e)}

# Стандартный запуск uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

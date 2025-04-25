# Импортируем нужные библиотеки
from fastapi import FastAPI, Request
from supabase import create_client, Client
import os

# Создаём экземпляр FastAPI-приложения
app = FastAPI()

# Подключение к Supabase с использованием переменных окружения
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Создаём клиента Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Эндпоинт для проверки жизни сервера
@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

# Функция для записи попытки в базу данных Supabase
def log_attempt(user_id: str, question: str, selected: str, correct: bool):
    data = {
        "user_id": user_id,
        "question": question,
        "selected": selected,
        "correct": correct
    }
    # Отправляем данные в таблицу attempts
    res = supabase.table("attempts").insert(data).execute()
    return res

# Эндпоинт для приёма ответа от пользователя и логирования его в базу
@app.post("/submit")
async def submit_answer(request: Request):
    body = await request.json()
    result = log_attempt(
        user_id=body.get("user_id", "anon"),
        question=body.get("question", "unknown"),
        selected=body.get("selected", "none"),
        correct=body.get("correct", False)
    )
    return {"status": "saved", "response": result.data}

# Стандартный запуск приложения через uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

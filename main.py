# Импорт нужных библиотек
from fastapi import FastAPI, Request
from supabase import create_client, Client
import os
import logging
from jose import jwt

# Создание экземпляра FastAPI
app = FastAPI()

# Подключение к Supabase через переменные окружения
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

# Логирование состояния загрузки переменных
if JWT_SECRET:
    logging.info(f"JWT_SECRET detected and loaded.")
else:
    logging.error("JWT_SECRET is missing!")

# Создание клиента Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Эндпоинт проверки работоспособности
@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

# Функция логирования попытки в базу данных
def log_attempt(user_id: str, question: str, selected: str, correct: bool, bot_id: str):
    data = {
        "user_id": user_id,
        "question": question,
        "selected": selected,
        "correct": correct,
        "bot_id": bot_id
    }
    res = supabase.table("attempts").insert(data).execute()
    return res

# Эндпоинт приёма ответов и логирования попыток
@app.post("/submit")
async def submit_answer(request: Request):
    try:
        body = await request.json()

        bot_id = "default_bot"
        token = request.headers.get('Authorization')
        if token:
            try:
                token = token.replace('Bearer ', '')
                decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                bot_id = decoded.get("bot_id", "default_bot")
            except Exception as token_error:
                logging.error(f"!!! TOKEN DECODE ERROR: {str(token_error)}")

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

# Стандартный запуск через uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

# Импорт библиотек
from fastapi import FastAPI, Request, HTTPException
from supabase import create_client, Client
import os
import jwt
import logging

# Логирование ошибок
logging.basicConfig(level=logging.INFO)

# Инициализация FastAPI-приложения
app = FastAPI()

# Настройки Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Проверка сервера
@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

# Функция записи попытки в базу
def log_attempt(user_id: str, question: str, selected: str, correct: bool):
    try:
        data = {
            "user_id": user_id,
            "question": question,
            "selected": selected,
            "correct": True if correct else False,  # Строгое преобразование
        }
        res = supabase.table("attempts").insert(data).execute()
        return res
    except Exception as e:
        logging.error(f"Unexpected error during log_attempt: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Проверка JWT токена
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logging.error("JWT token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        logging.error("Invalid JWT token")
        raise HTTPException(status_code=401, detail="Invalid token")

# Приём ответа пользователя
@app.post("/submit")
async def submit_answer(request: Request):
    try:
        # Проверка заголовков
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or malformed")

        token = auth_header.split(" ")[1]
        verify_jwt_token(token)

        # Чтение тела запроса
        body = await request.json()
        result = log_attempt(
            user_id=body.get("user_id", "anon"),
            question=body.get("question", "unknown"),
            selected=body.get("selected", "none"),
            correct=body.get("correct", False),
        )
        return {"status": "saved", "response": result.data}
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

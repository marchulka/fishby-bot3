from fastapi import FastAPI, Request, HTTPException
from supabase import create_client, Client
from jose import jwt
import os
import logging
import datetime

# Инициализация FastAPI
app = FastAPI()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Переменные окружения
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

# Проверка переменных
if not SUPABASE_URL or not SUPABASE_KEY or not JWT_SECRET:
    raise Exception("Одна из переменных окружения отсутствует!")

# Создание клиента Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------- ЭНДПОИНТЫ --------------------

# Эндпоинт: проверка сервера
@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

# Эндпоинт: просмотр переменных окружения
@app.get("/env-check")
async def env_check():
    return {
        "supabase_url_preview": SUPABASE_URL[:20],
        "supabase_key_preview": SUPABASE_KEY[:10],
        "jwt_secret_preview": JWT_SECRET[:10]
    }

# Эндпоинт: проверка валидности токена
@app.get("/token-check")
async def token_check(request: Request):
    try:
        token = request.headers.get('Authorization')
        if not token:
            raise HTTPException(status_code=401, detail="Токен отсутствует")
        token = token.replace('Bearer ', '')
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {"status": "decoded", "payload": payload}
        except Exception as e:
        logging.error(f"TOKEN DECODE ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}

# Эндпоинт: генерация нового токена
@app.get("/generate-token")
async def generate_token():
    try:
        payload = {
            "bot_id": "fishby_main_bot",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return {
            "status": "token_generated",
            "token": token
        }
    except Exception as e:
        logging.error(f"GENERATE TOKEN ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}

# Эндпоинт: приём ответа студента
@app.post("/submit")
async def submit_answer(request: Request):
    try:
        body = await request.json()

        # Достаём токен
        token = request.headers.get('Authorization')
        if not token:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        token = token.replace('Bearer ', '')

        # Декодируем токен
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            bot_id = decoded_token.get("bot_id", "default_bot")
        except Exception as e:
            logging.error(f"TOKEN DECODE FAILED: {str(e)}")
            bot_id = "default_bot"

        # Формируем данные для записи
        data = {
            "user_id": body.get("user_id", "anon"),
            "bot_id": bot_id,
            "session_id": body.get("session_id"),
            "branch_id": body.get("branch_id"),
            "theme": body.get("theme"),
            "question_id": body.get("question_id"),
            "question_text": body.get("question_text"),
            "arrow_pattern": body.get("arrow_pattern"),
            "bloom_level": body.get("bloom_level"),
            "fishbi_lvl": body.get("fishbi_lvl"),
            "attempt_number": body.get("attempt_number"),
            "time_spent": body.get("time_spent"),
            "device_type": body.get("device_type"),
            "platform": body.get("platform"),
            "network_type": body.get("network_type"),
            "answer_selected": body.get("answer_selected"),
            "answer_correct": body.get("answer_correct"),
            "answer_text_expected": body.get("answer_text_expected"),
            "speech_to_text": body.get("speech_to_text"),
            "audio_url": body.get("audio_url"),
            "emotion_detected": body.get("emotion_detected"),
            "confidence_score": body.get("confidence_score"),
            "gpt_analysis": body.get("gpt_analysis"),
            "commentary_read": body.get("commentary_read"),
            "hints_used": body.get("hints_used"),
            "attempt_success_on_retry": body.get("attempt_success_on_retry"),
            "reflection_text": body.get("reflection_text"),
            "metacognitive_pause": body.get("metacognitive_pause"),
            "transfer_case_success": body.get("transfer_case_success"),
            "strategy_selected": body.get("strategy_selected"),
            "error_category": body.get("error_category"),
            "mental_load_rating": body.get("mental_load_rating"),
            "successive_correct_streak": body.get("successive_correct_streak"),
            "attention_lapse": body.get("attention_lapse"),
            "meta_data": body.get("meta_data"),
        }

        # Логируем попытку
        response = supabase.table("attempts").insert(data).execute()

        if response.status_code != 201:
            logging.error(f"Ошибка при записи в Supabase: {response.data}")
            raise HTTPException(status_code=500, detail="Ошибка записи в базу")
        
        return {"status": "saved", "response": response.data}

    except Exception as e:
        logging.error(f"Unexpected error in /submit: {str(e)}")
        return {"status": "error", "message": str(e)}

# Для локального запуска
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

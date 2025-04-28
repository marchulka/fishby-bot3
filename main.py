from fastapi import FastAPI, Request, HTTPException
from supabase import create_client, Client
from jose import jwt
import os
import logging

# Создаём экземпляр FastAPI-приложения
app = FastAPI()

# Подключение к Supabase через переменные окружения
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

# 🧠 ДОБАВЛЕНО логирование секрета
print(f"Текущий JWT_SECRET: {JWT_SECRET} (len={len(JWT_SECRET)})")

if not all([SUPABASE_URL, SUPABASE_KEY, JWT_SECRET]):
    raise Exception("Одна из переменных окружения отсутствует!")

# Создаём клиента Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Конфиг логов
logging.basicConfig(level=logging.INFO)

# Эндпоинт для проверки жизни сервера
@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

# Эндпоинт для проверки токена
@app.get("/token-check")
async def token_check(request: Request):
    try:
        token = request.headers.get('Authorization')
        if not token:
            raise HTTPException(status_code=401, detail="Токен отсутствует")
        token = token.replace('Bearer ', '')
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {"status": "decoded", "payload": decoded}
    except Exception as e:
        logging.error(f"TOKEN CHECK ERROR: {str(e)}")
        raise HTTPException(status_code=401, detail="Ошибка проверки токена")

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
        bot_id = decoded.get("bot_id", "default_bot")

        # Подготавливаем данные для записи
        data = {
            "user_id": body.get("user_id", "anon"),
            "question": body.get("question", "unknown"),
            "selected": body.get("selected", "none"),
            "correct": body.get("correct", False),
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
            "commentary_listened": body.get("commentary_listened"),
            "user_note": body.get("user_note"),
            "answer_format": body.get("answer_format"),
            "input_method": body.get("input_method"),
            "tts_used": body.get("tts_used"),
            "gpt_version": body.get("gpt_version"),
            "gpt_prompt": body.get("gpt_prompt"),
            "gpt_response": body.get("gpt_response"),
            "gpt_score": body.get("gpt_score"),
            "meta_json": body.get("meta_json"),
            "meta_data": body.get("meta_data"),
            "is_skipped": body.get("is_skipped"),
            "user_emotion": body.get("user_emotion"),
            "commentary_quality": body.get("commentary_quality"),
            "bot_suggestion": body.get("bot_suggestion"),
            "teacher_comment": body.get("teacher_comment"),
            "next_best_step": body.get("next_best_step"),
            "created_by_bot": body.get("created_by_bot"),
            "verified_by_teacher": body.get("verified_by_teacher"),
            "error_category": body.get("error_category"),
            "hints_used": body.get("hints_used"),
            "mental_load_rating": body.get("mental_load_rating"),
            "attempt_success_on_retry": body.get("attempt_success_on_retry"),
            "attention_lapse": body.get("attention_lapse"),
            "metacognitive_pause": body.get("metacognitive_pause"),
            "reflection_text": body.get("reflection_text"),
            "strategy_selected": body.get("strategy_selected"),
            "successive_correct_streak": body.get("successive_correct_streak"),
            "transfer_case_success": body.get("transfer_case_success")
        }

        # Записываем попытку в базу
        response = supabase.table("attempts").insert(data).execute()

        # Проверка через .data
        if not response.data:
            logging.error(f"Ошибка при записи в Supabase: {response}")
            raise HTTPException(status_code=500, detail="Ошибка записи в базу")

        return {"status": "saved", "response": response.data}

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"status": "error", "message": str(e)}

# Стандартный запуск через uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

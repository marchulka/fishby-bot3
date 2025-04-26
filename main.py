from fastapi import FastAPI, Request
from supabase import create_client, Client
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# Подключаемся к Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Проверка, что сервер жив
@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

# Обработка отправки ответа
@app.post("/submit")
async def submit_answer(request: Request):
    try:
        body = await request.json()
        user_id = body.get("user_id", "anon")
        question = body.get("question", "unknown")
        selected = body.get("selected", "none")
        correct = body.get("correct", False)

        # Сохраняем в базу
        response = supabase.table("attempts").insert({
            "user_id": user_id,
            "question": question,
            "selected": selected,
            "correct": correct
        }).execute()

        # Проверка, что вставка успешна
        if hasattr(response, "data") and response.data:
            return {"status": "saved", "response": response.data}
        else:
            return JSONResponse(status_code=500, content={
                "status": "error",
                "message": "Insert failed or no data returned",
                "details": str(response)
            })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

# Локальный запуск
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

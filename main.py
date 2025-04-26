from fastapi import FastAPI, Request
from supabase import create_client, Client
from fastapi.responses import JSONResponse
import os

app = FastAPI()

@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

@app.post("/submit")
async def submit_answer(request: Request):
    try:
        # 🔁 Инициализируем клиент только внутри запроса (если переменные заданы)
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            return JSONResponse(status_code=500, content={
                "status": "error",
                "message": "Supabase credentials not found in environment variables."
            })

        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        body = await request.json()
        user_id = body.get("user_id", "anon")
        question = body.get("question", "unknown")
        selected = body.get("selected", "none")
        correct = body.get("correct", False)

        response = supabase.table("attempts").insert({
            "user_id": user_id,
            "question": question,
            "selected": selected,
            "correct": correct
        }).execute()

        if hasattr(response, "data") and response.data:
            return {"status": "saved", "response": response.data}
        else:
            return JSONResponse(status_code=500, content={
                "status": "error",
                "message": "Insert failed or empty response",
                "details": str(response)
            })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

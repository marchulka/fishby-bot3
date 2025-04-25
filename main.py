from fastapi import FastAPI

app = FastAPI()

@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

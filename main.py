from fastapi import FastAPI

app = FastAPI()

@app.get("/next-task")
async def next_task():
    return {"status": "ok", "message": "Server is live!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

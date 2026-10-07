from fastapi import FastAPI

app = FastAPI(title="Enterprise AI Resume Generator")

@app.get("/health")
def health():
    return {"status": "ok"}
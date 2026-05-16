from fastapi import FastAPI

app = FastAPI(title="ai-runtime")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "ai-runtime"}

from fastapi import FastAPI
from server.routers.upload import router as upload_router

app = FastAPI()

app.include_router(upload_router)

@app.get("/health")
def health():
    return {"status": "ok"}
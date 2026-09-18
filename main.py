from fastapi import FastAPI

from app.controllers.ask_controller import ask_router
from app.controllers.ingestion_controller import ingestion_router
from app.controllers.upload_file_controller import upload_router
from app.services.bm25_service import BM25Service

app = FastAPI()

app.include_router(upload_router)
app.include_router(ingestion_router)
app.include_router(ask_router)

app.state.bm25_service = BM25Service()

if __name__ == "__main__":
   import uvicorn
   uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
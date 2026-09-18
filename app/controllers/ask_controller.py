from fastapi import APIRouter, Depends

from fastapi_restful.cbv import cbv

from app.utils.bm25 import get_bm25_service
from app.services.ask_service import AskService
from app.services.bm25_service import BM25Service


ask_router = APIRouter(
    prefix="/ask",
    tags=["Ask"],
)


@cbv(ask_router)
class AskController:

    @ask_router.post("/query")
    def ask(
        self,
        query: str,
        bm25_service: BM25Service = Depends(
            get_bm25_service
        ),
    ):
        ask_service = AskService(
            bm25_service=bm25_service
        )

        results = ask_service.ask(query)

        return {
            "query": query,
            "results": results,
        }
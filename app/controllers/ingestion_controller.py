from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from starlette.status import HTTP_200_OK

from app.services.bm25_service import BM25Service
from app.services.ingestion_service import IngestionService
from app.utils.bm25 import get_bm25_service


ingestion_router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"],
)


@cbv(ingestion_router)
class IngestionController:

    @ingestion_router.post(
        "/build-index",
        status_code=HTTP_200_OK,
    )
    def build_index(
        self,
        bm25_service: BM25Service = Depends(
            get_bm25_service
        ),
    ):
        ingestion_service = IngestionService(
            bm25_service=bm25_service
        )

        result = ingestion_service.build_index()

        return {
            "success": True,
            **result,
        }

    @ingestion_router.post(
        "/{file_id}",
        status_code=HTTP_200_OK,
    )
    def ingest_file(
        self,
        file_id: str,
    ):
        ingestion_service = IngestionService()

        result = ingestion_service.ingest_file(
            file_id=file_id
        )

        return {
            "success": True,
            **result,
        }
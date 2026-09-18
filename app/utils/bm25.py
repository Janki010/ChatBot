from fastapi import Request

from app.services.bm25_service import BM25Service

def get_bm25_service(
    request: Request,
) -> BM25Service:
    return request.app.state.bm25_service
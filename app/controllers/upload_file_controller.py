from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv
from starlette.status import  HTTP_200_OK

from app.schemas.file_validate import FileValidator
from app.services.upload_file_service import UploadFileService

upload_router = APIRouter(prefix="/upload", tags=["Uploads"])

@cbv(upload_router)
class UploadFileController:
    def __init__(self):
        self.upload_service = UploadFileService()

    @upload_router.post(
        "/file",
        status_code=HTTP_200_OK,
        summary="Upload File",
    )
    def upload_file(self, file: UploadFile = File(...)):
        validation_errors = FileValidator.validate_file(file)

        if validation_errors:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "errors": validation_errors,
                },
            )

        file_id = self.upload_service.upload_file(file)

        return {"file_id": str(file_id)}


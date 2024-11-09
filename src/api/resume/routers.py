import os
import uuid
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from typing import Annotated
from pydantic import BaseModel
from sqlalchemy import insert
from db.base import async_session
from db.models import Resume

from fastapi import (APIRouter, HTTPException, Path, Query, Response, UploadFile, status)
from fastapi.responses import StreamingResponse

router = APIRouter(
    prefix="/resume",
    tags=["reume"],
)


BUCKET_NAME = "my-first-bucket"

s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id=os.getenv('ACCESS_KEY'),
    aws_secret_access_key=os.getenv('SECRET_KEY'),
    region_name='ru-central-1'
)


try:
    s3_client.create_bucket(Bucket=BUCKET_NAME)
except s3_client.exceptions.BucketAlreadyOwnedByYou:
    print(f'bucket {BUCKET_NAME} is already create')
except s3_client.exceptions.BucketAlreadyExists:
    pass



@router.post("/upload/")
async def upload_file(file: UploadFile, username: Annotated[str, Query()]):
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, file.filename)
        async with async_session() as session:
            query = insert(Resume).values(name=username, file_name=file.filename)
            await session.execute(query)
            await session.commit()

        return Response(status_code=status.HTTP_201_CREATED)

    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="Credentials not available")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/download/{filename}")
async def download_file(filename: Annotated[str, Path()]):
    try:
        file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=filename)
        return StreamingResponse(file_obj['Body'], media_type="application/octet-stream")
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
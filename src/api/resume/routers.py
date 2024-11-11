import os
import boto3
from botocore.exceptions import NoCredentialsError
from sqlalchemy import insert, select
from typing import Annotated, List

from db.base import async_session
from db.models import Resume
from .schemas import Files

from fastapi import (APIRouter, File, HTTPException, Path, Query, Response, UploadFile, status)

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

#  -> HTTPException | Response
#  -> HTTPException | List[Files]

@router.post("/upload/")
async def upload_resume(file: UploadFile, username: Annotated[str, Query(max_length=32)]) -> Response:
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


@router.delete("/delete/{filename}")
async def delete_resume(filename: Annotated[str, Path(max_length=128)]) -> Response:
    try:
        file_obj = s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
        async with async_session() as session:
            query = select(Resume).filter_by(file_name=filename)
            result = await session.execute(query)
            resume_to_delete = result.scalar_one_or_none()
            await session.delete(resume_to_delete)
            await session.commit()
        return Response(status_code=status.HTTP_201_CREATED)
    
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/list/")
async def resume_list() -> list[Files]:
    try:
        async with async_session() as session:
            query = select(Resume)
            result = await session.execute(query)
            resumes = result.scalars().all()
        result: list[Files] = []
        for resume in resumes:
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': resume.file_name},
                ExpiresIn=3600  # Время жизни URL в секундах
            )
            result.append(Files(name=resume.name, filepath=presigned_url))
        return result
    
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
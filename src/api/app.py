from fastapi import FastAPI
from .resume.routers import router as resume_router

def create_app():
    app = FastAPI()
    
    app.include_router(resume_router)

    return app
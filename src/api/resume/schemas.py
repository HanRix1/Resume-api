from pydantic import BaseModel


class Files(BaseModel):
    name : str
    filepath: str

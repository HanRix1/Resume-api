from db import Base
from uuid import UUID, uuid4
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Resume(Base):
    __tablename__ = "resume"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    file_name: Mapped[str] = mapped_column(String(128), nullable=False)
    # file_path: Mapped[str] = mapped_column(String(256), nullable=False)
    

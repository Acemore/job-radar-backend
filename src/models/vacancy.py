from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class VacancyModel(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    company_name: Mapped[str] = mapped_column()
    salary: Mapped[str] = mapped_column()
    link: Mapped[str] = mapped_column(index=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

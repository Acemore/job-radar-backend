from pydantic import BaseModel


class VacancyResponse(BaseModel):
    title: str
    company_name: str

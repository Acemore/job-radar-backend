from pydantic import BaseModel, ConfigDict


class VacancyDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, frozen=True, str_strip_whitespace=True
    )

    title: str
    company_name: str
    salary: str
    link: str


class VacancyResponse(BaseModel):
    title: str
    company_name: str
    salary: str
    link: str

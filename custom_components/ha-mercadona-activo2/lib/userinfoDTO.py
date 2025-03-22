from typing import List
from pydantic import BaseModel, Field


class Company(BaseModel):
    code: str
    name: str
    employee_number: str
    active: bool


# class Sustainability(BaseModel):
#     paper_reception: bool
#     show_warning: bool
#     show_reminder: bool


class UserDTO(BaseModel):
    userid: str
    name: str
    lastname: str
    email: str
    alias: str
    photo: str
    is_new_employee: bool
    company: str
    cod_company: str
    cod_department: str
    department: str
    cod_division_zone: str
    division_zone: str
    cod_store: str
    store: str
    cod_region: str
    region: str
    companies: List[Company]
    language_code: str
    language_name: str
    language_country: str
    external: bool
    acceptLegal: bool
    legalConditionsType: str
    #permissions: List[str]
    #news: List[Any]
    internal_user_id: str
    #segments: List[Any]
    #sustainability: Sustainability
    hasEverAcceptedLegal: bool
    city: str
    cod_city: str
    cod_province: str
    province: str
    banned: bool
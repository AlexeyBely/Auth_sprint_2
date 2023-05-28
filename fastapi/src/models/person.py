from models.mixins import OrjsonMixin
from pydantic import Field


class Person(OrjsonMixin):
    id: str
    full_name: str = Field(alias='name')

    class Config:
        allow_population_by_field_name = True

from models.mixins import OrjsonMixin


class Genre(OrjsonMixin):
    id: str
    name: str
    description: str

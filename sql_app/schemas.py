from pydantic import BaseModel


class CoilInputModel(BaseModel):
    length: float
    weight: float
    add_date: str | None = None
    del_date: str | None = None

    class ConfigDict:
        from_atributes = True


class CoilModel(CoilInputModel):
    id: int = 0

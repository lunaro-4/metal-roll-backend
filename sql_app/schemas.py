from pydantic import BaseModel



class Coil(BaseModel):
    id : int
    length : float
    weight : float
    add_date : str
    del_date : str | None = None

    class Config:
        orm_mode = True

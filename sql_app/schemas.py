from pydantic import BaseModel
from typing import Optional



class CoilModel(BaseModel):
    id : int  = 0  
    length : float
    weight : float
    add_date : str | None = None
    # del_date : Optional[str]
    del_date : str | None = None

    class Config:
        orm_mode = True

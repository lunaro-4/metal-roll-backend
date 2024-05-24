from sqlalchemy import Column, Date, Integer, Float
from sqlalchemy.orm import relationship

from .database import Base

class CoilBase(Base):
    __tablename__ = "coils"
    
    # id = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, primary_key=True)
    length = Column(Float)
    weight = Column(Float)
    add_date = Column(Date)
    del_date = Column(Date, nullable=True)

    def __init__(self, length, weight, add_date, del_date = None):
        self.length = length
        self.weight = weight
        self.add_date = add_date
        self.del_date = del_date



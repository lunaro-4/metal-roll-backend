from sqlalchemy import Column, Date, Integer, Float
from sqlalchemy.orm import relationship

from .database import Base

class Coil(Base):
    __tablename__ = "coils"
    
    id = Column(Integer, primary_key=True)
    length = Column(Float)
    weight = Column(Float)
    add_date = Column(Date)
    del_date = Column(Date, nullable=True)



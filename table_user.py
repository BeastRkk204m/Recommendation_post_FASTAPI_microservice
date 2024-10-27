from database import Base, engine, SessionLocal
from sqlalchemy import Column, String, Integer, func, ForeignKey, TIMESTAMP



class User (Base):
    __tablename__ = "user_data"
    __table_args__ = {"schema": "public"}
    age = Column (Integer)
    city = Column (String)
    country = Column (String)
    exp_group = Column (Integer)
    gender = Column (Integer)
    user_id = Column (Integer, primary_key=True)
    os = Column (String)
    source = Column (String)
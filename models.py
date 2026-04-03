from sqlalchemy import Column, Integer, String, Text, Float
from db import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    description = Column(Text)
    link = Column(String)
    match_score = Column(Float, default=0.0)

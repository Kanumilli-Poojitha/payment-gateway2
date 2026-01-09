from sqlalchemy import Column, String
from database import Base

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    api_secret = Column(String, nullable=False)
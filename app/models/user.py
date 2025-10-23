from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    """Modelo de usuário para o sistema bancário"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, nullable=False, name="password")
    accounts = relationship("Account", back_populates="owner", lazy="selectin")

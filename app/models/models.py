from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


class Users(Base):
    __tablename__ = "Users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True)
    password = Column(String(20))
    role = Column(String(20), default="Analyst")
    group_id = Column(Integer, ForeignKey("Groups.id"), nullable=True)

    group = relationship("Groups")

    
class Groups(Base):
    __tablename__ = "Groups"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)


class Tickets(Base):
    __tablename__ = "Tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="Open", nullable=False)
    note = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=True)
    group_id = Column(Integer, ForeignKey("Groups.id"), nullable=True)

    user = relationship("Users")
    group = relationship("Groups")

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Bank(Base):
    __tablename__ = "banks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)

    branches: Mapped[list["Branch"]] = relationship(back_populates="bank")

class Branch(Base):
    __tablename__ = "branches"
    ifsc: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    bank_id: Mapped[int] = mapped_column(ForeignKey("banks.id"), index=True)
    branch: Mapped[str] = mapped_column(String, index=True)
    address: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String, index=True)
    district: Mapped[str] = mapped_column(String, index=True)
    state: Mapped[str] = mapped_column(String, index=True)

    bank: Mapped["Bank"] = relationship(back_populates="branches")
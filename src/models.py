from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__="products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    protein: Mapped[float]
    fat: Mapped[float]
    carbs: Mapped[float]
    calories: Mapped[float]
    active: Mapped[bool]
    description: Mapped[str | None] = mapped_column(nullable=True)
    
    logs: Mapped[list["Log"]] = relationship(back_populates="product")
    
class Log(Base):
    __tablename__="logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    weight: Mapped[float]
    protein: Mapped[float]
    fat: Mapped[float]
    carbs: Mapped[float]
    calories: Mapped[float]
    date: Mapped[str]
    product: Mapped["Product"] = relationship(back_populates="logs")



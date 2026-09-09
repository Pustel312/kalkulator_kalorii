from sqlalchemy import ForeignKey, CheckConstraint, text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date


class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__="products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    protein: Mapped[float]
    fat: Mapped[float]
    carbs: Mapped[float]
    calories: Mapped[float]
    active: Mapped[bool]
    description: Mapped[str | None] = mapped_column(nullable=True)
    
    logs: Mapped[list["Log"]] = relationship(back_populates="product")
    #P from Products for args
    __table_args__ = (
        CheckConstraint("protein >= 0", name="Pprotein_nonnegative"),
        CheckConstraint("fat >= 0", name="Pfat_nonnegative"),
        CheckConstraint("carbs >= 0", name="Pcarbs_nonnegative"),
        CheckConstraint("calories >= 0", name="Pcalories_nonnegative"),
        Index(
            "uq_active_product_name",
            "name",
            unique=True,
            postgresql_where=text("active IS TRUE")
        )
    )
    
class Log(Base):
    __tablename__="logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    weight: Mapped[float]
    protein: Mapped[float]
    fat: Mapped[float]
    carbs: Mapped[float]
    calories: Mapped[float]
    date: Mapped[date]
    product: Mapped["Product"] = relationship(back_populates="logs")
    #L from Logs for args
    __table_args__ = (
        CheckConstraint("weight > 0", name="Lweight_higher_than_zero"),
        CheckConstraint("protein >= 0", name="Lprotein_nonnegative"),
        CheckConstraint("fat >= 0", name="Lfat_nonnegative"),
        CheckConstraint("carbs >= 0", name="Lcarbs_nonnegative"),
        CheckConstraint("calories >= 0", name="Lcalories_nonnegative"),
    )

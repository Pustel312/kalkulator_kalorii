from sqlalchemy import ForeignKey, CheckConstraint, text, Index, Enum as SqlEnum, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date as Date, datetime, timezone
from src.enums import ProductType, UserProfileActivityLevel, UserProfileWeightGoalRate, UserProfileSex
from decimal import Decimal
class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__="products"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str]
    type: Mapped[ProductType] = mapped_column(SqlEnum(ProductType, name="product_type"))
    protein: Mapped[float]
    fat: Mapped[float]
    carbs: Mapped[float]
    calories: Mapped[float]
    active: Mapped[bool]
    is_global: Mapped[bool] = mapped_column(default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    
    logs: Mapped[list["Log"]] = relationship(back_populates="product")
    user: Mapped["User"] = relationship(back_populates="products")
    components: Mapped[list["ProductComponent"]] = relationship(
        back_populates="parent_product", 
        foreign_keys="ProductComponent.parent_product_id"
        )
    used_in: Mapped[list["ProductComponent"]] = relationship(
        back_populates="component_product",
        foreign_keys="ProductComponent.component_product_id"
        )
        
    #P from Products for args
    __table_args__ = (
        CheckConstraint("protein >= 0", name="Pprotein_nonnegative"),
        CheckConstraint("fat >= 0", name="Pfat_nonnegative"),
        CheckConstraint("carbs >= 0", name="Pcarbs_nonnegative"),
        CheckConstraint("calories >= 0", name="Pcalories_nonnegative"),
        Index(
            "uq_active_product_name",
            "owner_id",
            "name",
            unique=True,
            postgresql_where=text("active IS TRUE")
        ),
        Index(
            "uq_active_global_product_name",
            "name",
            unique=True,
            postgresql_where=text("active IS TRUE AND is_global IS TRUE")
        )
    )

class ProductComponent(Base):
    __tablename__="product_components"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    component_product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    weight: Mapped[float]

    parent_product: Mapped[Product] = relationship(back_populates="components", foreign_keys=[parent_product_id])
    component_product: Mapped[Product] = relationship(back_populates="used_in", foreign_keys=[component_product_id])

    __table_args__ = (
        CheckConstraint("weight > 0", name="PCweight_higher_than_zero"),
    )

class Log(Base):
    __tablename__="logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product_type: Mapped[ProductType] = mapped_column(SqlEnum(ProductType, name="product_type"))
    weight: Mapped[float]
    protein: Mapped[float]
    fat: Mapped[float]
    carbs: Mapped[float]
    calories: Mapped[float]
    date: Mapped[Date] = mapped_column(index=True)

    user: Mapped["User"] = relationship(back_populates="logs")
    product: Mapped["Product"] = relationship(back_populates="logs")
    #L from Logs for args
    __table_args__ = (
        CheckConstraint("weight > 0", name="Lweight_higher_than_zero"),
        CheckConstraint("protein >= 0", name="Lprotein_nonnegative"),
        CheckConstraint("fat >= 0", name="Lfat_nonnegative"),
        CheckConstraint("carbs >= 0", name="Lcarbs_nonnegative"),
        CheckConstraint("calories >= 0", name="Lcalories_nonnegative"),
    )

class User(Base):
    __tablename__="users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc)) #zwraca jako date aktualny moment w ktorym utworzone zostalo konto

    userprofile: Mapped["UserProfile"] = relationship(back_populates="user", cascade="all, delete-orphan")
    products: Mapped[list["Product"]] = relationship(back_populates="user")
    logs: Mapped[list["Log"]] = relationship(back_populates="user")

class UserProfile(Base):
    __tablename__="userprofiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    sex: Mapped[UserProfileSex] = mapped_column(SqlEnum(UserProfileSex, name="sex"))
    height: Mapped[int] = mapped_column(nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    birth_date: Mapped[Date]
    activity_level: Mapped[UserProfileActivityLevel] = mapped_column(SqlEnum(UserProfileActivityLevel, name="activity_level"), default=UserProfileActivityLevel.moderate, nullable=False)
    goal: Mapped[UserProfileWeightGoalRate] = mapped_column(SqlEnum(UserProfileWeightGoalRate, name="goal_rate"), default=UserProfileWeightGoalRate.maintenance, nullable=False)

    user: Mapped["User"] = relationship(back_populates="userprofile")

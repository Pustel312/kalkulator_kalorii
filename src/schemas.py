from pydantic import BaseModel, Field, EmailStr
from datetime import date as Date, datetime
from src.enums import ProductType
# # # # # # # # # # # # # # # # # # # # # # # # PRODUCTS # # # # # # # # # # # # # # # # # # # # # # # #


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Nazwa produktu")
    type: ProductType = Field(..., description="Typ produktu")
    protein: float = Field(..., ge=0, description="Białko w 100g (>=0)")
    fat: float = Field(..., ge=0, description="Tłuszcze w 100g (>=0)")
    carbs: float = Field(..., ge=0, description="Węglowodany w 100g (>=0)")


class ProductResponse(ProductCreate):
    id: int
    calories: float

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    name: str | None = Field(..., min_length=1, description="Nazwa produktu")
    type: ProductType = Field(..., description="Typ produktu")
    protein: float | None = Field(default=None, ge=0)
    fat: float | None = Field(default=None, ge=0)
    carbs: float | None = Field(default=None, ge=0)

# # # # # # # # # # # # # # # # # # # # # # # # COMPONENTS # # # # # # # # # # # # # # # # # # # # # # # #

class ProductComponentCreate(BaseModel):
    product_id: int
    weight: float = Field(..., gt=0, description="Waga komponentu")
    
class ProductCreateComposed(BaseModel):
    name: str = Field(..., min_length=1, description="Nazwa produktu")
    type: ProductType = Field(..., description="Typ produktu")
    components: list[ProductComponentCreate] = Field(..., min_length=1, description="Komponenty")
class ProductComponentDetails(BaseModel):
    product_id: int
    name: str
    weight: float
class ProductComponentResult(BaseModel):
    id: int
    name: str = Field(..., min_length=1, description="Nazwa produktu")
    components: list[ProductComponentDetails] = Field(..., min_length=1, description="Komponenty")
# # # # # # # # # # # # # # # # # # # # # # # # LOGS # # # # # # # # # # # # # # # # # # # # # # # #
    
class LogCreate(BaseModel):
    product_id: int = Field(..., ge=0, description="Id produktu")
    weight: float = Field(..., ge=0, description="Waga produktu")

class LogResponse(BaseModel):
    id: int
    product_type: ProductType
    protein: float
    fat: float
    carbs: float
    calories: float
    date: Date
    
    class Config:
        from_attributes = True

# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #

class DailyReport(BaseModel):
    calories: float
    protein: float
    fat: float
    carbs: float
    log_count: int

class Top3Report(BaseModel):
    name: str
    number_of_logs: int
    weight_sum: float

class AvgWeightReport(BaseModel):
    name: str
    number_of_logs: int
    weight_avg: float

# # # # # # # # # # # # # # # # # # # # # # # # USERS # # # # # # # # # # # # # # # # # # # # # # # #

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    email: str
    active: bool
    created_at: datetime

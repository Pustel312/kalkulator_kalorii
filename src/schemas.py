from pydantic import BaseModel, Field
from datetime import date
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Nazwa produktu")
    protein: float = Field(..., ge=0, description="Białko w 100g (>=0)")
    fat: float = Field(..., ge=0, description="Tłuszcze w 100g (>=0)")
    carbs: float = Field(..., ge=0, description="Węglowodany w 100g (>=0)")


class ProductResponse(ProductCreate):
    id: int
    calories: float

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    protein: float | None = Field(default=None, ge=0)
    fat: float | None = Field(default=None, ge=0)
    carbs: float | None = Field(default=None, ge=0)
    
class LogCreate(BaseModel):
    product_id: int = Field(..., ge=0, description="Id produktu")
    weight: float = Field(..., ge=0, description="Waga produktu")

class LogResponse(BaseModel):
    id: int
    protein: float
    fat: float
    carbs: float
    calories: float
    date: date
    
    class Config:
        from_attributes = True

class DailyReport(BaseModel):
    calories: float
    protein: float
    fat: float
    carbs: float
    log_count: int
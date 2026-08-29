from pydantic import BaseModel, Field

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

class LogCreate(BaseModel):
    product_id: int = Field(..., ge=0, description="Id produktu")
    weight: float = Field(..., ge=0, description="Waga produktu")

class LogResponse(BaseModel):
    id: int
    protein: float
    fat: float
    carbs: float
    calories: float
    date: str
    
    class Config:
        from_attributes = True
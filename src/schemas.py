from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import date as Date, datetime
from src.enums import ProductType, UserProfileWeightGoalRate, UserProfileActivityLevel, UserProfileSex
from decimal import Decimal
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

    model_config = ConfigDict(from_attributes=True)
    
class ProductUpdate(BaseModel):
    name: str | None = Field(default= None, min_length=1, description="Nazwa produktu")
    type: ProductType | None = None
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
    model_config = ConfigDict(from_attributes=True)

# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #

class DailyReport(BaseModel):
    bmr: int
    tdee: int
    target_calories: int
    remaining_calories: int
    exceeded_calories: int
    protein_min: int
    protein_max: int
    protein_eaten: float
    fat_min: int
    fat_max: int
    fat_eaten: float
    carbs_min: int
    carbs_max: int
    carbs_eaten: float
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

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# # # # # # # # # # # # # # # # # # # # # # # # USERPROFILES # # # # # # # # # # # # # # # # # # # # # # # #

class UserProfileCreate(BaseModel):
    sex: UserProfileSex
    height: int = Field(..., ge=100, le=300)
    weight: Decimal = Field(..., ge=30, le=400)
    birth_date: Date
    activity_level: UserProfileActivityLevel = Field(default=UserProfileActivityLevel.moderate)
    goal: UserProfileWeightGoalRate = Field(default=UserProfileWeightGoalRate.maintenance)

class UserProfileResponse(BaseModel):
    user_id: int
    sex: UserProfileSex
    height: int 
    weight: Decimal 
    birth_date: Date
    activity_level: UserProfileActivityLevel 
    goal: UserProfileWeightGoalRate 
    
    model_config = ConfigDict(from_attributes=True)
class UserProfileUpdate(BaseModel):
    height: int | None = Field(default= None, ge=100, le=300, description="height of person")
    weight: Decimal | None = Field(default= None, ge=30, le=400, description="weight of person")
    birth_date: Date | None = Field(default=None)    
    activity_level: UserProfileActivityLevel | None = Field(default= None)
    goal: UserProfileWeightGoalRate | None = Field(default= None)




    
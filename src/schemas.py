from datetime import date as Date
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.enums import (
    PeriodType,
    ProductType,
    UserProfileActivityLevel,
    UserProfileSex,
    UserProfileWeightGoalRate,
)

# # # # # # # # # # # # # # # # # # # # # # # # PRODUCTS # # # # # # # # # # # # # # # # # # # # # # # #


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Product name")
    type: ProductType = Field(..., description="Product type")
    protein: float = Field(..., ge=0, description="Protein(>=0)")
    fat: float = Field(..., ge=0, description="Fat(>=0)")
    carbs: float = Field(..., ge=0, description="Carbs(>=0)")
    weight: float = Field(..., gt=0, description="Product weight")


class ProductResponse(BaseModel):
    name: str = Field(..., min_length=1, description="Product name")
    type: ProductType = Field(..., description="Product type")
    protein: float = Field(..., ge=0, description="Protein in 100g (>=0)")
    fat: float = Field(..., ge=0, description="Fat in 100g (>=0)")
    carbs: float = Field(..., ge=0, description="Carbs in 100g (>=0)")
    id: int
    calories: float = Field(..., ge=0, description="Calories in 100g")

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, description="Product name")
    type: ProductType | None = Field(default=None, description="Product type")    
    protein: float | None = Field(default=None, ge=0)
    fat: float | None = Field(default=None, ge=0)
    carbs: float | None = Field(default=None, ge=0)


# # # # # # # # # # # # # # # # # # # # # # # # COMPONENTS # # # # # # # # # # # # # # # # # # # # # # # #


class ProductComponentCreate(BaseModel):
    product_id: int
    weight: float = Field(..., gt=0, description="Component weight")


class ProductCreateComposed(BaseModel):
    name: str = Field(..., min_length=1, description="Product name")
    type: ProductType = Field(..., description="Product type")
    components: list[ProductComponentCreate] = Field(
        ..., min_length=1, description="Components"
    )


class ProductComponentDetails(BaseModel):
    product_id: int
    name: str = Field(..., min_length=1, description="Product name")
    weight: float = Field(..., gt=0, description="Component weight")


class ProductComponentResult(BaseModel):
    id: int
    name: str = Field(..., min_length=1, description="Product name")
    components: list[ProductComponentDetails] = Field(
        ..., min_length=1, description="Components"
    )


# # # # # # # # # # # # # # # # # # # # # # # # RECIPES # # # # # # # # # # # # # # # # # # # # # # # #


class ProductRecipeCreate(BaseModel):
    product_id: int
    recipe: str = Field(..., min_length=1, description="recipe")
    servings: int = Field(..., gt=0, description="number of servings")
    preparation_time: int | None = Field(
        default=None, ge=0, description="time of preparation"
    )


class ProductRecipeResponse(ProductRecipeCreate):
    model_config = ConfigDict(from_attributes=True)


class ProductRecipeUpdate(BaseModel):
    recipe: str | None = Field(default=None, min_length=1)
    servings: int | None = Field(default=None, gt=0)
    preparation_time: int | None = Field(default=None, ge=0)


# # # # # # # # # # # # # # # # # # # # # # # # LOGS # # # # # # # # # # # # # # # # # # # # # # # #


class LogCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="Product id")
    weight: float = Field(..., gt=0, description="Product weight")


class LogResponse(BaseModel):
    id: int
    product_type: ProductType = Field(..., description="Product type")
    protein: float = Field(..., ge=0, description="Protein")
    fat: float = Field(..., ge=0, description="Fat")
    carbs: float = Field(..., ge=0, description="Carbs")
    calories: float = Field(..., ge=0, description="Calories")
    date: Date

    model_config = ConfigDict(from_attributes=True)


# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #


class PeriodReport(BaseModel):
    period: PeriodType
    date_from: Date
    date_to: Date

    bmr: int = Field(..., ge=0, description="User BMR")  
    tdee: int = Field(..., ge=0, description="User TDEE") 

    target_calories: int = Field(..., ge=0, description="User target calories")
    remaining_calories: int = Field(..., ge=0, description="Remaining calories for user")
    exceeded_calories: int = Field(..., ge=0, description="Exceeded by user calories")

    protein_min: int = Field(..., ge=0, description="Minimum user proteins")
    protein_max: int = Field(..., ge=0, description="Maximum user proteins")
    protein_eaten: float = Field(..., ge=0, description="Proteins eaten by user")
    fat_min: int = Field(..., ge=0, description="Minimum user fat")
    fat_max: int = Field(..., ge=0, description="Maximum user fat")
    fat_eaten: float = Field(..., ge=0, description="Fat eaten by user")
    carbs_min: int = Field(..., ge=0, description="Minimum user carbs")
    carbs_max: int = Field(..., ge=0, description="Maximum user carbs")
    carbs_eaten: float = Field(..., ge=0, description="Carbs eaten by user")

    log_count: int = Field(..., ge=0, description="Number of counted logs")
    days_with_logs: int = Field(..., ge=0, description="Days with logs")
    days_without_logs: int = Field(..., ge=0, description="Days without logs")
    avg_calories_per_logged_day: int = Field(..., ge=0, description="Average calories logged per day")


class Top3Report(BaseModel):
    name: str = Field(..., min_length=1, description="Product name")
    number_of_logs: int = Field(..., ge=0, description="Number of logs")
    weight_sum: float = Field(..., ge=0, description="Sum of total weight")


class AvgWeightReport(BaseModel):
    name: str = Field(..., min_length=1, description="Product name")
    number_of_logs: int = Field(..., ge=0, description="Number of logs")
    weight_avg: float = Field(..., ge=0, description="Average weight of logged product")


# # # # # # # # # # # # # # # # # # # # # # # # USERS # # # # # # # # # # # # # # # # # # # # # # # #


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password")


class UserResponse(BaseModel):
    id: int
    email: EmailStr = Field(..., description="User email address")
    active: bool = Field(..., description="Account activity status")
    created_at: datetime = Field(..., description="Date of creation")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


# # # # # # # # # # # # # # # # # # # # # # # # USERPROFILES # # # # # # # # # # # # # # # # # # # # # # # #


class UserProfileCreate(BaseModel):
    sex: UserProfileSex
    height: int = Field(..., ge=100, le=300)
    weight: Decimal = Field(..., ge=30, le=400)
    birth_date: Date
    activity_level: UserProfileActivityLevel = Field(
        default=UserProfileActivityLevel.moderate
    )
    goal: UserProfileWeightGoalRate = Field(
        default=UserProfileWeightGoalRate.maintenance
    )


class UserProfileResponse(BaseModel):
    user_id: int
    sex: UserProfileSex = Field(..., description="Gender of person")
    height: int = Field(..., ge=100, le=300)
    weight: Decimal = Field(..., ge=30, le=400)
    birth_date: Date
    activity_level: UserProfileActivityLevel
    goal: UserProfileWeightGoalRate

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    height: int | None = Field(
        default=None, ge=100, le=300, description="height of person"
    )
    weight: Decimal | None = Field(
        default=None, ge=30, le=400, description="weight of person"
    )
    birth_date: Date | None = Field(default=None)
    activity_level: UserProfileActivityLevel | None = Field(default=None)
    goal: UserProfileWeightGoalRate | None = Field(default=None)

from enum import StrEnum

from pydantic import BaseModel, Field


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"


class ClothingSize(StrEnum):
    XXXS = "3XS"
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"
    XXXL = "3XL"
    XXXXL = "4XL"
    XXXXXL = "5XL"


class WearingStyle(StrEnum):
    TIGHT = "tight"
    NORMAL = "normal"
    OVERSIZE = "oversize"


class SizeParameters(BaseModel):
    breast: int = 0
    waist: int = 0
    hip: int = 0


class UserPreferences(BaseModel):
    gender: Gender = Gender.FEMALE
    age: int = 18

    clothing_size: ClothingSize | None = None
    size_parameters: SizeParameters | None = None
    wearing_styles: list[WearingStyle] = Field(default_factory=list)
    preferred_styles: list[str] = Field(default_factory=list)

    has_completed_onboarding: bool = False


class SearchMeta(BaseModel):
    categories: list[str]
    colors: list[str]
    brands: list[str]

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Category(BaseModel):
    category_name: str = Field(..., description="Name of the category")
    summary_text: str = Field(..., description="Summary of responses in this category")
    sentiment: str = Field(..., description="Overall sentiment: positive, negative, or neutral")
    response_count: int = Field(0, description="Number of responses in this category")
    percentage: float = Field(..., description="Percentage of responses in this category")

class FormAnalyticsBase(BaseModel):
    formId: int = Field(..., description="ID of the form")
    response_categories: Optional[List[Category]] = Field(None, description="Array of response categories")
    total_responses: int = Field(0, description="Total number of responses")
    status: Optional[str] = Field("active", description="Status of the analytics")

class FormAnalyticsCreate(FormAnalyticsBase):
    pass

class FormAnalyticsUpdate(BaseModel):
    response_categories: Optional[List[Category]] = None
    status: Optional[str] = None

class FormAnalyticsOut(FormAnalyticsBase):
    analyticsId: int
    create_timestamp: datetime
    update_timestamp: datetime

    class Config:
        from_attributes = True

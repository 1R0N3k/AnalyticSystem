from pydantic import BaseModel
from datetime import date

class MarginDataPoint(BaseModel):
    day: date
    revenue: float
    cost: float
    margin: float
    margin_percent: float

class MarginSummary(BaseModel):
    total_revenue: float
    total_cost: float
    total_margin: float
    margin_percent: float

class ABCProduct(BaseModel):
    product_name: str
    revenue: float
    category: str
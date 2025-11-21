from pydantic import BaseModel, ConfigDict

class OrderRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    
    id: int
    item_name: str
    location: str
    cost: float
    delivery_time: int
    status: str

class OrderCreate(BaseModel):
    item_name: str
    location: str
    cost: float
    delivery_time: int
    status: str

class OrderUpdate(BaseModel):
    item_name: str | None = None
    location: str | None = None
    cost: float | None = None
    delivery_time: int | None = None
    status: str | None = None

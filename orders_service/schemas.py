from pydantic import BaseModel

class OrderRead(BaseModel):
    id: int
    item_name: str
    location: str
    cost: float
    delivery_time: int
    status: str

    class Config:
        orm_mode = True     #lets fastapi convert sqlalchemy models to json

class OrderCreate(BaseModel):
    item_name: str
    location: str
    cost: float
    delivery_time: int
    status: str
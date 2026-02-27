from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from .db import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, nullable=False)
    location = Column(String)
    cost = Column(Float)
    delivery_time = Column(Integer) #minutes
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

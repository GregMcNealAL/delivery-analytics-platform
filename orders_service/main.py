from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from orders_service.db import SessionLocal, engine
from orders_service.models import Order, Base
from orders_service.schemas import OrderRead, OrderCreate
from typing import List

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Order Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/orders", response_model=List[OrderRead])
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return orders

@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders", response_model=OrderRead)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(**order.dict())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)  # refresh so new_order has the auto-generated ID
    return new_order

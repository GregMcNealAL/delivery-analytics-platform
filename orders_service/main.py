from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from orders_service.db import get_db
from orders_service.models import Order
from orders_service.schemas import OrderRead, OrderCreate

app = FastAPI(title="Order Service")

@app.get("/orders", response_model=list[OrderRead])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders", response_model=OrderRead)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(**order.dict())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    db.commit()
    return {"message": "Item deleted successfully"}
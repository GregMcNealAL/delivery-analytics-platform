from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from orders_service.db import get_db
from orders_service.models import Order
from orders_service.schemas import OrderRead, OrderCreate, OrderUpdate
from orders_service.dependencies import verify_api_key

app = FastAPI(title="Order Service")


@app.get("/orders", response_model=list[OrderRead], dependencies=[Depends(verify_api_key)])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@app.get("/orders/{order_id}", response_model=OrderRead, dependencies=[Depends(verify_api_key)])
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders", response_model=OrderRead, dependencies=[Depends(verify_api_key)])
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(**order.dict())
    db.add(new_order)
    try:
        db.commit()
        db.refresh(new_order)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database commit failed")
    return new_order

@app.patch("/orders/{order_id}", response_model=OrderRead, dependencies=[Depends(verify_api_key)])
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(order, key, value)

    try:
        db.commit()
        db.refresh(order)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database commit failed")
    return order

@app.delete("/orders/{order_id}", dependencies=[Depends(verify_api_key)])
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database commit failed")
    return {"message": "Item deleted successfully"}

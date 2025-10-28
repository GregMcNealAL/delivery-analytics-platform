from faker import Faker
import random
from orders_service.db import SessionLocal, engine, Base
from orders_service.models import Order

fake = Faker()

def create_fake_orders(n=200):
    session = SessionLocal()
    try:
        for _ in range(n):
            order = Order(
                item_name = fake.word().title() + " " + fake.word().title(),
                location = fake.city(),
                cost = round(random.uniform(5, 200), 2),
                delivery_time = random.randint(10, 120),  # minutes
                status = random.choice(["delivered", "pending", "cancelled"])
            )
            session.add(order)
        session.commit()
    finally:
        session.close()

if __name__ == "__main__":
    # Ensure tables exist (safe to call even if created already)
    Base.metadata.create_all(bind=engine)
    create_fake_orders(300)
    print("✅ Seeded DB with fake orders")
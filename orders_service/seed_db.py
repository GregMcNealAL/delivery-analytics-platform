import random
from faker import Faker
from orders_service.db import SessionLocal, engine, Base
from orders_service.models import Order

fake = Faker("en_US")

STATUSES = ["delivered", "pending", "cancelled"]

def generate_product_name():
    words = [fake.word().title() for _ in range(random.randint(2, 3))]
    return " ".join(words)

def seed_orders(n=300):
    session = SessionLocal()
    try:
        for _ in range(n):
            order = Order(
                item_name=generate_product_name(),
                location=fake.city(),
                cost=round(random.uniform(10, 500), 2),
                delivery_time=random.randint(15, 120),  # minutes
                status=random.choice(STATUSES)
            )
            session.add(order)
        session.commit()
        print(f"DB seeded successfully")
    finally:
        session.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_orders()

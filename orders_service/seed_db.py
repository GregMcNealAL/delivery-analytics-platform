import random
from orders_service.db import SessionLocal, engine, Base
from orders_service.models import Order

STATUSES = ["delivered", "pending", "cancelled"]
STATUS_WEIGHTS = [0.65, 0.25, 0.10]

PRODUCT_CATALOG = {
    "Electronics": [
        "Wireless Mouse",
        "Mechanical Keyboard",
        "USB-C Charger",
        "Bluetooth Headphones",
        "Portable SSD",
        "Smartphone Case",
    ],
    "Home": [
        "Paper Towels",
        "Dish Soap",
        "Laundry Detergent",
        "Trash Bags",
        "Air Filter",
        "Storage Bins",
    ],
    "Grocery": [
        "Organic Bananas",
        "Whole Milk",
        "Brown Eggs",
        "Sourdough Bread",
        "Greek Yogurt",
        "Ground Coffee",
    ],
    "Office": [
        "Notebook Pack",
        "Ballpoint Pens",
        "Printer Paper",
        "Desk Lamp",
        "Stapler Set",
        "Dry Erase Markers",
    ],
}

ALABAMA_LOCATIONS = [
    "Birmingham",
    "Hoover",
    "Homewood",
    "Vestavia Hills",
    "Mountain Brook",
    "Trussville",
    "Pelham",
    "Alabaster",
    "Tuscaloosa",
    "Huntsville",
    "Montgomery",
    "Mobile",
]

# Heavier traffic in the Birmingham metro to resemble local delivery demand.
ALABAMA_LOCATION_WEIGHTS = [
    0.24,  # Birmingham
    0.14,  # Hoover
    0.08,  # Homewood
    0.08,  # Vestavia Hills
    0.06,  # Mountain Brook
    0.06,  # Trussville
    0.06,  # Pelham
    0.06,  # Alabaster
    0.08,  # Tuscaloosa
    0.06,  # Huntsville
    0.05,  # Montgomery
    0.03,  # Mobile
]


def generate_product_name() -> str:
    category = random.choice(list(PRODUCT_CATALOG.keys()))
    product = random.choice(PRODUCT_CATALOG[category])
    return f"{category} - {product}"

def generate_location() -> str:
    return random.choices(ALABAMA_LOCATIONS, weights=ALABAMA_LOCATION_WEIGHTS, k=1)[0]


def seed_orders(n=500):
    session = SessionLocal()
    try:
        for _ in range(n):
            order = Order(
                item_name=generate_product_name(),
                location=generate_location(),
                cost=round(random.uniform(10, 500), 2),
                delivery_time=random.randint(15, 120),  # minutes
                status=random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0],
            )
            session.add(order)
        session.commit()
        print(f"DB seeded successfully: {n} rows")
    finally:
        session.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_orders()

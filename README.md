# Delivery Analytics Platform
 
 Project I made to learn **FastAPI**, **SQlAlchemy**, and how services talk to each other.

 ---

 ## What It Does

 - **Orders Service (port 8000)**
    - Stores delivery data data in SQLite (seeded with Faker)
    - Includes endpoints to view all orders, get order by ID, and add new orders

- **Analytics Service (port 8001)**
    - Pulls data from Orders API
    - Calculates total orders, average delivery time, average cost, and top 3 locations

## Setup
 
 # 1. Clone the repo:
 
 ```bash
git clone https://github.com/GregMcNealAL/delivery-analytics-platform.git
cd delivery-analytics-platform
```
# 2. Create and activate virtual environnment:
```bash
python -m venv venv
```

### Windows Powershell
```bash
venv\Scripts\Activate.ps1
```
### macOS/Linux
```bash
source venv/bin/activate
```

# 3. Install dependencies:
```bash
pip install -r requirements.txt
```

# 4. Seed the database:
```bash
python -m orders_service.seed_db
```

# 5. Run services:
### Orders service
```bash
uvicorn orders_service.main:app --reload --port 8000
```
### In another terminal: Analytics service
```bash
uvicorn analytics_service.main:app --reload --port 8001
```
## Notes
    - FastAPI provides interactive API docs at `/docs` (e.g., `http://127.0.0.1:8000/docs`) -- great for testing endpoints and learning how the API works.
    - Database in SQLite for simplicity but it could be easily switched to PostgreSQL.
# Backend Assignment API Documentation

## API Overview

This API is designed to calculate the total CO2 emissions for different business facilities over a specified date range. The main endpoint handles POST requests and calculates emissions based on transaction data stored in a PostgreSQL database.

---

## API Endpoint

### POST /api/

#### Description
This endpoint calculates total CO2 emissions for selected business facilities between a specified date range.

#### Request Format

**Endpoint**: `/api/`

**Method**: `POST`

**Request Body**:

```json
{
    "startDate": "2020-11-03",  
    "endDate": "2024-12-02",    
    "businessFacilities": [
        "GreenEat Tangs", "GreenEat Fusionopolis","Fresh Kitchen Capital Tower","Fresh Kitchen Havelock" 
    ]
}
```
**Response Body**:
```json
{
    "GreenEat Fusionopolis": 1375514.2300000028,
    "Fresh Kitchen Capital Tower": 286035.1799999986,
    "Fresh Kitchen Havelock": 20901.49000000001,
    "GreenEat Tangs": 4673766.800000042
}
```
## Prerequisites

- Python 3.13+
- PostgreSQL (Database)
- Virtualenv (for isolated Python environment)

## Steps to Set Up Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Abhinav4382/backend-assignment.git
   cd backend-assignment
   ```
2.**Create a Virtual Environment**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
 ```
3.**Install Dependencies**:
```bash
  pip install -r requirements.txt
```
4.**Set Up PostgreSQL Database**:
  Create a PostgreSQL database (e.g., backend_assigndb).
 ```python
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'backend_assigndb',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
5.**Apply Migrations**:
  ```python
  python manage.py migrate
  ```
6.**Start the Django Server**:
```python
python manage.py runserver
```

# Expense Tracker API

This project is a Django-based API for managing users and tracking their expenses. It includes features for splitting expenses among participants using different methods (equal, exact, and percentage splits).

## Features

- Create and retrieve users
- Add expenses and split them among participants
- Retrieve individual user expenses
- Retrieve all expenses
- Download balance sheet as CSV

## Installation

### Prerequisites

- Python 3.x
- pip (Python package installer)
- virtualenv

### Setup

1. **Clone the repository**:
    ```sh
    git clone https://github.com/TUSHAR-VERMA-star/dailyExpenses.git
    cd expense-tracker
    ```

2. **Create a virtual environment**:
    ```sh
    python -m venv venv
    ```

3. **Activate the virtual environment**:
    - On Windows:
      ```sh
      .\venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```sh
      source venv/bin/activate
      ```

4. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

5. **Apply migrations**:
    ```sh
    python manage.py migrate
    ```

6. **Run the development server**:
    ```sh
    python manage.py runserver
    ```

## Functionality

### Error Handling and Input Validation

- Input validation is handled by serializers.
- Specific error messages and exception handling are implemented.

### Performance Optimization

- `select_related` and `prefetch_related` are used to optimize database queries and enhance performance for large datasets.

### Unit and Integration Tests

- Basic unit and integration tests are included in `tests.py`.

## API Endpoints

### Users

1. **Create User**
    - **URL**: `/api/users/`
    - **Method**: `POST`
    - **Body**:
      ```json
      {
            "email": "user1@example.com",
            "name": "User One",
            "mobile_number": "1234567890"
      }

      ```

2. **Retrieve User Details**
    - **URL**: `/api/users/{user_id}/`
    - **Method**: `GET`

3. **Retrieve All Users**
    - **URL**: `/api/users/`
    - **Method**: `GET`

### Expenses

1. **Add Expense**
    - **URL**: `/api/add-expense/`
    - **Method**: `POST`
    - **Body**:
      ```json
      {
        "user": 1,
        "description": "Dinner",
        "amount": 90.00,
        "split_method": "equal",
        "participants": [
          {"user_id": 1},
          {"user_id": 2},
          {"user_id": 3}
        ]
      }
      ```

2. **Retrieve User Expenses**
    - **URL**: `/api/users/{user_id}/expenses/`
    - **Method**: `GET`

3. **Retrieve Overall Expenses**
    - **URL**: `/api/expenses/`
    - **Method**: `GET`

4. **Download Balance Sheet**
    - **URL**: `/api/download-balance-sheet/`
    - **Method**: `GET`

## Code Overview

### Error Handling and Input Validation

Input validation is managed using Django Rest Framework's serializers. Specific error messages and validation rules are defined within the serializers. Additionally, exception handling is implemented in the views to provide meaningful error responses.

### Performance Optimization

Database queries are optimized using `select_related` to reduce the number of queries made to the database, especially for related data. This improves performance when handling large datasets.

### Unit and Integration Tests

Unit and integration tests are included in `tests.py` to ensure the functionality of the API endpoints. These tests cover creating users, adding expenses with different split methods, and retrieving user and overall expenses.

### Example Test Cases

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Expense

class ExpenseTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create(name="User 1")
        self.user2 = User.objects.create(name="User 2")
        self.user3 = User.objects.create(name="User 3")

    def test_create_user(self):
        response = self.client.post('/api/users/', {'name': 'New User'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_user(self):
        response = self.client.get(f'/api/users/{self.user1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_expense_equal_split(self):
        data = {
            "user": self.user1.id,
            "description": "Dinner",
            "amount": 90.00,
            "split_method": "equal",
            "participants": [
                {"user_id": self.user1.id},
                {"user_id": self.user2.id},
                {"user_id": self.user3.id}
            ]
        }
        response = self.client.post('/api/add-expense/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_expense_exact_split(self):
        data = {
            "user": self.user1.id,
            "description": "Movie",
            "amount": 60.00,
            "split_method": "exact",
            "participants": [
                {"user_id": self.user1.id, "amount": 20.00},
                {"user_id": self.user2.id, "amount": 20.00},
                {"user_id": self.user3.id, "amount": 20.00}
            ]
        }
        response = self.client.post('/api/add-expense/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_expense_percentage_split(self):
        data = {
            "user": self.user1.id,
            "description": "Gift",
            "amount": 100.00,
            "split_method": "percentage",
            "participants": [
                {"user_id": self.user1.id, "percentage": 50},
                {"user_id": self.user2.id, "percentage": 30},
                {"user_id": self.user3.id, "percentage": 20}
            ]
        }
        response = self.client.post('/api/add-expense/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_user_expenses(self):
        Expense.objects.create(user=self.user1, description="Dinner", amount=30, split_method="equal")
        response = self.client.get(f'/api/users/{self.user1.id}/expenses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_overall_expenses(self):
        Expense.objects.create(user=self.user1, description="Dinner", amount=30, split_method="equal")
        response = self.client.get('/api/expenses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_balance_sheet(self):
        Expense.objects.create(user=self.user1, description="Dinner", amount=30, split_method="equal")
        response = self.client.get('/api/download-balance-sheet/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="balance_sheet.csv"', response['Content-Disposition'])

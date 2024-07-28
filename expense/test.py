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

import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import db, create_app
from app.models.user import User
from app.models.expense import Expense


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.app = create_app({"TESTING": True})
        # self.app.testing = True

    def test_register(self):
        response = self.app.post('/user/register', json={
            'username': 'test_user',
            'password': 'test_password',
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'User registered!')

    def test_login(self):
        response = self.app.post('/user/login', json={
            'username': 'test_user',
            'password': 'test_password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_login_invalid_credentials(self):
        response = self.app.post('/user/login', json={
            'username': 'test_user',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid credentials')


class TestExpense(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True


    def test_add_expense(self):
        response = self.app.post('/expenses', json={
            'amount': 100,
            'description': 'Test expense',
            'date': '2022-01-01',
            'category': 'Test category'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Expense added successfully')

    def test_get_expenses(self):
        response = self.app.get('/expenses')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_delete_expense(self):
        expense = Expense(amount=100, description='Test expense', date='2022-01-01', category='Test category')
        db.session.add(expense)
        db.session.commit()

        response = self.app.delete(f'/expenses/{expense.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Expense deleted!')

    def test_update_expense(self):
        expense = Expense(amount=100, description='Test expense', date='2022-01-01', category='Test category')
        db.session.add(expense)
        db.session.commit()

        response = self.app.put(f'/expenses/{expense.id}', json={
            'amount': 200,
            'description': 'Updated expense',
            'date': '2022-02-01',
            'category': 'Updated category'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Expense updated!')


if __name__ == '__main__':
    unittest.main()
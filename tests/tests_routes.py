import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token
from app import db, create_app
from app.models.user import User
from app.models.expense import Expense
from flask import json


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        # self.app.testing = True

        # Create a test user
        self.test_user = User(username='testuser', email='testuser@example.com')
        self.test_user.set_password('testpassword')
        db.session.add(self.test_user)
        db.session.commit()
        
        self.access_token = create_access_token(identity={'id': self.test_user.id})


    def test_register(self):
        response = self.client.post('/user/register', json={
            'username': '3uniqueuser',
            'email': 'uniqueuser@example.com',
            'password': 'uniquepassword'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'User registered!')

    def test_login(self):
        response = self.client.post('/user/login', json={
            'username': 'test_user',
            'password': 'test_password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_login_invalid_credentials(self):
        response = self.client.post('/user/login', json={
            'username': 'test_user',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid credentials')


class TestExpense(unittest.TestCase):

    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()
        # self.app = app.test_client()
        # self.app.testing = True

        # Create a test user
        self.test_user = User(username='testuser', email='testuser@example.com')
        self.test_user.set_password('testpassword')
        db.session.add(self.test_user)
        db.session.commit()
        self.access_token = create_access_token(identity={'id': self.test_user.id})

    def test_add_expense(self):
        response = self.client.post('/expenses', json={
            'amount': 100,
            'description': 'Test expense',
            'date': '2022-01-01',
            'category': 'Test category'
        }, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Expense added successfully')

    def test_get_expenses(self):
        # Add an expense first
        expense = Expense(amount=50.0, description='Test expense', date='2023-07-24', user_id=self.test_user.id, category='Food')
        db.session.add(expense)
        db.session.commit()
        response = self.client.get('/expenses',headers={'Authorization': f'Bearer {self.access_token}'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertTrue(len(data) > 0)

    def test_delete_expense(self):
        expense = Expense(amount=100, description='Test expense', date='2022-01-01', user_id=self.test_user.id, category='Test category')
        db.session.add(expense)
        db.session.commit()

        response = self.client.delete(f'/expenses/{expense.id}', headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Expense deleted!')

    def test_update_expense(self):
        expense = Expense(amount=100, description='Test expense', date='2022-01-01',user_id=self.test_user.id, category='Test category')
        db.session.add(expense)
        db.session.commit()

        response = self.client.put(f'/expenses/{expense.id}', json={
            'amount': 200,
            'description': 'Updated expense',
            'date': '2022-02-01',
            'category': 'Updated category'
        }, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Expense updated!')


if __name__ == '__main__':
    unittest.main()
import pytest
from app import create_app, db
from app.models.packing_list import PackingList
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='module')
def test_client():
    app = create_app({'TESTING': True})  # Create a Flask application instance with the testing configuration
    with app.test_client() as testing_client:  # Create a test client for making HTTP requests
        with app.app_context():  # Push an application context
            db.create_all()  # Create all database tables within this context
        yield testing_client  # Provide the test client to the test functions
        with app.app_context():  # Push an application context again for cleanup
            db.drop_all()  # Drop all database tables to clean up


@pytest.fixture
def auth_user_headers(test_client):
    # Register test user:
    test_client.post('/user/register', json={
        'username': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com'
    })

    # Login test user:
    response = test_client.post('/user/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })

    access_token = response.json.get('access_token')
    return {'Authorization': f'Bearer {access_token}'}


def test_add_item(test_client, auth_user_headers):
    response = test_client.post('/packing-list', json={
        'item_name': 'Toothbrush'
    }, headers=auth_user_headers)
    assert response.status_code == 201
    assert response.json.get('message') == 'Item added to packing list'


def test_get_list_items(test_client, auth_user_headers):
    # First add an item
    test_client.post('/packing-list', json={'item_name': 'Pants'}, headers=auth_user_headers)
    response = test_client.get('/packing-list', headers=auth_user_headers)
    assert response.status_code == 200
    assert len(response.json) > 0


# def test_get_empty_list(test_client, auth_user_headers):
#     response = test_client.get('/packing-list', headers=auth_user_headers)
#     assert response.status_code == 200
#     assert len(response.json) == 0


def test_update_item(test_client, auth_user_headers):
    # Add  item
    test_client.post('/packing_list', json={'item_name':'Soap'}, headers=auth_user_headers)
    # Get item ID
    response = test_client.get('/packing-list', headers=auth_user_headers)
    item_id = response.json[0]['id']
    response = test_client.put(f'/packing-list/{item_id}', json={
        'item_name': 'Bobby Wash',
        'is_packed': True
    }, headers=auth_user_headers)
    assert response.status_code == 200
    assert response.json.get('message') == 'Item updated'


# def test_update_item_invalid_id(test_client, auth_user_headers):
#     response = test_client.put('/packing-list/123', json={
#         'item_name': 'Shoes',
#         'is_packed': True
#     }, headers=auth_user_headers)
#     assert response.status_code == 404
#     assert response.json.get('message') == 'Item not found'


def test_delete_item(test_client, auth_user_headers):
    # Add item
    test_client.post('/packing-list', json={'item_name':'Shoes'}, headers=auth_user_headers)
    # Get item ID
    response = test_client.get('packing-list', headers=auth_user_headers)
    item_id = response.json[0]['id']
    response = test_client.delete(f'/packing-list/{item_id}', headers=auth_user_headers)
    assert response.status_code == 200
    assert response.json.get('message') == 'Item deleted'


# def test_delete_item_invalid_id(test_client, auth_user_headers):
#     response = test_client.delete('/packing-list/123', headers=auth_user_headers)
#     assert response.status_code == 404
#     assert response.json.get('message') == 'Item not found'



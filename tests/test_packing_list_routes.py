import pytest
from app import create_app, db
from flask_jwt_extended import create_access_token
from app.models.packing_list import PackingList
from app.models.item import Item
from app.models.user import User

@pytest.fixture(scope='module')
def test_client():
    # Create the flask app instance
    app = create_app('testing')

    # Create the application context and the test client:
    with app.app_context():
        db.create_all()
        print("DB created")
        yield app.test_client()
        db.drop_all()
        print("DB dropped")


@pytest.fixture
def auth_token(test_client):
    # Create a test user and get an auth token
    with test_client.application.app_context():
        user = User(username='testuser', email='test@test.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        # Make sure user instance is still bound to the session
        db.session.refresh(user) # Refres user to ensure it's up-to-date
    
    # Create and return access token for user
    access_token = create_access_token(identity={'id': user.id})
    return access_token


@pytest.fixture
def packing_list(test_client, auth_token):
    # Create a packing list to be used in tests:
    response = test_client.post(
        '/packing-list',
        json={'listName': 'Test List for Deletion', 'items': [{'description': 'Item to be deleted'}]},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    return response.json['packingList']['id']


def test_create_list(test_client, auth_token):
    # Test creating a new packcing list
    response = test_client.post(
        '/packing-list',
        json={'listName': 'New Test List', 'items': [{'description': 'New Item', 'quantity': 5}]},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201
    assert response.json['message'] == 'New packing list created'
    assert 'packingList' in response.json
    assert response.json['packingList']['listName'] == 'New Test List'
    assert len(response.json['packingList']['items']) == 1
    assert response.json['packingList']['items'][0]['description'] == 'New Item'


def test_get_lists(test_client, auth_token):
    # Test getting all packing lists
    test_client.post(
        '/packing-list',
        json={'listName': 'Vacation', 'items': [{'description': 'Shirt', 'quantity': 3}]},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    response = test_client.get(
        '/packing-list',
        headers={'Authorization': f'Bearer {auth_token}'})
    
    # Print response for debugging
    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json)
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0

    # Verify that the response contains the packing list created by the fixture
    packing_list_ids = [plist['id'] for plist in response.json]
    print("Packing List IDs in response:", packing_list_ids)
    
    
def test_delete_list(test_client, auth_token, packing_list):
    # Print packing list ID before deletion
    print("Packing List ID to be deleted:", packing_list)

    response_before_delete = test_client.get(
        f'/packing-list/{packing_list}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response_before_delete.status_code == 200
    assert response_before_delete.json['id'] == packing_list

    # Print the packing list ID before deletion
    print("Packing List ID to be deleted:", packing_list)

    # Test deleting a packing list
    response = test_client.delete(f'/packing-list/{packing_list}',
                headers={'Authorization': f'Bearer {auth_token}'})
    
    # print the response for debbuging
    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json)

    assert response.status_code == 200
    assert response.json['message'] == 'Packing list deleted!'

    response_after_delete = test_client.get(
        f'/packing-list/{packing_list}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )

    assert response_after_delete.status_code == 404


def test_update_list(test_client, auth_token):
    # create initial packing list:
    response = test_client.post(
        '/packing-list',
        json={'listName': 'Update Test List', 'items': [{'description': 'Initial Item', 'quantity': 1}]},
        headers={'Authorization': f'Bearer {auth_token}'}
    )

    list_id = response.json['packingList']['id']

    # Update list with new items
    response = test_client.put(
        f'/packing-list/{list_id}',
        json={'listName': 'Updated List Name', 'items': [{'id': None, 'description': 'New Item', 'quantity': 1}]},
        headers={'Authorization': f'Bearer {auth_token}'}
    )

    assert response.status_code == 200
    assert response.json['message'] == 'Packing list updated'
    assert response.json['packing_list']['listName'] == 'Updated List Name'

    updated_items = response.json['packing_list']['items']
    assert len(updated_items) == 2
    assert any(item['description'] == 'New Item' for item in updated_items)

    initial_item_exists = any(item['description'] == 'Initial Item' for item in updated_items)
    assert initial_item_exists

def test_get_list_by_id(test_client, auth_token):
    response = test_client.post(
        '/packing-list',
        json={'listName': 'Test List by ID', 'items': [{'description': 'Item to get list by ID'}]},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    list_id = response.json['packingList']['id']

    response = test_client.get(
        f'/packing-list/{list_id}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )

    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json)

    assert response.status_code == 200
    assert response.json['id'] == list_id
    assert response.json['listName'] == 'Test List by ID'
    assert len(response.json['items']) == 1
    assert response.json['items'][0]['description'] == 'Item to get list by ID'

    response = test_client.get(
        '/packing-list/12345',
        headers={'Authorization': f'Bearer {auth_token}'}
    )

    print("Response Status Code (non-existent):", response.status_code)
    print("Response JSON (non-existent):", response.json)

    assert response.status_code == 404
    assert response.json['message'] == 'Packing list not found'

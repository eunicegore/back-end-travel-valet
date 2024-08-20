import pytest
from app import create_app, db
from app.models.packing_list import PackingList
from app.models.item import Item
from app.models.user import User
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

@pytest.fixture
def auth_token(test_client):
    # Create test user and get an auth token
    with test_client.application.app_context():
        user = User(username='testuser', email='test@test.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity={'id': user.id})
    return access_token

@pytest.fixture
def packing_list(test_client, auth_token):
    response = test_client.post(
        '/packing-list',
        json={'listName':'Test List for Items', 'items': [{'description': 'Item for testing'}]},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201
    return response.json['packingList']['id']


def test_add_item_to_list(test_client, auth_token, packing_list):
    response = test_client.post(
        f'/packing-list/{packing_list}/items',
        json={'description': 'New Item', 'quantity': 3},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201
    assert response.json['message'] == 'Item added to list'
    assert 'item' in response.json
    assert response.json['item']['description'] == 'New Item'
    assert response.json['item']['quantity'] == 3


def test_delete_item(test_client, auth_token, packing_list):
    # Add  item
    response = test_client.post(
        f'/packing-list/{packing_list}/items',
        json={'description': 'Test Item', 'quantity': 1, 'packed': False},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201
    item_id = response.json['item']['id']
    print(f"Added item ID: {item_id}")

    # Delete the item
    response = test_client.delete(
        f'/packing-list/{packing_list}/items/{item_id}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )

    print(f"Deleted item ID: {item_id}")
    assert response.status_code == 200
    assert response.json['message'] == 'Item deleted'

    response = test_client.get(
        f'/packing-list/{packing_list}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    packing_list_data = response.json
    item_ids = [item['id'] for item in packing_list_data['items']]
    assert item_id not in item_ids


def test_toggle_packed_status(test_client, auth_token, packing_list):
    # Add item
    response = test_client.post(
        f'/packing-list/{packing_list}/items',
        json={'description': 'Item to toggle', 'quantity': 1},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201
    item_id = response.json['item']['id']
    
    # Toggle the status
    response = test_client.patch(
        f'/packing-list/{packing_list}/items/{item_id}/toggle',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert response.json['message'] == 'Item status toggled'
    assert response.json['item']['packed'] is True  # Assuming it toggles to True

    # Toggle again
    response = test_client.patch(
        f'/packing-list/{packing_list}/items/{item_id}/toggle',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert response.json['message'] == 'Item status toggled'
    assert response.json['item']['packed'] is False  # Should toggle back to False

def test_update_item(test_client, auth_token, packing_list):
    # Add an item to the list
    response = test_client.post(
        f'/packing-list/{packing_list}/items',
        json={'description': 'Item to update', 'quantity': 1},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201
    item_id = response.json['item']['id']
    
    # Update the item
    response = test_client.put(
        f'/packing-list/{packing_list}/items/{item_id}',
        json={'description': 'Updated Item', 'quantity': 5},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert response.json['message'] == 'Item updated'
    assert response.json['item']['description'] == 'Updated Item'
    assert response.json['item']['quantity'] == 5


def test_delete_all_items(test_client, auth_token, packing_list):
    # Add items
    items_to_add = [
        {'description': 'Item 1', 'quantity': 1, 'packed': False},
        {'description': 'Item 2', 'quantity': 2, 'packed': True},
        {'description': 'Item 3', 'quantity': 3, 'packed': False}
    ]
    for item in items_to_add:
        response = test_client.post(
            f'/packing-list/{packing_list}/items',
            json=item,
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 201

    # Delete all items
    response = test_client.delete(
        f'/packing-list/{packing_list}/items',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    assert response.json['message'] == 'All items deleted from list'
    
    # Get updated list
    response = test_client.get(
        f'/packing-list/{packing_list}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    packing_list_data = response.json
    item_ids = [item['id'] for item in packing_list_data['items']]
    assert len(item_ids) == 0



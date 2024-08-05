import pytest
from app import create_app, db


@pytest.fixture(scope="module")
def test_client():
    app = create_app({"TESTING": True})
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
        yield testing_client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def auth_user_headers(test_client):
    test_client.post(
        "/user/register",
        json={
            "username": "test_user",
            "password": "test_password",
            "email": "test@test.com",
        },
    )

    response = test_client.post(
        "/user/login", json={"username": "test_user", "password": "test_password"}
    )

    access_token = response.json.get("access_token")
    return {"Authorization": f"Bearer {access_token}"}

# Create a packing list to use in the items tests:
@pytest.fixture
def mock_packing_list(test_client, auth_user_headers):
    response = test_client.post('/packing-list', json={'list_name': 'Test Packing List'}, headers=auth_user_headers)
    return response.json['packing_list']

def test_add_item(test_client, auth_user_headers, mock_packing_list):
    response = test_client.post(
        f"/packing-list/{mock_packing_list['list_id']}/items",
        json={
            "item_name": "Add New Item",
            "quantity": 1,
            "packed_quantity": 0,
            "is_packed": False,
        },
        headers=auth_user_headers,
    )
    assert response.status_code == 201
    data = response.json
    assert data['message'] == 'Item added to list'
    assert 'item' in data


def test_delete_item(test_client, auth_user_headers, mock_packing_list):
    # Add a new item:
    response = test_client.post(
        f'/packing-list/{mock_packing_list['list_id']}/items',
        json={
            'item_name': 'Item to Delete',
            'quantity': 1
            },
            headers=auth_user_headers
    ) 
    item_id = response.json['item']['item_id']

    # Delete the item:
    response = test_client.delete(
        f'/packing-list/items/{item_id}',
        headers=auth_user_headers
    )
    assert response.status_code == 200
    assert response.json['message'] == 'Item deleted'


def test_toggle_item_status(test_client, auth_user_headers, mock_packing_list):
    response = test_client.post(
        f'/packing-list/{mock_packing_list['list_id']}/items',
        json={
            'item_name': 'Item Toggle status',
            'quantity': 1,
            'is_packed': False
        },
        headers=auth_user_headers
    )
    item_id = response.json['item']['item_id']

    # Toggle is_packed status:
    response = test_client.patch(
        f'/packing-list/items/{item_id}/toggle',
        headers=auth_user_headers
    )
    assert response.status_code == 200
    assert response.json['message'] == 'Item status toggled'
    assert response.json['item']['is_packed'] is True

def test_toggle_item_not_found(test_client, auth_user_headers):
    response = test_client.patch(
        '/packing-list/items/999/toggle',
        headers=auth_user_headers
    )
    print(response.data)
    assert response.status_code == 404
    data = response.json
    assert data['message'] == 'Item not found'
    assert data is not None, "Response data is None"
    assert data['message'] == 'Item not found'


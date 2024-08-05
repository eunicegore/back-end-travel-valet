import pytest
from app import create_app, db


@pytest.fixture(scope="module")
def test_client():
    app = create_app(
        {"TESTING": True}
    )  # Create a Flask application instance with the testing configuration
    with app.test_client() as testing_client:  # Create a test client for making HTTP requests
        with app.app_context():  # Push an application context
            db.create_all()  # Create all database tables within this context
        yield testing_client  # Provide the test client to the test functions
        with app.app_context():  # Push an application context again for cleanup
            db.drop_all()  # Drop all database tables to clean up


@pytest.fixture
def auth_user_headers(test_client):
    # Register test user:
    test_client.post(
        "/user/register",
        json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com",
        },
    )

    # Store response of login in a user:
    response = test_client.post(
        "/user/login", json={"username": "testuser", "password": "testpassword"}
    )

    # extract access token from post response 
    access_token = response.json.get("access_token")
    return {"Authorization": f"Bearer {access_token}"}


def test_create_list(test_client, auth_user_headers):
    response = test_client.post(
        "/packing-list",
        json={
            "list_name": "Test List",
            "items": [
                {"item_name": "Shirt", "quantity": 5},
                {"item_name": "Pants", "quantity": 2},
            ],
        },
        headers=auth_user_headers,
    )
    assert response.status_code == 201
    data = response.json
    assert data["message"] == "New packing list created"
    assert "packing_list" in data


def test_get_all_lists(test_client, auth_user_headers):
    # Create test data: new packing list with items:
    create_response = test_client.post(
        "/packing-list",
        json={
            "list_name": "Test List",
            "items": [
                {
                    "item_name": "Pants",
                    "quantity": 3,
                    "packed_quantity": 1,
                    "is_packed": False,
                },
                {
                    "item_name": "Shirts",
                    "quantity": 5,
                    "packed_quantity": 3,
                    "is_packed": False,
                },
            ],
        },
        headers=auth_user_headers,
    )

    # Check that packing list was created successfully:
    assert create_response.status_code == 201
    created_list = create_response.json["packing_list"]
    assert "list_id" in created_list
    assert created_list["list_name"] == "Test List"
    assert len(created_list["items"]) > 0

    # Get all packing lists:
    get_response = test_client.get("/packing-list", headers=auth_user_headers)

    # Check that the response is successful:
    assert get_response.status_code == 200
    data = get_response.json

    # Check that response data is a list and not empty
    assert isinstance(data, list)
    assert len(data) > 0

    # Check that the created test list is in the response - list of lists:
    lists_ids = [lst["list_id"] for lst in data]
    assert created_list["list_id"] in lists_ids


def test_update_list(test_client, auth_user_headers):
    # Create a packing list:
    create_response = test_client.post(
        "/packing-list",
        json={
            "list_name": "Test List",
            "items": [
                {"item_name": "Hat", "quantity": 2},
                {"item_name": "Shirt", "quantity": 5},
            ],
        },
        headers=auth_user_headers,
    )

    assert create_response.status_code == 201

    created_list = create_response.json["packing_list"]
    list_id = created_list["list_id"]

    print(f"Created packing list ID: {list_id}")

    # Get item IDs for later updates:
    item_ids = [item["item_id"] for item in created_list["items"]]

    # Update the items in the packing list:
    update_response = test_client.put(
        f"/packing-list/{list_id}",
        json={
            "list_name": "Updated Test List",
            "items": [
                {
                    "item_id": item_ids[0],  # Update the first item
                    "item_name": "Updated Item",
                    "quantity": 80,
                    "packed_quantity": 5,
                    "is_packed": True,
                },
                {"item_name": "Second update - add new item", "quantity": 100},
            ],
        },
        headers=auth_user_headers,
    )

    # Debug - print to see the update response details:
    print(f"Update Response JSON: {update_response.json}")
    print(f"Update Response Status Code: {update_response.status_code}")

    # Check that the update was successful
    assert update_response.status_code == 200
    updated_list = update_response.json["packing_list"]
    assert updated_list["list_name"] == "Updated Test List"

    # Check updated item:
    updated_items = {item["item_id"]: item for item in updated_list["items"]}
    assert updated_items[item_ids[0]]["item_name"] == "Updated Item"
    assert updated_items[item_ids[0]]["quantity"] == 80
    assert updated_items[item_ids[0]]["packed_quantity"] == 5
    assert updated_items[item_ids[0]]["is_packed"] is True

    # Check new item:
    new_item = next(
        (item for item in updated_list["items"] if item["item_name"] == "Second update - add new item"),
        None
    )
    assert new_item is not None
    assert new_item["quantity"] == 100


def test_delete_list(test_client, auth_user_headers):
    # Create a packing list with one item:
    create_response = test_client.post(
        "/packing-list",
        json={
            "list_name": "List to Delete",
            "items": [{"item_name": "Delete Item", "quantity": 1}],
        },
        headers=auth_user_headers,
    )

    print(f"created list: {create_response.json}")

    # Get id of list:
    list_id = create_response.json["packing_list"]["list_id"]
    print(f"id of new list: {list_id}")

    # Delete the packing list:
    delete_response = test_client.delete(
        f"/packing-list/{list_id}", headers=auth_user_headers
    )
    assert delete_response.status_code == 200
    data = delete_response.json
    print(f"data after deleting the list: {data}")
    assert data["message"] == "Packing list deleted"

    # Verify that the packing list is deleted:
    verify_response = test_client.get(
        f"/packing-list/{list_id}", headers=auth_user_headers
    )
    assert verify_response.status_code == 404
    assert verify_response.json.get("message") == "Packing list not found"


def test_get_list_by_id(test_client, auth_user_headers):
    # Create a packing list:
    create_response = test_client.post(
        "/packing-list",
        json={
            "list_name": "List by ID",
            "items": [{"item_name": "Shoes", "quantity": 1}]
        },
        headers=auth_user_headers,
    )

    list_id = create_response.json["packing_list"]["list_id"]

    # Get the packing list with the above id:
    get_response = test_client.get(
        f"/packing-list/{list_id}", headers=auth_user_headers
    )
    assert get_response.status_code == 200
    data = get_response.json
    assert data["list_name"] == "List by ID"
    assert "items" in data

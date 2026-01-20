import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/"

def test_user_registration():
    url = f"{BASE_URL}register"
    headers = {"Content-Type": "application/json"}
    data = {
        "username": "newtestuser",
        "password": "testpassword123"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["username"] == "newtestuser"

if __name__ == "__main__":
    test_user_registration()

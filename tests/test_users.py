import pytest
from fastapi import status


def test_create_user(client):
    """Тест создания пользователя"""
    response = client.post("/users/", json={"name": "John Doe"})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "John Doe"
    assert "id" in data


def test_create_user_empty_name(client):
    """Тест создания пользователя с пустым именем"""
    response = client.post("/users/", json={"name": ""})
    
    assert response.status_code == status.HTTP_200_OK  # Pydantic валидация пропустит пустую строку
    data = response.json()
    assert data["name"] == ""


def test_get_users_empty(client):
    """Тест получения списка пользователей, когда нет ни одного"""
    response = client.get("/users/")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_users(client, create_test_user):
    """Тест получения списка пользователей"""
    # Создаем тестовых пользователей
    user1 = create_test_user("Alice")
    user2 = create_test_user("Bob")
    
    response = client.get("/users/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    # Проверяем, что созданные пользователи есть в ответе
    names = [user["name"] for user in data]
    assert "Alice" in names
    assert "Bob" in names


def test_get_users_with_filter(client, create_test_user):
    """Тест фильтрации пользователей по имени"""
    create_test_user("Alice Wonderland")
    create_test_user("Bob Marley")
    create_test_user("Charlie Brown")
    
    response = client.get("/users/?name_contains=alice")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Alice Wonderland"
    
    # Регистронезависимый поиск
    response = client.get("/users/?name_contains=marley")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Bob Marley"


def test_get_users_with_sorting(client, create_test_user):
    """Тест сортировки пользователей"""
    create_test_user("Charlie")
    create_test_user("Alice")
    create_test_user("Bob")
    
    # Сортировка по возрастанию
    response = client.get("/users/?sort=name")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    names = [user["name"] for user in data[:3]]
    assert names == ["Alice", "Bob", "Charlie"]
    
    # Сортировка по убыванию
    response = client.get("/users/?sort=-name")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    names = [user["name"] for user in data[:3]]
    assert names == ["Charlie", "Bob", "Alice"]


def test_get_users_with_pagination(client, create_test_user):
    """Тест пагинации пользователей"""
    # Создаем 15 пользователей
    for i in range(15):
        create_test_user(f"User{i}")
    
    # Первая страница (лимит 10)
    response = client.get("/users/?limit=10&offset=0")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10
    
    # Вторая страница
    response = client.get("/users/?limit=10&offset=10")
    data = response.json()
    assert len(data) == 5


def test_get_user_by_id(client, create_test_user):
    """Тест получения пользователя по ID"""
    user = create_test_user("Unique User")
    
    response = client.get(f"/users/{user.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user.id
    assert data["name"] == "Unique User"


def test_get_user_not_found(client):
    """Тест получения несуществующего пользователя"""
    response = client.get("/users/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"


def test_update_user(client, create_test_user):
    """Тест обновления пользователя"""
    user = create_test_user("Old Name")
    
    response = client.put(f"/users/{user.id}", json={"name": "New Name"})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user.id
    assert data["name"] == "New Name"
    
    # Проверяем, что обновление сохранилось
    response = client.get(f"/users/{user.id}")
    assert response.json()["name"] == "New Name"


def test_update_user_not_found(client):
    """Тест обновления несуществующего пользователя"""
    response = client.put("/users/99999", json={"name": "New Name"})
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"


def test_delete_user(client, create_test_user):
    """Тест удаления пользователя"""
    user = create_test_user("To Be Deleted")
    
    response = client.delete(f"/users/{user.id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Проверяем, что пользователь действительно удален
    response = client.get(f"/users/{user.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_not_found(client):
    """Тест удаления несуществующего пользователя"""
    response = client.delete("/users/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"

def test_delete_users_range(client, create_test_user):
    u1 = create_test_user("U1")
    u2 = create_test_user("U2")
    u3 = create_test_user("U3")
    u4 = create_test_user("U4")

    response = client.delete(
        f"/users/?from={u2.id}&to={u3.id}"
    )

    assert response.status_code == 204

    r1 = client.get(f"/users/{u1.id}")
    r2 = client.get(f"/users/{u2.id}")
    r3 = client.get(f"/users/{u3.id}")
    r4 = client.get(f"/users/{u4.id}")

    assert r1.status_code == 200
    assert r2.status_code == 404
    assert r3.status_code == 404
    assert r4.status_code == 200

def test_delete_users_range_invalid(client):
    response = client.delete("/users/?from=10&to=5")

    assert response.status_code == 400

def test_delete_users_range_not_found(client):
    response = client.delete("/users/?from=1000&to=2000")

    assert response.status_code == 404
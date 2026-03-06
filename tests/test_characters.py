import pytest
from fastapi import status


def test_create_character(client, create_test_user):
    """Тест создания персонажа"""
    user = create_test_user("Character Owner")
    
    response = client.post("/characters/", json={
        "name": "Test Character",
        "level": 5,
        "health": 150,
        "exp": 1200,
        "user_id": user.id
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Character"
    assert data["level"] == 5
    assert data["health"] == 150
    assert data["exp"] == 1200
    assert data["user_id"] == user.id
    assert "id" in data


def test_create_character_user_not_found(client):
    """Тест создания персонажа для несуществующего пользователя"""
    response = client.post("/characters/", json={
        "name": "Orphan Character",
        "level": 1,
        "health": 100,
        "exp": 0,
        "user_id": 99999
    })
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"


def test_get_characters_empty(client):
    """Тест получения списка персонажей, когда нет ни одного"""
    response = client.get("/characters/")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_characters(client, create_test_user, create_test_character):
    """Тест получения списка персонажей"""
    user1 = create_test_user("User 1")
    user2 = create_test_user("User 2")
    
    char1 = create_test_character("Character 1", user1.id, level=10, health=200, exp=5000)
    char2 = create_test_character("Character 2", user1.id, level=5, health=120, exp=1500)
    char3 = create_test_character("Character 3", user2.id, level=8, health=180, exp=3000)
    
    response = client.get("/characters/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3
    names = [char["name"] for char in data]
    assert "Character 1" in names
    assert "Character 2" in names
    assert "Character 3" in names


def test_get_characters_filter_by_user(client, create_test_user, create_test_character):
    """Тест фильтрации персонажей по пользователю"""
    user1 = create_test_user("Owner 1")
    user2 = create_test_user("Owner 2")
    
    create_test_character("User1 Char 1", user1.id)
    create_test_character("User1 Char 2", user1.id)
    create_test_character("User2 Char", user2.id)
    
    response = client.get(f"/characters/?user_id={user1.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(char["user_id"] == user1.id for char in data)
    
    response = client.get(f"/characters/?user_id={user2.id}")
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == user2.id


def test_get_characters_filter_by_name(client, create_test_user, create_test_character):
    """Тест фильтрации персонажей по имени"""
    user = create_test_user("Filter Test")
    
    create_test_character("Warrior Max", user.id)
    create_test_character("Warrior John", user.id)
    create_test_character("Mage Alice", user.id)
    
    response = client.get("/characters/?name_contains=warrior")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all("warrior" in char["name"].lower() for char in data)


def test_get_characters_with_sorting(client, create_test_user, create_test_character):
    """Тест сортировки персонажей"""
    user = create_test_user("Sort Test")
    
    create_test_character("Z", user.id, level=3)
    create_test_character("A", user.id, level=1)
    create_test_character("M", user.id, level=2)
    
    # Сортировка по имени (возрастание)
    response = client.get("/characters/?sort=name")
    data = response.json()[:3]
    names = [char["name"] for char in data]
    assert names == ["A", "M", "Z"]
    
    # Сортировка по имени (убывание)
    response = client.get("/characters/?sort=-name")
    data = response.json()[:3]
    names = [char["name"] for char in data]
    assert names == ["Z", "M", "A"]
    
    # Сортировка по уровню (возрастание)
    response = client.get("/characters/?sort=level")
    data = response.json()[:3]
    levels = [char["level"] for char in data]
    assert levels == [1, 2, 3]
    
    # Сортировка по уровню (убывание)
    response = client.get("/characters/?sort=-level")
    data = response.json()[:3]
    levels = [char["level"] for char in data]
    assert levels == [3, 2, 1]


def test_get_characters_with_pagination(client, create_test_user, create_test_character):
    """Тест пагинации персонажей"""
    user = create_test_user("Pagination Test")
    
    for i in range(15):
        create_test_character(f"Character{i}", user.id)
    
    response = client.get("/characters/?limit=10&offset=0")
    data = response.json()
    assert len(data) == 10
    
    response = client.get("/characters/?limit=10&offset=10")
    data = response.json()
    assert len(data) == 5


def test_get_character_by_id(client, create_test_user, create_test_character):
    """Тест получения персонажа по ID"""
    user = create_test_user("Owner")
    character = create_test_character("Specific Character", user.id, level=7, health=170, exp=2500)
    
    response = client.get(f"/characters/{character.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == character.id
    assert data["name"] == "Specific Character"
    assert data["level"] == 7
    assert data["health"] == 170
    assert data["exp"] == 2500
    assert data["user_id"] == user.id


def test_get_character_not_found(client):
    """Тест получения несуществующего персонажа"""
    response = client.get("/characters/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Character not found"


def test_update_character(client, create_test_user, create_test_character):
    """Тест обновления персонажа"""
    user = create_test_user("Owner")
    character = create_test_character("Old Name", user.id, level=1, health=100, exp=0)
    
    response = client.put(f"/characters/{character.id}", json={
        "name": "New Name",
        "level": 10,
        "health": 200,
        "exp": 5000
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == character.id
    assert data["name"] == "New Name"
    assert data["level"] == 10
    assert data["health"] == 200
    assert data["exp"] == 5000
    assert data["user_id"] == user.id
    
    # Проверяем, что изменения сохранились
    response = client.get(f"/characters/{character.id}")
    data = response.json()
    assert data["name"] == "New Name"
    assert data["level"] == 10
    assert data["health"] == 200
    assert data["exp"] == 5000


def test_update_character_partial(client, create_test_user, create_test_character):
    """Тест частичного обновления персонажа (только имя)"""
    user = create_test_user("Owner")
    character = create_test_character("Old Name", user.id, level=5, health=150, exp=1000)
    
    response = client.put(f"/characters/{character.id}", json={
        "name": "New Name Only"
        # level, health, exp не передаем
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "New Name Only"
    assert data["level"] == 5  # не изменилось
    assert data["health"] == 150
    assert data["exp"] == 1000


def test_update_character_not_found(client):
    """Тест обновления несуществующего персонажа"""
    response = client.put("/characters/99999", json={
        "name": "New Name"
    })
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Character not found"


def test_delete_character(client, create_test_user, create_test_character):
    """Тест удаления персонажа"""
    user = create_test_user("Owner")
    character = create_test_character("To Be Deleted", user.id)
    
    response = client.delete(f"/characters/{character.id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Проверяем, что персонаж действительно удален
    response = client.get(f"/characters/{character.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_character_not_found(client):
    """Тест удаления несуществующего персонажа"""
    response = client.delete("/characters/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Character not found"


def test_get_character_items(client, create_test_user, create_test_character, create_test_item):
    """Тест получения предметов персонажа"""
    user = create_test_user("Owner")
    character = create_test_character("Hero", user.id)
    other_character = create_test_character("Other", user.id)
    
    item1 = create_test_item("Sword", character.id)
    item2 = create_test_item("Shield", character.id)
    item3 = create_test_item("Potion", other_character.id)  # предмет другого персонажа
    
    response = client.get(f"/characters/{character.id}/items")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    item_names = [item["name"] for item in data]
    assert "Sword" in item_names
    assert "Shield" in item_names
    assert "Potion" not in item_names
    assert all(item["character_id"] == character.id for item in data)


def test_get_character_items_character_not_found(client):
    """Тест получения предметов для несуществующего персонажа"""
    response = client.get("/characters/99999/items")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Character not found"


def test_get_character_user(client, create_test_user, create_test_character):
    """Тест получения владельца персонажа"""
    user = create_test_user("Owner Name")
    character = create_test_character("Hero", user.id)
    
    response = client.get(f"/characters/{character.id}/user")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user.id
    assert data["name"] == "Owner Name"


def test_get_character_user_character_not_found(client):
    """Тест получения владельца для несуществующего персонажа"""
    response = client.get("/characters/99999/user")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Character not found"
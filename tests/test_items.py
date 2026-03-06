import pytest
from fastapi import status

def test_create_item(client, create_test_user, create_test_character):
    """Тест создания предмета"""
    user = create_test_user("Item Owner")
    character = create_test_character("Test Character", user.id)
    
    response = client.post("/items/", json={
        "name": "Test Item",
        "character_id": character.id
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["character_id"] == character.id
    assert "id" in data


def test_create_item_character_not_exists(client):
    """Тест создания предмета для несуществующего персонажа"""
    response = client.post("/items/", json={
        "name": "Orphan Item",
        "character_id": 99999
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"


def test_get_items_empty(client):
    """Тест получения списка предметов, когда нет ни одного"""
    response = client.get("/items/")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_items(client, create_test_user, create_test_character, create_test_item):
    """Тест получения списка предметов"""
    user = create_test_user("User 1")
    character1 = create_test_character("Character 1", user.id)
    character2 = create_test_character("Character 2", user.id)
    
    item1 = create_test_item("Item 1", character1.id)
    item2 = create_test_item("Item 2", character1.id)
    item3 = create_test_item("Item 3", character2.id)
    
    response = client.get("/items/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3
    item_names = [item["name"] for item in data]
    assert "Item 1" in item_names
    assert "Item 2" in item_names
    assert "Item 3" in item_names


def test_get_items_filter_by_character(client, create_test_user, create_test_character, create_test_item):
    """Тест фильтрации предметов по персонажу"""
    user = create_test_user("Owner")
    character1 = create_test_character("Character 1", user.id)
    character2 = create_test_character("Character 2", user.id)
    
    create_test_item("Char1 Item 1", character1.id)
    create_test_item("Char1 Item 2", character1.id)
    create_test_item("Char2 Item", character2.id)
    
    response = client.get(f"/items/?character_id={character1.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(item["character_id"] == character1.id for item in data)
    
    response = client.get(f"/items/?character_id={character2.id}")
    data = response.json()
    assert len(data) == 1
    assert data[0]["character_id"] == character2.id


def test_get_items_filter_by_name(client, create_test_user, create_test_character, create_test_item):
    """Тест фильтрации предметов по имени"""
    user = create_test_user("Filter Test")
    character = create_test_character("Test Character", user.id)
    
    create_test_item("Smartphone iPhone", character.id)
    create_test_item("Smartphone Samsung", character.id)
    create_test_item("Laptop Dell", character.id)
    
    response = client.get("/items/?name_contains=smartphone")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all("smartphone" in item["name"].lower() for item in data)


def test_get_items_with_sorting(client, create_test_user, create_test_character, create_test_item):
    """Тест сортировки предметов"""
    user = create_test_user("Sort Test")
    character = create_test_character("Test Character", user.id)
    
    create_test_item("Z", character.id)
    create_test_item("A", character.id)
    create_test_item("M", character.id)
    
    response = client.get("/items/?sort=name")
    data = response.json()[:3]
    names = [item["name"] for item in data]
    assert names == ["A", "M", "Z"]
    
    response = client.get("/items/?sort=-name")
    data = response.json()[:3]
    names = [item["name"] for item in data]
    assert names == ["Z", "M", "A"]


def test_get_items_with_pagination(client, create_test_user, create_test_character, create_test_item):
    """Тест пагинации предметов"""
    user = create_test_user("Pagination Test")
    character = create_test_character("Test Character", user.id)
    
    for i in range(15):
        create_test_item(f"Item{i}", character.id)
    
    response = client.get("/items/?limit=10&offset=0")
    data = response.json()
    assert len(data) == 10
    
    response = client.get("/items/?limit=10&offset=10")
    data = response.json()
    assert len(data) == 5


def test_get_item_by_id(client, create_test_user, create_test_character, create_test_item):
    """Тест получения предмета по ID"""
    user = create_test_user("Item Owner")
    character = create_test_character("Test Character", user.id)
    item = create_test_item("Specific Item", character.id)
    
    response = client.get(f"/items/{item.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == item.id
    assert data["name"] == "Specific Item"
    assert data["character_id"] == character.id


def test_get_item_not_found(client):
    """Тест получения несуществующего предмета"""
    response = client.get("/items/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item not found"


def test_update_item(client, create_test_user, create_test_character, create_test_item):
    """Тест обновления предмета"""
    user = create_test_user("Owner")
    character1 = create_test_character("Original Character", user.id)
    character2 = create_test_character("New Character", user.id)
    item = create_test_item("Old Name", character1.id)
    
    response = client.put(f"/items/{item.id}", json={
        "name": "New Name",
        "character_id": character2.id
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == item.id
    assert data["name"] == "New Name"
    assert data["character_id"] == character2.id
    
    # Проверяем, что изменения сохранились
    response = client.get(f"/items/{item.id}")
    data = response.json()
    assert data["name"] == "New Name"
    assert data["character_id"] == character2.id


def test_update_item_not_found(client, create_test_user, create_test_character):
    """Тест обновления несуществующего предмета"""
    user = create_test_user("Some User")
    character = create_test_character("Test Character", user.id)
    
    response = client.put("/items/99999", json={
        "name": "New Name",
        "character_id": character.id
    })
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item not found"


def test_update_item_character_not_found(client, create_test_user, create_test_character, create_test_item):
    """Тест обновления предмета с несуществующим персонажем"""
    user = create_test_user("Owner")
    character = create_test_character("Test Character", user.id)
    item = create_test_item("Test Item", character.id)
    
    response = client.put(f"/items/{item.id}", json={
        "name": "New Name",
        "character_id": 99999
    })
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Character not found"


def test_delete_item(client, create_test_user, create_test_character, create_test_item):
    """Тест удаления предмета"""
    user = create_test_user("Item Owner")
    character = create_test_character("Test Character", user.id)
    item = create_test_item("To Be Deleted", character.id)
    
    response = client.delete(f"/items/{item.id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Проверяем, что предмет действительно удален
    response = client.get(f"/items/{item.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_item_not_found(client):
    """Тест удаления несуществующего предмета"""
    response = client.delete("/items/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item not found"


def test_get_items_by_character(client, create_test_user, create_test_character, create_test_item):
    """Тест получения предметов конкретного персонажа через /by_character/{character_id}"""
    user = create_test_user("Target User")
    character = create_test_character("Target Character", user.id)
    other_character = create_test_character("Other Character", user.id)
    
    create_test_item("Char Item 1", character.id)
    create_test_item("Char Item 2", character.id)
    create_test_item("Other Char Item", other_character.id)
    
    response = client.get(f"/items/by_character/{character.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(item["character_id"] == character.id for item in data)
    
    # Проверяем, что предметы другого персонажа не попали в результат
    other_ids = [item["character_id"] for item in data if item["character_id"] == other_character.id]
    assert len(other_ids) == 0


def test_get_items_by_character_not_found(client):
    """Тест получения предметов для несуществующего персонажа"""
    response = client.get("/items/by_character/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Character not found"


def test_get_items_by_character_filtered(client, create_test_user, create_test_character, create_test_item):
    """Тест фильтрации предметов персонажа через /by_character/{character_id}"""
    user = create_test_user("Filter User")
    character = create_test_character("Test Character", user.id)
    
    create_test_item("Red Car", character.id)
    create_test_item("Blue Car", character.id)
    create_test_item("Red Bike", character.id)
    
    response = client.get(f"/items/by_character/{character.id}?name_contains=car")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all("car" in item["name"].lower() for item in data)


def test_get_items_by_character_sorted(client, create_test_user, create_test_character, create_test_item):
    """Тест сортировки предметов персонажа через /by_character/{character_id}"""
    user = create_test_user("Sort User")
    character = create_test_character("Test Character", user.id)
    
    create_test_item("Zoo", character.id)
    create_test_item("Apple", character.id)
    create_test_item("Mango", character.id)
    
    response = client.get(f"/items/by_character/{character.id}?sort=name")
    data = response.json()
    names = [item["name"] for item in data]
    assert names == ["Apple", "Mango", "Zoo"]
    
    response = client.get(f"/items/by_character/{character.id}?sort=-name")
    data = response.json()
    names = [item["name"] for item in data]
    assert names == ["Zoo", "Mango", "Apple"]
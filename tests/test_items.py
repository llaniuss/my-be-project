from app import models


def test_create_item(client, test_db):
    user = models.User(name="Owner")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    response = client.post("/items", json={"name": "Sword", "owner_id": user.id})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Sword"
    assert data["owner_id"] == user.id

    # verify
    item_in_db = test_db.query(models.Item).filter_by(id=data["id"]).first()
    assert item_in_db is not None
    assert item_in_db.name == "Sword"


def test_get_items(client, test_db):
    user = models.User(name="User")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    item = models.Item(name="Sword", owner_id=user.id)
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)

    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_user_items(client, test_db):
    user = models.User(name="Test User")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    items = [
        models.Item(name="Sword", owner_id=user.id),
        models.Item(name="Shield", owner_id=user.id),
        models.Item(name="Potion", owner_id=user.id),
    ]
    test_db.add_all(items)
    test_db.commit()
    for it in items:
        test_db.refresh(it)

    response = client.get(f"/users/{user.id}/items?name_contains=Sword")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Sword"


def test_get_user_items_sort(client, test_db):
    user = models.User(name="User")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    test_db.add_all([
        models.Item(name="A", owner_id=user.id),
        models.Item(name="C", owner_id=user.id),
        models.Item(name="B", owner_id=user.id),
    ])
    test_db.commit()

    # refresh items not strictly required here, but fine to keep if needed
    response = client.get(f"/users/{user.id}/items?sort=-name")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "C"
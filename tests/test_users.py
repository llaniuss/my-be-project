from app import models


def test_create_user(client, test_db):
    response = client.post("/users", json={"name": "John"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John"
    assert "id" in data

    # verify record is really in test_db
    user_in_db = test_db.query(models.User).filter_by(id=data["id"]).first()
    assert user_in_db is not None
    assert user_in_db.name == "John"


def test_get_users(client, test_db):
    user1 = models.User(name="A")
    user2 = models.User(name="B")
    test_db.add_all([user1, user2])
    test_db.commit()
    test_db.refresh(user1)
    test_db.refresh(user2)

    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user(client, test_db):
    user = models.User(name="Test")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    response = client.get(f"/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id


def test_get_user_not_found(client, test_db):
    response = client.get("/users/9999")
    assert response.status_code == 404


def test_update_user(client, test_db):
    user = models.User(name="Old")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    response = client.put(f"/users/{user.id}", json={"name": "New"})
    assert response.status_code == 200
    assert response.json()["name"] == "New"


def test_delete_user(client, test_db):
    user = models.User(name="To delete")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    response = client.delete(f"/users/{user.id}")
    assert response.status_code == 204

    user_in_db = test_db.query(models.User).filter(models.User.id == user.id).first()
    assert user_in_db is None


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

    # filter
    response = client.get(f"/users/{user.id}/items?name_contains=Sword")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Sword"

    # sort desc
    response = client.get(f"/users/{user.id}/items?sort=-name")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Sword"

    # pagination
    response = client.get(f"/users/{user.id}/items?limit=2&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 2
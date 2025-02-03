from datetime import datetime

from httpx import AsyncClient
from litestar import status_codes

from src.versions import ApiVersion
from src.modules.product.models import Product


Model = Product
endpoint = f"{ApiVersion.V1}/{Model._meta.tablename}"


async def test_create_one(client: AsyncClient):
    response = await client.post(
        endpoint,
        json={
            "title": "test_create_product_title",
            "description": "test_create_product_description",
            "price": 5,
        },
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_create_product_title"
    assert item["description"] == "test_create_product_description"
    assert item["price"] == 5
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])

    db_item = await Product.read_one(item["id"])
    assert db_item.title == "test_create_product_title"
    assert db_item.description == "test_create_product_description"
    assert db_item.price == 5


async def test_create_one_raises_error_for_duplicate(client: AsyncClient):
    data = {
        "title": "test_create_one_raises_error_for_duplicate_title",
        "description": "test_create_one_raises_error_for_duplicate_description",
        "price": 5,
    }

    item = Product(**data)
    await item.save()
    await item.refresh()

    response = await client.post(
        endpoint,
        json=data,
    )
    assert response.status_code == status_codes.HTTP_409_CONFLICT
    assert response.json() == {
        "status_code": 409,
        "detail": 'duplicate key value violates unique constraint "product_title_key"\nDETAIL:  Key (title)=(test_create_one_raises_error_for_duplicate_title) already exists.',
    }


async def test_read_one(client: AsyncClient):
    item = Product(
        title="test_read_product_title",
        description="test_read_product_description",
        price=5,
    )
    await item.save()
    await item.refresh()

    response = await client.get(f"{endpoint}/{item.id}")
    assert response.status_code == status_codes.HTTP_200_OK
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_read_product_title"
    assert item["description"] == "test_read_product_description"
    assert item["price"] == 5
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])


async def test_read_one_raises_error_if_not_exists(client: AsyncClient):
    # Get max id in db
    max_id = await Product.max_id()
    not_exist_id = max_id + 1
    assert not await Product.exists().where(Product.id == not_exist_id)

    response = await client.get(
        f"{endpoint}/{not_exist_id}"
    )
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
    assert response.json() == {
        "status_code": 404,
        "detail": f"Product with id='{not_exist_id}' not found.",
    }


async def test_update_one(client: AsyncClient):
    item = Product(
        title="test_update_product_title",
        description="test_update_product_description",
        price=5,
    )
    await item.save()
    await item.refresh()

    response = await client.patch(
        f"{endpoint}/{item.id}",
        json={
            "title": "test_update_product_title_updated",
            "description": "test_update_product_description_updated",
            "price": 4,
        },
    )
    assert response.status_code == status_codes.HTTP_200_OK
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_update_product_title_updated"
    assert item["description"] == "test_update_product_description_updated"
    assert item["price"] == 4
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])

    db_item = await Product.read_one(item["id"])
    assert db_item.title == "test_update_product_title_updated"
    assert db_item.description == "test_update_product_description_updated"
    assert db_item.price == 4


async def test_update_one_raises_error_if_not_exists(client: AsyncClient):
    # Get max id in db
    max_id = await Product.max_id()
    not_exist_id = max_id + 1
    assert not await Product.exists().where(Product.id == not_exist_id)

    response = await client.patch(
        f"{ApiVersion.V1}/{Model._meta.tablename}/{not_exist_id}",
        json={
            "title": "test_update_product_title_updated",
            "description": "test_update_product_description_updated",
            "price": 4,
        },
    )
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
    assert response.json() == {
        "status_code": 404,
        "detail": f"Product with id='{not_exist_id}' not found.",
    }


async def test_update_one_allows_partial(client: AsyncClient):
    item = Product(
        title="test_update_one_allows_partial_title",
        description="test_update_one_allows_partial_description",
        price=5,
    )
    await item.save()
    await item.refresh()

    response = await client.patch(
        f"{endpoint}/{item.id}",
        json={
            "description": "test_update_one_allows_partial_description_updated",
            "price": 4,
        },
    )
    assert response.status_code == status_codes.HTTP_200_OK
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_update_one_allows_partial_title"
    assert item["description"] == "test_update_one_allows_partial_description_updated"
    assert item["price"] == 4
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])

    db_item = await Product.read_one(item["id"])
    assert db_item.title == "test_update_one_allows_partial_title"
    assert db_item.description == "test_update_one_allows_partial_description_updated"
    assert db_item.price == 4


async def test_upsert_one_create_new(client: AsyncClient):
    # Verify that the item does not exist
    assert not await Product.exists().where(
        Product.title == "test_upsert_one_create_new_title",
        Product.description == "test_upsert_one_create_new_description",
        Product.price == 5,
    )

    response = await client.put(
        endpoint,
        json={
            "title": "test_upsert_one_create_new_title",
            "description": "test_upsert_one_create_new_description",
            "price": 5,
        },
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_upsert_one_create_new_title"
    assert item["description"] == "test_upsert_one_create_new_description"
    assert item["price"] == 5
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])

    db_item = await Product.read_one(item["id"])
    assert db_item.title == "test_upsert_one_create_new_title"
    assert db_item.description == "test_upsert_one_create_new_description"
    assert db_item.price == 5


async def test_upsert_one_update(client: AsyncClient):
    item = Product(
        title="test_upsert_one_update_title",
        description="test_upsert_one_update_description_old",
        price=5,
    )
    await item.save()
    await item.refresh()

    response = await client.put(
        endpoint,
        json={
            "title": "test_upsert_one_update_title",
            "description": "test_upsert_one_update_description_new",
            "price": 4,
        },
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_upsert_one_update_title"
    assert item["description"] == "test_upsert_one_update_description_new"
    assert item["price"] == 4
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])

    db_item = await Product.read_one(item["id"])
    assert db_item.title == "test_upsert_one_update_title"
    assert db_item.description == "test_upsert_one_update_description_new"
    assert db_item.price == 4


async def test_delete_one(client: AsyncClient):
    item = Product(
        title="test_delete_product_title",
        description="test_delete_product_description",
        price=5,
    )
    await item.save()
    await item.refresh()

    response = await client.delete(f"{endpoint}/{item.id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT
    assert not await Product.exists().where(Product.id == item.id)


async def test_read_count(client: AsyncClient):
    # Delete all items
    await Product.delete_all(force=True)

    # Create 2 items
    items = []
    for i in range(2):
        item = Product(
            title=f"test_read_count_product_title_{i}",
            description=f"test_read_count_product_description_{i}",
            price=i,
        )
        await item.save()
        await item.refresh()
        items.append(item)

    response = await client.get(f"{endpoint}/count")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == 2


async def test_read_all(client: AsyncClient):
    # Delete all items
    await Product.delete_all(force=True)

    # Create 2 items
    items = []
    for i in range(2):
        item = Product(
            title=f"test_read_all_product_title_{i}",
            description=f"test_read_all_product_description_{i}",
            price=i,
        )
        await item.save()
        await item.refresh()
        items.append(item)

    response = await client.get(
        endpoint,
        params={
            "offset": 0,
            "limit": 10,
        },
    )
    assert response.status_code == status_codes.HTTP_200_OK
    items_response = response.json()
    assert len(items_response) == 2
    # assert response.headers["X-Total-Count"] == "2"
    # assert response.headers["X-Offset"] == "0"
    # assert response.headers["X-Limit"] == "10"
    for i, item in enumerate(items_response):
        assert isinstance(item["id"], int)
        assert item["title"] == f"test_read_all_product_title_{i}"
        assert item["description"] == f"test_read_all_product_description_{i}"
        assert item["price"] == i
        assert datetime.fromisoformat(item["created_at"])
        assert datetime.fromisoformat(item["updated_at"])


async def test_create_many(client: AsyncClient):
    # Delete all items
    await Product.delete_all(force=True)

    item1 = {
        "title": "test_create_many_product_title_1",
        "description": "test_create_many_product_description_1",
        "price": 1,
    }
    item2 = {
        "title": "test_create_many_product_title_2",
        "description": "test_create_many_product_description_2",
        "price": 2,
    }

    response = await client.post(
        f"{endpoint}/many", json=[item1, item2]
    )

    assert response.status_code == status_codes.HTTP_201_CREATED
    items = response.json()
    assert len(items["ids"]) == 2

    # Get item1 from db
    db_item1 = await Product.read_one(items["ids"][0])
    assert db_item1.title == item1["title"]
    assert db_item1.description == item1["description"]
    assert db_item1.price == item1["price"]

    # Get item 2 from db
    db_item2 = await Product.read_one(items["ids"][1])
    assert db_item2.title == item2["title"]
    assert db_item2.description == item2["description"]
    assert db_item2.price == item2["price"]


async def test_create_many_raises_error_for_duplicate(client: AsyncClient):
    # Delete all items
    await Product.delete_all(force=True)

    item1 = {
        "title": "test_create_many_raises_error_for_duplicate_product_title_1",
        "description": "test_create_many_raises_error_for_duplicate_product_description_1",
        "price": 1,
    }

    # Create item1 directly
    db_item1 = Product(**item1)
    await db_item1.save()

    item2 = {
        "title": "test_create_many_raises_error_for_duplicate_product_title_2",
        "description": "test_create_many_raises_error_for_duplicate_product_description_2",
        "price": 2,
    }

    response = await client.post(
        f"{endpoint}/many", json=[item1, item2]
    )
    assert response.status_code == status_codes.HTTP_409_CONFLICT
    assert response.json() == {
        "status_code": 409,
        "detail": 'duplicate key value violates unique constraint "product_title_key"\nDETAIL:  Key (title)=(test_create_many_raises_error_for_duplicate_product_title_1) already exists.',
    }


async def test_update_many(client: AsyncClient):
    # Delete all items
    await Product.delete_all(force=True)

    item1 = {
        "title": "test_update_many_product_title_1",
        "description": "test_update_many_product_description_1",
        "price": 1,
    }
    item2 = {
        "title": "test_update_many_product_title_2",
        "description": "test_update_many_product_description_2",
        "price": 2,
    }

    # Create item1 and item2 directly
    db_item1 = Product(**item1)
    await db_item1.save()
    db_item2 = Product(**item2)
    await db_item2.save()

    item1_update = {
        "id": db_item1.id,
        "title": "test_update_many_product_title_1",
        # "description": "test_update_many_product_description_1_updated", # Omit optional field to test partial update
        "price": 3,
    }
    item2_update = {
        "id": db_item2.id,
        # "title": "test_update_many_product_title_2", # Omit required field to test partial update
        "description": "test_update_many_product_description_2_updated",
        "price": 4,
    }

    response = await client.patch(
        f"{endpoint}/many", json=[item1_update, item2_update]
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items["ids"]) == 2

    # Get item1 from db
    db_item1 = await Product.read_one(items["ids"][0])
    assert db_item1.title == item1_update["title"]
    assert db_item1.description == "test_update_many_product_description_1"
    assert db_item1.price == item1_update["price"]

    # Get item 2 from db
    db_item2 = await Product.read_one(items["ids"][1])
    assert db_item2.title == "test_update_many_product_title_2"
    assert db_item2.description == item2_update["description"]
    assert db_item2.price == item2_update["price"]


async def test_upsert_many_create_new(client: AsyncClient):
    # Delete all items
    await Product.delete_all(force=True)

    item1 = {
        "title": "test_upsert_many_create_new_product_title_1",
        "description": "test_upsert_many_create_new_product_description_1",
        "price": 1,
    }
    item2 = {
        "title": "test_upsert_many_create_new_product_title_2",
        "description": "test_upsert_many_create_new_product_description_2",
        "price": 2,
    }

    response = await client.put(
        f"{endpoint}/many", json=[item1, item2]
    )

    assert response.status_code == status_codes.HTTP_201_CREATED
    items = response.json()
    assert len(items["ids"]) == 2

    # Get item1 from db
    db_item1 = await Product.read_one(items["ids"][0])
    assert db_item1.title == item1["title"]
    assert db_item1.description == item1["description"]
    assert db_item1.price == item1["price"]

    # Get item 2 from db
    db_item2 = await Product.read_one(items["ids"][1])
    assert db_item2.title == item2["title"]
    assert db_item2.description == item2["description"]
    assert db_item2.price == item2["price"]


async def test_upsert_many_create_one_update_one(client: AsyncClient):
    # Delete all items
    await Product.delete_all(force=True)

    item1 = {
        "title": "test_upsert_many_create_one_update_one_product_title_1",
        "description": "test_upsert_many_create_one_update_one_product_description_1",
        "price": 1,
    }
    item2 = {
        "title": "test_upsert_many_create_one_update_one_product_title_2",
        "description": "test_upsert_many_create_one_update_one_product_description_2",
        "price": 2,
    }

    item1_update = {
        "title": "test_upsert_many_create_one_update_one_product_title_1",  # Same title
        "description": "test_upsert_many_create_one_update_one_product_description_1_updated",
        "price": 3,
    }

    # Create item1 directly
    db_item1 = Product(**item1)
    await db_item1.save()
    await db_item1.refresh()

    # Call upsert_many with item1 and item2
    response = await client.put(
        f"{endpoint}/many", json=[item1_update, item2]
    )

    assert response.status_code == status_codes.HTTP_201_CREATED
    items = response.json()
    assert len(items["ids"]) == 2

    # Get item1 from db
    db_item1 = await Product.read_one(items["ids"][0])
    assert db_item1.title == item1_update["title"]
    assert db_item1.description == item1_update["description"]
    assert db_item1.price == item1_update["price"]

    # Get item 2 from db
    db_item2 = await Product.read_one(items["ids"][1])
    assert db_item2.title == item2["title"]
    assert db_item2.description == item2["description"]
    assert db_item2.price == item2["price"]


async def test_delete_all(client: AsyncClient):
    await Product.delete_all(force=True)

    # Create 2 items
    items = []
    for i in range(2):
        item = Product(
            title=f"test_delete_all_product_title_{i}",
            description=f"test_delete_all_product_description_{i}",
            price=i,
        )
        await item.save()
        await item.refresh()
        items.append(item)

    assert await Product.count() == 2

    # Call delete_all
    response = await client.delete(endpoint)
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT
    assert await Product.count() == 0

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
            "price": 5.0,
        },
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_create_product_title"
    assert item["description"] == "test_create_product_description"
    assert item["price"] == 5.0
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])

    db_item = await Product.read_one(item["id"])
    assert db_item.title == "test_create_product_title"
    assert db_item.description == "test_create_product_description"
    assert db_item.price == 5.0


async def test_create_one_raises_error_for_duplicate(client: AsyncClient):
    data = {
        "title": "test_create_one_raises_error_for_duplicate_title",
        "description": "test_create_one_raises_error_for_duplicate_description",
        "price": 5.0,
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
        price=5.0,
    )
    await item.save()
    await item.refresh()

    response = await client.get(f"{endpoint}/{item.id}")
    assert response.status_code == status_codes.HTTP_200_OK
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_read_product_title"
    assert item["description"] == "test_read_product_description"
    assert item["price"] == 5.0
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
        price=5.0,
    )
    await item.save()
    await item.refresh()

    response = await client.patch(
        f"{endpoint}/{item.id}",
        json={
            "title": "test_update_product_title_updated",
            "description": "test_update_product_description_updated",
            "price": 4.0,
        },
    )
    assert response.status_code == status_codes.HTTP_200_OK
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_update_product_title_updated"
    assert item["description"] == "test_update_product_description_updated"
    assert item["price"] == 4.0
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])

    db_item = await Product.read_one(item["id"])
    assert db_item.title == "test_update_product_title_updated"
    assert db_item.description == "test_update_product_description_updated"
    assert db_item.price == 4.0


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
            "price": 4.0,
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
        price=5.0,
    )
    await item.save()
    await item.refresh()

    response = await client.patch(
        f"{endpoint}/{item.id}",
        json={
            "description": "test_update_one_allows_partial_description_updated",
            "price": 4.0,
        },
    )
    assert response.status_code == status_codes.HTTP_200_OK
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_update_one_allows_partial_title"
    assert item["description"] == "test_update_one_allows_partial_description_updated"
    assert item["price"] == 4.0
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])

    db_item = await Product.read_one(item["id"])
    assert db_item.title == "test_update_one_allows_partial_title"
    assert db_item.description == "test_update_one_allows_partial_description_updated"
    assert db_item.price == 4.0


# async def test_update_one_applies_null(client: AsyncClient):
#     item = Product(
#         title="test_update_one_applies_null_title",
#         description="test_update_one_applies_null_description",
#         price=5.0,
#     )
#     await item.save()
#     await item.refresh()

#     response = await client.patch(
#         f"{endpoint}/{item.id}",
#         json={
#             "title": None,
#             "description": None,
#             "price": None,
#         },
#     )
#     assert response.status_code == status_codes.HTTP_200_OK
#     item = response.json()
#     assert isinstance(item["id"], int)
#     assert item["title"] is None
#     assert item["description"] is None
#     assert item["price"] is None
#     assert datetime.fromisoformat(item["created_at"])
#     assert datetime.fromisoformat(item["updated_at"])

#     db_item = await Product.read_one(item["id"])
#     assert db_item.title is None
#     assert db_item.description is None
#     assert db_item.price is None


async def test_upsert_one_create_new(client: AsyncClient):
    # Verify that the item does not exist
    assert not await Product.exists().where(
        Product.title == "test_upsert_one_create_new_title",
        Product.description == "test_upsert_one_create_new_description",
        Product.price == 5.0,
    )

    response = await client.put(
        endpoint,
        json={
            "title": "test_upsert_one_create_new_title",
            "description": "test_upsert_one_create_new_description",
            "price": 5.0,
        },
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_upsert_one_create_new_title"
    assert item["description"] == "test_upsert_one_create_new_description"
    assert item["price"] == 5.0
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])

    db_item = await Product.read_one(item["id"])
    assert db_item.title == "test_upsert_one_create_new_title"
    assert db_item.description == "test_upsert_one_create_new_description"
    assert db_item.price == 5.0


async def test_upsert_one_update(client: AsyncClient):
    item = Product(
        title="test_upsert_one_update_title",
        description="test_upsert_one_update_description_old",
        price=5.0,
    )
    await item.save()
    await item.refresh()

    response = await client.put(
        endpoint,
        json={
            "title": "test_upsert_one_update_title",
            "description": "test_upsert_one_update_description_new",
            "price": 4.0,
        },
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    item = response.json()
    assert isinstance(item["id"], int)
    assert item["title"] == "test_upsert_one_update_title"
    assert item["description"] == "test_upsert_one_update_description_new"
    assert item["price"] == 4.0
    assert datetime.fromisoformat(item["created_at"])
    assert datetime.fromisoformat(item["updated_at"])

    db_item = await Product.read_one(item["id"])
    assert db_item.title == "test_upsert_one_update_title"
    assert db_item.description == "test_upsert_one_update_description_new"
    assert db_item.price == 4.0


async def test_delete_one(client: AsyncClient):
    item = Product(
        title="test_delete_product_title",
        description="test_delete_product_description",
        price=5.0,
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
        "price": 4.0,
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


async def test_search_no_params_returns_all(client: AsyncClient):
    """
    Test that searching with no parameters returns all existing products.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="All_Product_1", description="Desc 1", price=10.0)
    await product1.save()
    product2 = Product(title="All_Product_2", description="Desc 2", price=20.0)
    await product2.save()

    response = await client.post(
        f"{endpoint}/search",
        json={}, # Empty payload
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 2
    # Check if both items are returned (order might not be guaranteed)
    returned_titles = {item["title"] for item in items}
    assert returned_titles == {"All_Product_1", "All_Product_2"}

async def test_search_by_title_partial(client: AsyncClient):
    """
    Test searching by a partial title match.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Laptop Pro X", description="High-end laptop", price=1500.0)
    await product1.save()
    product2 = Product(title="Desktop Mini", description="Compact desktop", price=800.0)
    await product2.save()
    product3 = Product(title="Wireless Pro Mouse", description="Ergonomic mouse", price=75.0)
    await product3.save()

    response = await client.post(
        f"{endpoint}/search",
        json={"title": "Pro"},
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 2
    returned_titles = {item["title"] for item in items}
    assert returned_titles == {"Laptop Pro X", "Wireless Pro Mouse"}

async def test_search_by_title_exact_no_match(client: AsyncClient):
    """
    Test searching by a title that doesn't exist.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Existing Product", description="Desc", price=50.0)
    await product1.save()

    response = await client.post(
        f"{endpoint}/search",
        json={"title": "NonExistent"},
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 0

async def test_search_by_description_partial(client: AsyncClient):
    """
    Test searching by a partial description match.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Product A", description="This has a unique keyword", price=10.0)
    await product1.save()
    product2 = Product(title="Product B", description="Another item description", price=20.0)
    await product2.save()
    product3 = Product(title="Product C", description="Contains the unique term as well", price=30.0)
    await product3.save()

    response = await client.post(
        f"{endpoint}/search",
        json={"description": "unique"},
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 2
    returned_titles = {item["title"] for item in items}
    assert returned_titles == {"Product A", "Product C"}

async def test_search_by_price_min(client: AsyncClient):
    """
    Test searching by minimum price.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Cheap Item", description="Desc 1", price=5.0)
    await product1.save()
    product2 = Product(title="Mid Item", description="Desc 2", price=50.0)
    await product2.save()
    product3 = Product(title="Expensive Item", description="Desc 3", price=100.0)
    await product3.save()

    response = await client.post(
        f"{endpoint}/search",
        json={"price_min": 40.0},
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 2
    returned_titles = {item["title"] for item in items}
    assert returned_titles == {"Mid Item", "Expensive Item"}
    # Also check prices
    returned_prices = {item["price"] for item in items}
    assert returned_prices == {50.0, 100.0}


async def test_search_by_price_max(client: AsyncClient):
    """
    Test searching by maximum price.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Cheap Item", description="Desc 1", price=5.0)
    await product1.save()
    product2 = Product(title="Mid Item", description="Desc 2", price=50.0)
    await product2.save()
    product3 = Product(title="Expensive Item", description="Desc 3", price=100.0)
    await product3.save()

    response = await client.post(
        f"{endpoint}/search",
        json={"price_max": 60.0},
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 2
    returned_titles = {item["title"] for item in items}
    assert returned_titles == {"Cheap Item", "Mid Item"}
    returned_prices = {item["price"] for item in items}
    assert returned_prices == {5.0, 50.0}

async def test_search_by_price_range(client: AsyncClient):
    """
    Test searching by both minimum and maximum price.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Cheap Item", description="Desc 1", price=5.0)
    await product1.save()
    product2 = Product(title="Mid Item 1", description="Desc 2", price=50.0)
    await product2.save()
    product3 = Product(title="Mid Item 2", description="Desc 3", price=75.0)
    await product3.save()
    product4 = Product(title="Expensive Item", description="Desc 4", price=100.0)
    await product4.save()

    response = await client.post(
        f"{endpoint}/search",
        json={"price_min": 40.0, "price_max": 80.0},
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 2
    returned_titles = {item["title"] for item in items}
    assert returned_titles == {"Mid Item 1", "Mid Item 2"}
    returned_prices = {item["price"] for item in items}
    assert returned_prices == {50.0, 75.0}


async def test_search_by_id_min(client: AsyncClient):
    """
    Test searching by minimum ID.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Item 1", description="Desc 1", price=10.0)
    await product1.save()
    await product1.refresh() # Ensure ID is loaded
    product2 = Product(title="Item 2", description="Desc 2", price=20.0)
    await product2.save()
    await product2.refresh() # Ensure ID is loaded
    product3 = Product(title="Item 3", description="Desc 3", price=30.0)
    await product3.save()
    await product3.refresh() # Ensure ID is loaded

    # Assume IDs are sequential and product2 has id > product1.id
    search_id_min = product2.id

    response = await client.post(
        f"{endpoint}/search",
        json={"id_min": search_id_min},
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 2 # Should match product2 and product3
    returned_ids = {item["id"] for item in items}
    assert returned_ids == {product2.id, product3.id}
    for item in items:
        assert item["id"] >= search_id_min

async def test_search_by_id_max(client: AsyncClient):
    """
    Test searching by maximum ID.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Item 1", description="Desc 1", price=10.0)
    await product1.save()
    await product1.refresh()
    product2 = Product(title="Item 2", description="Desc 2", price=20.0)
    await product2.save()
    await product2.refresh()
    product3 = Product(title="Item 3", description="Desc 3", price=30.0)
    await product3.save()
    await product3.refresh()

    search_id_max = product2.id

    response = await client.post(
        f"{endpoint}/search",
        json={"id_max": search_id_max},
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 2 # Should match product1 and product2
    returned_ids = {item["id"] for item in items}
    assert returned_ids == {product1.id, product2.id}
    for item in items:
        assert item["id"] <= search_id_max

async def test_search_by_id_range(client: AsyncClient):
    """
    Test searching by both minimum and maximum ID.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Item 1", description="Desc 1", price=10.0)
    await product1.save()
    await product1.refresh()
    product2 = Product(title="Item 2", description="Desc 2", price=20.0)
    await product2.save()
    await product2.refresh()
    product3 = Product(title="Item 3", description="Desc 3", price=30.0)
    await product3.save()
    await product3.refresh()
    product4 = Product(title="Item 4", description="Desc 4", price=40.0)
    await product4.save()
    await product4.refresh()

    search_id_min = product2.id
    search_id_max = product3.id

    response = await client.post(
        f"{endpoint}/search",
        json={"id_min": search_id_min, "id_max": search_id_max},
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 2 # Should match product2 and product3
    returned_ids = {item["id"] for item in items}
    assert returned_ids == {product2.id, product3.id}
    for item in items:
        assert search_id_min <= item["id"] <= search_id_max

async def test_search_combined_title_and_price_min(client: AsyncClient):
    """
    Test searching by a combination of title and minimum price.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Widget Blue", description="A blue widget", price=15.0)
    await product1.save()
    product2 = Product(title="Widget Red", description="A red widget", price=25.0)
    await product2.save()
    product3 = Product(title="Gadget Blue", description="A blue gadget", price=35.0)
    await product3.save()
    product4 = Product(title="Widget Green", description="A green widget", price=5.0)
    await product4.save()


    response = await client.post(
        f"{endpoint}/search",
        json={"title": "Widget", "price_min": 20.0},
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 1
    assert items[0]["title"] == "Widget Red"
    assert items[0]["price"] == 25.0

async def test_search_combined_all_params_match(client: AsyncClient):
    """
    Test searching by a combination of all parameters leading to a specific item.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Specific Item Alpha", description="Unique description one", price=99.99)
    await product1.save()
    await product1.refresh()
    product2 = Product(title="Specific Item Beta", description="Unique description two", price=149.50)
    await product2.save()
    await product2.refresh()
    product3 = Product(title="Generic Item Gamma", description="Common description three", price=50.0)
    await product3.save()
    await product3.refresh()

    # Target product2
    response = await client.post(
        f"{endpoint}/search",
        json={
            "id_min": product2.id,
            "id_max": product2.id,
            "title": "Beta",
            "description": "two",
            "price_min": 140.0,
            "price_max": 150.0,
            },
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 1
    assert items[0]["id"] == product2.id
    assert items[0]["title"] == "Specific Item Beta"
    assert items[0]["price"] == 149.50


async def test_search_combined_params_no_match(client: AsyncClient):
    """
    Test searching by a combination of parameters that results in no matches.
    """
    await Product.delete_all(force=True)
    product1 = Product(title="Apple iPhone", description="Latest model", price=999.0)
    await product1.save()
    product2 = Product(title="Samsung Galaxy", description="Android flagship", price=899.0)
    await product2.save()

    response = await client.post(
        f"{endpoint}/search",
        json={
            "title": "Apple",    # Matches product1
            "price_max": 500.0,  # Excludes product1
            },
    )

    assert response.status_code == status_codes.HTTP_200_OK
    items = response.json()
    assert len(items) == 0

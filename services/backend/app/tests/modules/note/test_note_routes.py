import pytest
from datetime import datetime

from httpx import AsyncClient
from litestar import status_codes

from src.base.versions import ApiVersion
from src.modules.note.models import Note


Model = Note


@pytest.mark.asyncio(loop_scope='session')
async def test_create_one(client: AsyncClient):
    response = await client.post(
        f"{ApiVersion.V1}/{Model._meta.tablename}",
        json={
            'title': 'test_create_note_title',
            'body': 'test_create_note_body',
            'rating': 5,
        }
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    item = response.json()
    assert isinstance(item['id'], int)
    assert item['title'] == 'test_create_note_title'
    assert item['body'] == 'test_create_note_body'
    assert item['rating'] == 5
    assert datetime.fromisoformat(item['created_at'])
    assert datetime.fromisoformat(item['updated_at'])

    db_item = await Note.read_one(item['id'])
    assert db_item.title == 'test_create_note_title'
    assert db_item.body == 'test_create_note_body'
    assert db_item.rating == 5


@pytest.mark.asyncio(loop_scope='session')
async def test_create_one_raises_error_for_duplicate(client: AsyncClient):
    item = Note(
        title='test_create_one_raises_error_for_duplicate_title',
        body='test_create_one_raises_error_for_duplicate_body',
        rating=5,
    )
    await item.save()
    await item.refresh()

    response = await client.post(
        f"{ApiVersion.V1}/{Model._meta.tablename}",
        json={
            'title': 'test_create_one_raises_error_for_duplicate_title',
            'body': 'test_create_one_raises_error_for_duplicate_body',
            'rating': 5,
        }
    )
    assert response.status_code == status_codes.HTTP_409_CONFLICT
    assert response.json() == {
        "status_code": 409,
        "detail": "duplicate key value violates unique constraint \"note_title_key\"\nDETAIL:  Key (title)=(test_create_one_raises_error_for_duplicate_title) already exists."
    }


@pytest.mark.asyncio(loop_scope='session')
async def test_read_one(client: AsyncClient):
    item = Note(
        title='test_read_note_title',
        body='test_read_note_body',
        rating=5,
    )
    await item.save()
    await item.refresh()

    response = await client.get(
        f"{ApiVersion.V1}/{Model._meta.tablename}/{item.id}"
    )
    assert response.status_code == status_codes.HTTP_200_OK
    item = response.json()
    assert isinstance(item['id'], int)
    assert item['title'] == 'test_read_note_title'
    assert item['body'] == 'test_read_note_body'
    assert item['rating'] == 5
    assert datetime.fromisoformat(item['created_at'])
    assert datetime.fromisoformat(item['updated_at'])


@pytest.mark.asyncio(loop_scope='session')
async def test_update_one(client: AsyncClient):
    item = Note(
        title='test_update_note_title',
        body='test_update_note_body',
        rating=5,
    )
    await item.save()
    await item.refresh()

    response = await client.patch(
        f"{ApiVersion.V1}/{Model._meta.tablename}/{item.id}",
        json={
            'title': 'test_update_note_title_updated',
            'body': 'test_update_note_body_updated',
            'rating': 4,
        }
    )
    assert response.status_code == status_codes.HTTP_200_OK
    item = response.json()
    assert isinstance(item['id'], int)
    assert item['title'] == 'test_update_note_title_updated'
    assert item['body'] == 'test_update_note_body_updated'
    assert item['rating'] == 4
    assert datetime.fromisoformat(item['created_at'])
    assert datetime.fromisoformat(item['updated_at'])

    db_item = await Note.read_one(item['id'])
    assert db_item.title == 'test_update_note_title_updated'
    assert db_item.body == 'test_update_note_body_updated'
    assert db_item.rating == 4


@pytest.mark.asyncio(loop_scope='session')
async def test_upsert_one_create_new(client: AsyncClient):
    # Verify that the item does not exist
    assert not await Note.exists().where(
        Note.title=='test_upsert_one_create_new_title',
        Note.body=='test_upsert_one_create_new_body',
        Note.rating==5,
    )

    response = await client.put(
        f"{ApiVersion.V1}/{Model._meta.tablename}",
        json={
            'title': 'test_upsert_one_create_new_title',
            'body': 'test_upsert_one_create_new_body',
            'rating': 5,
        }
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    item = response.json()
    assert isinstance(item['id'], int)
    assert item['title'] == 'test_upsert_one_create_new_title'
    assert item['body'] == 'test_upsert_one_create_new_body'
    assert item['rating'] == 5
    assert datetime.fromisoformat(item['created_at'])
    assert datetime.fromisoformat(item['updated_at'])

    db_item = await Note.read_one(item['id'])
    assert db_item.title == 'test_upsert_one_create_new_title'
    assert db_item.body == 'test_upsert_one_create_new_body'
    assert db_item.rating == 5


@pytest.mark.asyncio(loop_scope='session')
async def test_upsert_one_update(client: AsyncClient):
    item = Note(
        title='test_upsert_one_update_title',
        body='test_upsert_one_update_body_old',
        rating=5,
    )
    await item.save()
    await item.refresh()

    response = await client.put(
        f"{ApiVersion.V1}/{Model._meta.tablename}",
        json={
            'title': 'test_upsert_one_update_title',
            'body': 'test_upsert_one_update_body_new',
            'rating': 4,
        }
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    item = response.json()
    assert isinstance(item['id'], int)
    assert item['title'] == 'test_upsert_one_update_title'
    assert item['body'] == 'test_upsert_one_update_body_new'
    assert item['rating'] == 4
    assert datetime.fromisoformat(item['created_at'])
    assert datetime.fromisoformat(item['updated_at'])

    db_item = await Note.read_one(item['id'])
    assert db_item.title == 'test_upsert_one_update_title'
    assert db_item.body == 'test_upsert_one_update_body_new'
    assert db_item.rating == 4


@pytest.mark.asyncio(loop_scope='session')
async def test_delete_one(client: AsyncClient):
    item = Note(
        title='test_delete_note_title',
        body='test_delete_note_body',
        rating=5,
    )
    await item.save()
    await item.refresh()

    response = await client.delete(
        f"{ApiVersion.V1}/{Model._meta.tablename}/{item.id}"
    )
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT
    assert not await Note.exists().where(Note.id==item.id)


@pytest.mark.asyncio(loop_scope='session')
async def test_read_all(client: AsyncClient):
    # Delete all items
    await Note.delete_all(force=True)

    # Create 2 items
    items = []
    for i in range(2):
        item = Note(
            title=f'test_read_all_note_title_{i}',
            body=f'test_read_all_note_body_{i}',
            rating=i,
        )
        await item.save()
        await item.refresh()
        items.append(item)

    response = await client.get(
        f"{ApiVersion.V1}/{Model._meta.tablename}"
    )
    assert response.status_code == status_codes.HTTP_200_OK
    items_response = response.json()
    assert len(items_response) == 2
    for i, item in enumerate(items_response):
        assert isinstance(item['id'], int)
        assert item['title'] == f'test_read_all_note_title_{i}'
        assert item['body'] == f'test_read_all_note_body_{i}'
        assert item['rating'] == i
        assert datetime.fromisoformat(item['created_at'])
        assert datetime.fromisoformat(item['updated_at'])


@pytest.mark.asyncio(loop_scope='session')
async def test_create_many(client: AsyncClient):
    # Delete all items
    await Note.delete_all(force=True)

    item1 = {
        'title': 'test_create_many_note_title_1',
        'body': 'test_create_many_note_body_1',
        'rating': 1,
    }
    item2 = {
        'title': 'test_create_many_note_title_2',
        'body': 'test_create_many_note_body_2',
        'rating': 2,
    }

    response = await client.post(
        f"{ApiVersion.V1}/{Model._meta.tablename}/many",
        json=[item1, item2]
    )

    assert response.status_code == status_codes.HTTP_201_CREATED
    items = response.json()
    assert len(items['ids']) == 2

    # Get item1 from db
    db_item1 = await Note.read_one(items['ids'][0])
    assert db_item1.title == item1['title']
    assert db_item1.body == item1['body']
    assert db_item1.rating == item1['rating']

    # Get item 2 from db
    db_item2 = await Note.read_one(items['ids'][1])
    assert db_item2.title == item2['title']
    assert db_item2.body == item2['body']
    assert db_item2.rating == item2['rating']


@pytest.mark.asyncio(loop_scope='session')
async def test_create_many_raises_error_for_duplicate(client: AsyncClient):
    # Delete all items
    await Note.delete_all(force=True)

    item1 = {
        'title': 'test_create_many_raises_error_for_duplicate_note_title_1',
        'body': 'test_create_many_raises_error_for_duplicate_note_body_1',
        'rating': 1,
    }

    # Create item1 directly
    db_item1 = Note(**item1)
    await db_item1.save()

    item2 = {
        'title': 'test_create_many_raises_error_for_duplicate_note_title_2',
        'body': 'test_create_many_raises_error_for_duplicate_note_body_2',
        'rating': 2,
    }

    response = await client.post(
        f"{ApiVersion.V1}/{Model._meta.tablename}/many",
        json=[item1, item2]
    )
    assert response.status_code == status_codes.HTTP_409_CONFLICT
    assert response.json() == {
        "status_code": 409,
        "detail": "duplicate key value violates unique constraint \"note_title_key\"\nDETAIL:  Key (title)=(test_create_many_raises_error_for_duplicate_note_title_1) already exists."
    }


@pytest.mark.asyncio(loop_scope='session')
async def test_upsert_many_create_new(client: AsyncClient):
    # Delete all items
    await Note.delete_all(force=True)

    item1 = {
        'title': 'test_upsert_many_create_new_note_title_1',
        'body': 'test_upsert_many_create_new_note_body_1',
        'rating': 1,
    }
    item2 = {
        'title': 'test_upsert_many_create_new_note_title_2',
        'body': 'test_upsert_many_create_new_note_body_2',
        'rating': 2,
    }

    response = await client.put(
        f"{ApiVersion.V1}/{Model._meta.tablename}/many",
        json=[item1, item2]
    )

    assert response.status_code == status_codes.HTTP_201_CREATED
    items = response.json()
    assert len(items['ids']) == 2

    # Get item1 from db
    db_item1 = await Note.read_one(items['ids'][0])
    assert db_item1.title == item1['title']
    assert db_item1.body == item1['body']
    assert db_item1.rating == item1['rating']

    # Get item 2 from db
    db_item2 = await Note.read_one(items['ids'][1])
    assert db_item2.title == item2['title']
    assert db_item2.body == item2['body']
    assert db_item2.rating == item2['rating']


@pytest.mark.asyncio(loop_scope='session')
async def test_upsert_many_create_one_update_one(client: AsyncClient):
    # Delete all items
    await Note.delete_all(force=True)

    item1 = {
        'title': 'test_upsert_many_create_one_update_one_note_title_1',
        'body': 'test_upsert_many_create_one_update_one_note_body_1',
        'rating': 1,
    }
    item2 = {
        'title': 'test_upsert_many_create_one_update_one_note_title_2',
        'body': 'test_upsert_many_create_one_update_one_note_body_2',
        'rating': 2,
    }

    item1_update = {
        'title': 'test_upsert_many_create_one_update_one_note_title_1', # Same title
        'body': 'test_upsert_many_create_one_update_one_note_body_1_updated',
        'rating': 3,
    }

    # Create item1 directly
    db_item1 = Note(**item1)
    await db_item1.save()
    await db_item1.refresh()

    # Call upsert_many with item1 and item2
    response = await client.put(
        f"{ApiVersion.V1}/{Model._meta.tablename}/many",
        json=[item1_update, item2]
    )

    assert response.status_code == status_codes.HTTP_201_CREATED
    items = response.json()
    assert len(items['ids']) == 2

    # Get item1 from db
    db_item1 = await Note.read_one(items['ids'][0])
    assert db_item1.title == item1_update['title']
    assert db_item1.body == item1_update['body']
    assert db_item1.rating == item1_update['rating']

    # Get item 2 from db
    db_item2 = await Note.read_one(items['ids'][1])
    assert db_item2.title == item2['title']
    assert db_item2.body == item2['body']
    assert db_item2.rating == item2['rating']

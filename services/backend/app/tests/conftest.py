import pytest
from litestar.testing.client.async_client import AsyncTestClient
from sqlalchemy_utils import drop_database, database_exists

from src.logging.service import logger
from src import config
from src.database.models import DatabaseBind
from src.database.service import db
from src.app import create_app
from src.lifespan import lifespan


def init_db():
    test_db_name = f"{config.DATABASE_NAME}_test"
    test_db_bind = DatabaseBind(
        host=config.DATABASE_HOST_NAME,
        name=test_db_name,
        username=config.DATABASE_HOST_USERNAME,
        password=config.DATABASE_HOST_PASSWORD,
        port=config.DATABASE_HOST_PORT,
    )
    # Drop db before tests. DB Service will create it again.
    if database_exists(test_db_bind.url_sync):
        logger.info(f"Dropping test database: {test_db_name}...")
        drop_database(test_db_bind.url_sync)

    # Can't use connection pool in tests, causes eventloop issues
    db.init(test_db_bind, use_pool=False)


@pytest.fixture(scope='session')
def app():
    init_db()
    app = create_app(lifespan=[lifespan])
    yield app


# @pytest.fixture(scope='session')
# async def login(client) -> Login:
#     return await Login.create(
#         LoginCreate(
#             email='user@test.com',
#             password='user_password',
#         )
#     )


# @pytest.fixture(scope='session')
# async def sysadmin_login(client) -> Login:
#     login = await Login.create(
#         LoginCreate(
#             email='sysadmin@test.com',
#             password='sysadmin',
#         )
#     )
#     login.verified = True
#     await login.promote_to_sysadmin()
#     return login


@pytest.fixture(scope='session')
async def client(app):
    async with AsyncTestClient(app) as c:
        yield c

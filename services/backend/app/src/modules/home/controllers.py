from litestar import get, status_codes, Request

from src.base.versions import ApiVersion
from src.base.controllers.base import AppController


class HomeController(AppController):
    path = f"{ApiVersion.NONE}/home"

    @get(
        '/',
        status_code=status_codes.HTTP_200_OK,
        summary='Home: Read',
        description='Returns 200 if service is up and running',
        tags=['Home'],
        exclude_from_auth=True,
    )
    async def index(self, request: Request) -> dict:
        """
        Home

        Returns:
            dict: {
                'message': 'Hello boils and ghouls'
            }
        """
        request.logger.warning("inside a request")
        return {
            'message': 'Hello boils and ghouls'
        }

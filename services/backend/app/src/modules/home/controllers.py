from litestar import get, status_codes, Request

from src.versions import ApiVersion
from src.controllers.base import AppController
from src.modules.home.dtos import HomeReadDTO


class HomeController(AppController):
    path = f"{ApiVersion.NONE}/home"

    @get(
        "/",
        status_code=status_codes.HTTP_200_OK,
        summary="Home: Read",
        description="Returns 200 if service is up and running",
        tags=["Home"],
        exclude_from_auth=True,
    )
    async def index(self, request: Request) -> HomeReadDTO:
        """
        Home

        Returns:
            dict: {
                'message': 'Hello boils and ghouls'
            }
        """
        return HomeReadDTO()

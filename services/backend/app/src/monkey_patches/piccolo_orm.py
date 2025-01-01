import typing as t

from piccolo.custom_types import QueryResponseType
from piccolo.query.base import Query


async def run_mp(
    self,
    node: t.Optional[str] = None,
    in_pool: bool = True,
) -> QueryResponseType:
    return await self._run(node=node, in_pool=in_pool)


def patch():
    Query.run = run_mp

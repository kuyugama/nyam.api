from sqlalchemy import Select, select, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models import BasePage, TextPage, ImagePage


def page_filters(query: Select, chapter_id: int):
    return query.filter(BasePage.chapter_id == chapter_id)


def page_options(query: Select, model: type[TextPage | ImagePage]):
    if model is ImagePage:
        query = query.options(
            joinedload(
                ImagePage.image
            )
        )
    return query


async def list_pages(
    session: AsyncSession,
    chapter_id: int,
    offset: int,
    limit: int,
    model: type[TextPage | ImagePage],
) -> ScalarResult[TextPage | ImagePage]:
    return await session.scalars(
        page_filters(page_options(select(model).offset(offset).limit(limit), model), chapter_id)
    )

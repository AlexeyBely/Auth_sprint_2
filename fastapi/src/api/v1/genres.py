from http import HTTPStatus

from api.v1.response_models import (GenreListResponse, GenreResponse,
                                    GenreSortSelection, PaginatedParams)
from core import messages
from interfaces.composition_services import get_genre_service
from services.genre import GenreService

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get('/{genre_id}',
            response_model=GenreResponse,
            summary='Информация по жанру',
            description='Поиск жанра по uuid',
            response_description='Полная информация по жанру',
            tags=['Поиск по uuid']
            )
async def genre_details(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service)
) -> GenreResponse:
    """
    Show a genre by its UUID.

    :param genre_id: genre UUID.
    :param genre_service: the request handling service.
    :return: the genre.
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.GENRE_NOT_FOUND)
    return GenreResponse(id=genre.id, name=genre.name, description=genre.description)


@router.get('/',
            response_model=GenreListResponse,
            summary='Поиск жанров с сортировкой',
            description='Поиск с сортировкой по алфавиту',
            response_description='Название и описание жанра',
            )
async def genre_list(
    genre_service: GenreService = Depends(get_genre_service),
    paginated_params: PaginatedParams = Depends(PaginatedParams),
    sort: GenreSortSelection | None = None
) -> GenreListResponse:
    """
    Show the genre list. The response will be paginated and can be sorted.

    :param genre_service: the request handling service.
    :param paginated_params: parameters to paginate:
        size - the records number per page,
        page - the page number.
    :param sort: a comma-separated list of <field>:<direction> pairs. Note: not all field types can be sorted.
    :return: the genre list.
    """
    if sort is not None:
        sort = sort.value
    genres = await genre_service.get_list(paginated_params.size, paginated_params.page, sort)
    return genres

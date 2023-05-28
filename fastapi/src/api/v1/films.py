from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.v1.auth import TokenData, authenticate
from api.v1.access_rules import is_privilege_user
from api.v1.response_models import (FilmResponse, FilmsListResponse,
                                    FilmSortSelection, PaginatedParams)
from core import messages
from interfaces.composition_services import get_film_service
from services.film import FilmService


router = APIRouter()


@router.get('/{film_id}',
            response_model=FilmResponse,
            summary='Информация по кинопроизведению',
            description='Поиск кинопроизведения по uuid',
            response_description='Полная информация по кинопроизведению',
            tags=['Поиск по uuid']
            )
async def film_details(
    film_id: str,
    film_service: FilmService = Depends(get_film_service),
    #token_data: TokenData = Depends(authenticate)
) -> FilmResponse:
    """Show a film by its UUID."""
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.FILM_NOT_FOUND)
    return film


@router.get('/search/',
            response_model=FilmsListResponse,
            summary='Поиск по названию кинопроизведения',
            description='Полнотекстовый поиск по названию кинопроизведения',
            response_description='Название и рейтинг кинопроизведения',
            tags=['Полнотекстовый поиск']
            )
async def film_search(
    query: str = Query('title', description='название кинопроизведения'),
    paginated_params: PaginatedParams = Depends(PaginatedParams),
    sort: FilmSortSelection = FilmSortSelection.rating_desc,
    film_service: FilmService = Depends(get_film_service),
    #token_data: TokenData = Depends(authenticate)
) -> FilmsListResponse:
    """Show the short film list. Query by movie title."""
    films = await film_service.search(query=query, page=paginated_params.page, size=paginated_params.size, sort=sort)
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.FILM_NOT_FOUND)
    return films


@router.get('/',
            response_model=FilmsListResponse,
            summary='Поиск с сортировкой',
            description='Поиск с сортировкой по рейтингу и выбором жанра (опционально)',
            response_description='Название и рейтинг кинопроизведения',
            )
async def film_list(
    sort: FilmSortSelection = FilmSortSelection.rating_desc,
    filter: str = Query(None, description='uuid жанра'),
    paginated_params: PaginatedParams = Depends(PaginatedParams),
    film_service: FilmService = Depends(get_film_service),
    #privilege_user = Depends(is_privilege_user)
) -> FilmsListResponse:
    """Show the short film list. Filter by uuid genre."""

    # If user is not privilege returns only 1 page with 3 films
    privilege_user = True
    page = paginated_params.page if privilege_user else 1
    size = paginated_params.size if privilege_user else 3

    films = await film_service.get_list(sort, filter, page, size)
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.FILM_NOT_FOUND)
    return films

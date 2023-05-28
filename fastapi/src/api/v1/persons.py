from http import HTTPStatus

from api.v1.response_models import (FilmShortListResponse, FilmSortSelection,
                                    PaginatedParams, PersonListResponse,
                                    PersonResponse, PersonSortSelection)
from core import messages
from interfaces.composition_services import get_person_service
from services.person import PersonService

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get('/',
            response_model=PersonListResponse,
            summary='Поиск персон с сортировкой',
            description='Поиск с сортировкой по алфавиту',
            response_description='Полное имя персоны',
            )
async def person_list(
    paginated_params: PaginatedParams = Depends(PaginatedParams),
    sort: PersonSortSelection | None = None,
    person_service: PersonService = Depends(get_person_service)
) -> PersonListResponse:
    """
    Show the person list. The response will be paginated and can be sorted.

    :param paginated_params: parameters to paginate:
        size - the records number per page,
        page - the page number.
    :param sort: a comma-separated list of <field>:<direction> pairs. Note: not all field types can be sorted.
    :param person_service: the request handling service.
    :return: the person list.
    """
    if sort is not None:
        sort = sort.value
    response = await person_service.get_list(paginated_params.size, paginated_params.page, sort)
    return response


@router.get('/search',
            response_model=PersonListResponse,
            summary='Поиск по имени персоны',
            description='Полнотекстовый поиск по имени персоны',
            response_description='Полное имя персоны',
            tags=['Полнотекстовый поиск']
            )
async def person_search(
    query: str,
    paginated_params: PaginatedParams = Depends(PaginatedParams),
    person_service: PersonService = Depends(get_person_service)
) -> PersonListResponse:
    """
    Search for persons by name.

    :param query: the search query
    :param paginated_params: parameters to paginate:
        size - the records number per page,
        page - the page number.
    :param person_service: the request handling service.
    :return: the persons found.
    """
    response = await person_service.search(query, paginated_params.size, paginated_params.page)
    return response


@router.get('/{person_id}',
            response_model=PersonResponse,
            summary='Информация по персоне',
            description='Поиск персоны по uuid',
            response_description='Полная информация по персоне',
            tags=['Поиск по uuid']
            )
async def person_details(
        person_id: str,
        person_service: PersonService = Depends(get_person_service)
) -> PersonResponse:
    """
    Get person by its UUID.

    :param person_id: the person UUID.
    :param person_service: the request handling service.
    :return: the person.
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.PERSON_NOT_FOUND)
    return person


@router.get('/{person_id}/film',
            response_model=FilmShortListResponse,
            summary='Информация о фильмах по персоне',
            description='Поиск фильмов в которых участвовала uuid персона',
            response_description='Название и рейтинг кинопроизведения',
            )
async def person_films(person_id: str,
                       paginated_params: PaginatedParams = Depends(PaginatedParams),
                       sort: FilmSortSelection | None = None,
                       person_service: PersonService = Depends(get_person_service)
                       ) -> FilmShortListResponse:
    """
    Returns films in which the person with the person_id UUID participated.

    :param person_id: the person UUID.
    :param paginated_params: parameters to paginate:
        size - the records number per page,
        page - the page number.
    :param sort: a comma-separated list of <field>:<direction> pairs. Note: not all field types can be sorted.
    :param person_service: the request handling service.
    :return: the films found.
    """
    if sort is not None:
        sort = sort.value
    films = await person_service.get_person_films(person_id, paginated_params.size, paginated_params.page, sort)
    if films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.PERSON_NOT_FOUND)
    return films

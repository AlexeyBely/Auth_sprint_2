from math import ceil

from core import messages


def compute_page_numbers(current_page: int, records_per_page: int, total_records: int, start_from_zero: bool = False,
                         raise_if_current_out_of_range: bool = False) -> dict[str: int]:
    """
    Compute the first, the last, the previous and the next page numbers for pagination.

    :param current_page: the current page number
    :param records_per_page: the number of records per page
    :param total_records: the total records number
    :param start_from_zero: is the first page number equals 0
    :param raise_if_current_out_of_range: If it is True and the current page number is less than first (or more than
        last) the exception will be raised. Otherwise the current page number will be set as first (or last).
    :return: the dictionary with the next keys:
        first - the first page of data,
        last - the last page of data,
        prev - the previous page of data,
        next - the next page of data
    """
    if records_per_page <= 0:
        raise ValueError(messages.SHOULD_BE_GREATER_THAN.format('records_per_page', 0))
    if total_records == 0:
        return {'prev': None, 'next': None, 'first': None, 'last': None}
    if total_records < 0:
        raise ValueError(messages.SHOULD_BE_GREATER_THAN.format('total_records', 0))
    first_page = 0 if start_from_zero else 1
    last_page = ceil(total_records / records_per_page)
    if first_page == 0:
        last_page -= 1
    if current_page < first_page:
        if raise_if_current_out_of_range:
            raise ValueError(messages.SHOULD_BE_AT_LEAST.format('current_page', first_page))
        else:
            current_page = first_page
    if current_page > last_page:
        if raise_if_current_out_of_range:
            raise ValueError(messages.SHOULD_BE_AT_MOST.format('current_page', last_page))
        else:
            current_page = last_page
    prev_page = current_page - 1 if current_page > first_page else None
    next_page = current_page + 1 if current_page < last_page else None
    return {'prev': prev_page, 'next': next_page, 'first': first_page, 'last': last_page}

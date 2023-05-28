from functools import wraps
from typing import Type

from pydantic import BaseModel
from storage.base_storage import BaseStorage
from storage.redis_storage import get_redis_storage


def cache_es(Model: Type[BaseModel]):
    """
    Кеширование ответов от Elasticsearch запрошенных с одинаковыми параметрами.

    Model - модель pydantic, используется для валидирования данних из redis.
    Функция декоратор оборачивает функции возвращающие типы BaseModel и
    List[BaseModel]
    данные в redis хранятся по ключу Model.__name__/args[]&(kwargs[])
    """
    def func_wrapper(func):
        # в качестве хранилища выбран redis
        storage: BaseStorage = get_redis_storage()

        @wraps(func)
        async def inner(*args, **kwargs):
            arg_count = len(args)
            qry = f'{Model.__name__}/'
            for i in range(1, arg_count):
                qry += f'{args[i]}&'
            for k in kwargs:
                qry += f'{kwargs[k]}&'
            # Читаем данние из кеша
            data_from_redis = await storage.retrieve_data(qry)
            if not data_from_redis:
                # Если данных нет в кеше, то вызываем функцию
                data_es = await func(*args, **kwargs)
                if data_es is None:
                    # Если он отсутствует в ES, значит, фильма нет в БД
                    return None
                # Сохраняем фильм в кеш
                if type(data_es) is list:
                    data_for_redis = [data.json() for data in data_es]
                else:
                    data_for_redis = data_es.json()
                await storage.save_data(qry, data_for_redis)
                return data_es
            if type(data_from_redis) is list:
                model_data = [Model.parse_raw(data) for data in data_from_redis]
            else:
                model_data = Model.parse_raw(data_from_redis)
            return model_data
        return inner
    return func_wrapper

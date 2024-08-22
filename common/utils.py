import logging
from django.core.cache import cache
from django.conf import settings

from common.exceptions import ExpiredApiCacheData

logger = logging.getLogger()


class CacheDataManager:

    @staticmethod
    def _get_cache_key(data_type, unique_key):
        return data_type + '_' + unique_key

    @staticmethod
    def set_cache(data_type, unique_key, data):
        cache_key = CacheDataManager._get_cache_key(data_type, unique_key)
        cache.set(cache_key, data, settings.CACHE_TIMEOUT)

    @staticmethod
    def get_cache(data_type, unique_key):
        cache_key = CacheDataManager._get_cache_key(data_type, unique_key)
        cached_data = cache.get(cache_key)
        if cached_data is None:
            # Todo: 캐시 데이터가 없을 경우 err logging
            raise ExpiredApiCacheData

        return cached_data

    @staticmethod
    def delete_cache(data_type, unique_key):
        cache_key = CacheDataManager._get_cache_key(data_type, unique_key)
        cache.delete(cache_key)


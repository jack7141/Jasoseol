from rest_framework import status
from .base import CustomAPIException




class ExpiredApiCacheData(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'E01'
    default_detail = 'API Cache 데이터가 만료되어 존재하지 않습니다.'


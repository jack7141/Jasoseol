# Chating Server
Chating 서버(Chating Server)

## Tech
* [Django] - Python 웹 애플리케이션 프레임워크
* [Django Rest Framework] - RESTFul Web API
* [Django Rest Swagger] - [Django Rest Framework]을 위한 문서 생성기

## System Requirements
[python] 3.10 사용

## API Document

API에 대한 문서는 swagger를 통해 자동생성되도록 되어있습니다.
각 API는 `버전`이 존재하며 버전의 룰은 `"v{version}"`으로 적용됩니다.
> 예) v1, v2, v3 ...

Swagger API 문서 주소는 `/api/v{version}/swagger`입니다.
> 예) /api/v1/swagger


실행
> api_backend 폴더 > secrets.json에서 DB 정보를 입력합니다.
> 
> EX
> 
> "NAME": "jasoseol",
> 
> "USER": "#ROOT",
> 
> "PASSWORD": "password",
> 
> "HOST": "#HOST",
> 
> 
> frontend와 함께 실행이 되므로 localhost:80 에서 실행이 됩니다.
> 
> ASGI를 활용하여 비동기 통신을 하려 하였으며, redis를 활용하여 channel layer를 구성하였고, DB 과부하를 방지하고자 최근 100건의 
> 
> 메세지는 redis cache를 활용하여 저장하고 나머지 데이터는 DB에서 조회하는 구조로 처리하였습니다.
> 
> 대용량에 따라서는 샤딩과 celery 비동기 task를 활용하여 처리할 수 있을것같으나, 간단하게 구성하기 위해서 기술 스택만 적었습니다.

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [fount logo]: <https://fount.co/wp-content/uploads/2017/07/fount-ci@2x.png>
   [python]: <https://www.python.org/>
   [Django]: <https://www.djangoproject.com/>
   [Django Rest Framework]: <http://www.django-rest-framework.org/>
   [Django Rest Swagger]: <https://django-rest-swagger.readthedocs.io>

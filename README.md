# Music Manager API Server
Music Manage 서버(Music Manager Server)

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

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [fount logo]: <https://fount.co/wp-content/uploads/2017/07/fount-ci@2x.png>
   [python]: <https://www.python.org/>
   [Django]: <https://www.djangoproject.com/>
   [Django Rest Framework]: <http://www.django-rest-framework.org/>
   [Django Rest Swagger]: <https://django-rest-swagger.readthedocs.io>

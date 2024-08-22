from django.http.request import QueryDict
from rest_framework.response import Response


class MappingViewSetMixin(object):
    serializer_action_map = {}
    permission_classes_map = {}

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.permission_classes_map.get(self.action, None):
            permission_classes = self.permission_classes_map[self.action]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.serializer_action_map.get(self.action, None):
            return self.serializer_action_map[self.action]
        return self.serializer_class


class RetrieveModelMixin(object):
    def retrieve(self, request, *args, **kwargs):
        input_params = self._set_input_params(request, **kwargs)
        serializer = self.get_serializer(data=input_params)
        serializer.is_valid(raise_exception=True)
        response = Response(data=serializer.data)
        if request.accepted_media_type.find('csv') > 0:
            response['Content-Disposition'] = f'attachment; filename="{self.action}.csv"'
        return response

    def _set_input_params(self, request, **kwargs):
        input_params = kwargs
        input_params.update(request.data)
        input_params.update(self._query_dict_to_dict(request.query_params))
        return input_params

    def _query_dict_to_dict(self, data):
        if type(data) == QueryDict:
            return data.dict()
        return data


class CreateModelMixin(object):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)


class UpdateModelMixin(object):
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)


class DeleteModelMixin(object):
    def destroy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)

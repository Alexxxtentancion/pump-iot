from django.http.response import HttpResponseBase
from rest_framework.response import Response


class ResponseSerializerMixin:
    SERIALIZER_FIELD_NAME = 'serializer'

    def finalize_response(self, request, response, *args, **kwargs):
        if not isinstance(response, HttpResponseBase):
            serializer = getattr(self, self.SERIALIZER_FIELD_NAME, None)
            if serializer:
                response = Response(serializer().data)
            else:
                response = Response(response)

        if response.exception:
            response.data = {'reason': response.data, 'status': 'error'}
        else:
            response.data = {'data': response.data, 'status': 'ok'}
        return super().finalize_response(request, response, *args, **kwargs)


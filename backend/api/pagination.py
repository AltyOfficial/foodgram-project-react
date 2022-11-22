from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ResponseOnlyPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(data)


class RecipesPagination(PageNumberPagination):
    page_size_query_param = 'limit'
